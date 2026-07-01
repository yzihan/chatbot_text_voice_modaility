from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import datetime, timezone
import io
import os
from pathlib import Path
import threading
import time
import uuid
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, Header, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse

from admin_repository import record_backend_step
from admin_routes import router as admin_router
from conversation_engine.engine import ConversationEngine
from conversation_engine.logger import logger
from conversation_engine.openai_api import send_audio
from conversation_engine.question_list.codes.question_list import create_quetion_nodes
from conversation_engine.question_list.codes.question_sequence import get_question_indices
from database_sql import init_database
from sql_models import utc_now
from sql_repository import (
    client_message_exists,
    complete_audio_transcription,
    conversation_belongs_to_participant,
    create_conversation,
    export_database_zip,
    get_or_create_participant,
    get_participant,
    list_conversation_metadata,
    parse_client_timestamp,
    record_audio_upload,
    record_conversation_turn,
    record_failed_user_input,
    record_interaction_event,
    record_pending_user_input,
)

APP_DIR = Path(__file__).resolve().parent
load_dotenv(APP_DIR / ".env")



CACHE_TIME = 60 * 60  # 1 hour
DATABASE_DIR = APP_DIR / "database"
CHAT_DIR = DATABASE_DIR / "chats"

CHAT_DIR.mkdir(parents=True, exist_ok=True)


def error_response(status_code: int, message: str) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"error": message})


def chat_save_path(participant_id: str, interview_id: str) -> Path:
    return CHAT_DIR / participant_id / interview_id


def get_cors_allowed_origins() -> list[str]:
    origins = os.getenv("CORS_ALLOWED_ORIGINS", "")
    return [origin.strip() for origin in origins.split(",") if origin.strip()]


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_database()
    thread = threading.Thread(target=cleanup_engines, daemon=True)
    thread.start()
    yield


app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(admin_router)


# engines
engines = {}
engines_last_updated_time = {}


@app.get("/")
def read_root():
    return {"message": "Hello Nova!"}

@app.post("/chatbot/user")
async def search_or_create(request: Request):
    try:
        body = await request.json()
        participant_id = body.get("participantID")

        if not participant_id:
            logger.error("participantID is required")
            return error_response(400, "participantID is required")

        participant = get_or_create_participant(participant_id)
        return participant.id

    except Exception as e:
        logger.error(f"[/chatbot/user]: {str(e)}")
        return error_response(500, str(e))


@app.post("/chatbot/new_conversation")
async def new_conversation(request: Request):
    try:
        body = await request.json()
        participant_id = body.get("participantID")
        group = body.get("group")
        selection_reason = body.get("selectionReason", "")
        modality_selected_client_at = body.get("modalitySelectedClientAt")
        selection_reason_client_at = body.get("selectionReasonClientAt")
        source = body.get("source")

        if not participant_id:
            return error_response(400, "participantID is required")
        
        if not group:
            return error_response(400, "group is required")

        if source not in {"selection", "voice", "keyboard"}:
            return error_response(400, "source must be selection, voice, or keyboard")

        if source == "selection" and not selection_reason.strip():
            return error_response(400, "selectionReason is required")

        if source == "selection" and (
            not modality_selected_client_at or not selection_reason_client_at
        ):
            return error_response(
                400,
                "Selection mode and reason timestamps are required",
            )

        try:
            parse_client_timestamp(modality_selected_client_at)
            parse_client_timestamp(selection_reason_client_at)
        except (TypeError, ValueError):
            return error_response(400, "Selection timestamps must be valid ISO-8601 timestamps")
        

        participant = get_participant(participant_id)
        if not participant:
            return error_response(400, "User data is lost. Please re-register.")
        user_index = participant.user_index


        interview_id = str(uuid.uuid4())
        # TODO: this is hard coded for now, need to be dynamic based on different interview types in the future.
        question_indices = get_question_indices("HEX")

        engine = ConversationEngine(
            session_id=interview_id,
            user_index=user_index,
            group=group,
            source=source,
            selection_reason=selection_reason,
            question_indices=question_indices,
            user_info={"user_name": participant_id, "uid": participant_id},
            root_node=create_quetion_nodes(question_indices),
            save_path=str(chat_save_path(participant_id, interview_id)),
        )

        engines[interview_id] = engine
        engines_last_updated_time[interview_id] = time.time()

        logger.debug(f"New Conversation Started: {interview_id}")
        logger.debug(f"Current Activate conversations: {engines_last_updated_time}")

        data = engine.init_conversation()

        if data.get("status") == "success":
            create_conversation(
                conversation_id=interview_id,
                participant_key=participant_id,
                modality_group=group,
                source_system=source,
                selection_reason=selection_reason,
                modality_selected_client_at=modality_selected_client_at,
                selection_reason_client_at=selection_reason_client_at,
                question_code=engine.question_code,
                question_sequence=question_indices,
                initial_messages=data["messages_to_returned"],
            )
            engine.save_conversation_state()
            return {
                "_id": interview_id,
                "question_data": data["messages_to_returned"],
                "is_ending": data["is_ending"]
            }
        else:
            logger.error(f"[/chatbot/new_conversation]: Some error happened: {data.get('error', 'Unknown error')}")
            return error_response(500, f"Some error happened: {data.get('error', 'Unknown error')}")

    except Exception as e:
        logger.error(f"{str(e)}")
        return error_response(500, str(e))


@app.post("/chatbot/voice-chat")
async def voice_recognition(
    uid: str = Form(...),
    participantID: str = Form(...),
    interviewID: str = Form(...),
    audio: UploadFile = File(...)
):
    upload_started_at = utc_now()
    content = b""
    webm_path = None
    recording = None
    try:
        if not conversation_belongs_to_participant(interviewID, participantID):
            return error_response(404, "Conversation not found for participant")

        unique_id = str(uuid.uuid4())
        save_dir = chat_save_path(participantID, interviewID)
        save_dir.mkdir(parents=True, exist_ok=True)

        webm_path = save_dir / f"{unique_id}.webm"

        with webm_path.open("wb") as buffer:
            content = await audio.read()
            buffer.write(content)

        recording = record_audio_upload(
            conversation_id=interviewID,
            participant_key=participantID,
            file_path=str(webm_path),
            original_filename=audio.filename,
            mime_type=audio.content_type,
            content=content,
            upload_started_at=upload_started_at,
            uploaded_at=utc_now(),
        )

        with webm_path.open("rb") as f:
            transcript = send_audio(f)

        recording = complete_audio_transcription(recording.id, transcript)

        return JSONResponse(content={
            "transcript": transcript,
            "message": "Audio saved and transcribed successfully!",
            "file_path": str(webm_path),
            "audio_recording_id": recording.id,
            "transcribed_at": recording.transcribed_at.isoformat(),
        })

    except Exception as e:
        if recording is None and webm_path is not None and content:
            try:
                record_audio_upload(
                    conversation_id=interviewID,
                    participant_key=participantID,
                    file_path=str(webm_path),
                    original_filename=audio.filename,
                    mime_type=audio.content_type,
                    content=content,
                    upload_started_at=upload_started_at,
                    uploaded_at=utc_now(),
                )
            except Exception as record_error:
                logger.error(f"Failed to record unsuccessful audio upload: {record_error}")
        logger.error(f"[/chatbot/voice-chat]: {str(e)}")
        return error_response(500, f"Error for voice recognition: {str(e)}")


@app.post("/chatbot/chat")
async def continue_conversation(request: Request):
    pending_message = None
    interviewID = None
    client_message_id = None
    participant_id = None
    server_message_id = None
    try:
        body = await request.json()
        server_received_at = datetime.now(timezone.utc).isoformat()

        interviewID = body.get("interviewID")
        user_resp = body.get("user_resp")
        audioFilepPath = body.get("audioFilepPath")
        audio_recording_ids = body.get("audio_recording_ids") or []
        audio_file_paths = body.get("audio_file_paths") or ([audioFilepPath] if audioFilepPath else [])
        client_message_id = body.get("client_message_id") or str(uuid.uuid4())
        client_created_at = body.get("client_created_at")
        input_method = body.get("input_method")
        participant_id = body.get("participantID")
        record_backend_step(
            "incoming_request",
            "received",
            conversation_id=interviewID,
            client_message_id=client_message_id,
            participant_key=participant_id,
            metadata={
                "has_audio": bool(audioFilepPath or audio_recording_ids or audio_file_paths),
                "input_method": input_method,
            },
        )
        

        if not interviewID or user_resp is None or not str(user_resp).strip() or not participant_id:
            record_backend_step(
                "request_validation",
                "failed",
                conversation_id=interviewID,
                client_message_id=client_message_id,
                participant_key=participant_id,
                detail="Missing interviewID, participantID, or user_resp",
            )
            return error_response(400, "Missing 'interviewID', 'participantID', or 'user_resp'")

        try:
            parse_client_timestamp(client_created_at)
        except (TypeError, ValueError):
            record_backend_step(
                "request_validation",
                "failed",
                conversation_id=interviewID,
                client_message_id=client_message_id,
                participant_key=participant_id,
                detail="client_created_at must be a valid ISO-8601 timestamp",
            )
            return error_response(400, "client_created_at must be a valid ISO-8601 timestamp")

        if not conversation_belongs_to_participant(interviewID, participant_id):
            record_backend_step(
                "request_validation",
                "failed",
                conversation_id=interviewID,
                client_message_id=client_message_id,
                participant_key=participant_id,
                detail="Conversation not found for participant",
            )
            return error_response(404, "Conversation not found for participant")

        if client_message_exists(interviewID, client_message_id):
            record_backend_step(
                "request_validation",
                "failed",
                conversation_id=interviewID,
                client_message_id=client_message_id,
                participant_key=participant_id,
                detail="Duplicate client_message_id",
            )
            return error_response(409, "This message was already recorded")

        if interviewID not in engines:
            logger.debug(f"Conversation Expired: {interviewID}")
            record_backend_step(
                "engine_lookup",
                "failed",
                conversation_id=interviewID,
                client_message_id=client_message_id,
                participant_key=participant_id,
                detail="Conversation engine expired",
            )
            return error_response(404, "Your session expired! Please go back to home page and restart again!")

        engine = engines[interviewID]
        input_method = input_method or engine.group
        response_metadata = {
            **getattr(engine.current_node, "info", {}),
            "response_to_node_id": engine.current_node.id,
            "response_started_client_at": body.get("response_started_client_at"),
            "response_time_ms": body.get("response_time_ms"),
        }
        server_message_id = str(uuid.uuid4())
        pending_message = {
            "id": server_message_id,
            "conversation_id": interviewID,
            "role": "user",
            "content": user_resp,
            "raw_user_input": user_resp,
            "audio_file_path": audioFilepPath,
            "audio_file_paths": audio_file_paths,
            "audio_recording_ids": audio_recording_ids,
            "client_message_id": client_message_id,
            "client_created_at": client_created_at,
            "input_method": input_method,
            "created_at": server_received_at,
            "info": response_metadata,
        }
        record_pending_user_input(interviewID, pending_message)
        record_backend_step(
            "pending_message_saved",
            "completed",
            conversation_id=interviewID,
            message_id=server_message_id,
            client_message_id=client_message_id,
            participant_key=participant_id,
        )
        engines_last_updated_time[interviewID] = time.time()

        logger.debug(f"Chat Conversation: {interviewID}")
        logger.debug(f"Current Activate conversations: {engines_last_updated_time}")

        # Assuming this method is async
        record_backend_step(
            "backend_processing",
            "started",
            conversation_id=interviewID,
            message_id=server_message_id,
            client_message_id=client_message_id,
            participant_key=participant_id,
            metadata={"node_id": getattr(engine.current_node, "id", None)},
        )
        data = await engine.process_user_response(
            user_resp,
            audioFilepPath,
            audio_recording_ids=audio_recording_ids,
            audio_file_paths=audio_file_paths,
            server_message_id=server_message_id,
            client_message_id=client_message_id,
            client_created_at=client_created_at,
            input_method=input_method,
            server_received_at=server_received_at,
            response_metadata=response_metadata,
        )

        if data.get("status") == "success":
            record_conversation_turn(
                conversation_id=interviewID,
                user_message=data["user_message"],
                assistant_messages=data["messages_to_returned"],
                questions_answered=engine._user_responses_received,
                is_ending=data["is_ending"],
            )
            record_backend_step(
                "api_model_call",
                "completed",
                conversation_id=interviewID,
                message_id=server_message_id,
                client_message_id=client_message_id,
                participant_key=participant_id,
                metadata={
                    "assistant_messages": len(data["messages_to_returned"]),
                    "is_ending": data["is_ending"],
                    "response_metadata": response_metadata,
                },
            )
            record_backend_step(
                "returned_response",
                "completed",
                conversation_id=interviewID,
                message_id=server_message_id,
                client_message_id=client_message_id,
                participant_key=participant_id,
            )
            engine.save_conversation_state()
            return {
                "question_data": data["messages_to_returned"],
                "is_ending": data["is_ending"]
            }
        else:
            failed_message = next(
                (
                    message
                    for message in reversed(engine.complete_chatting_messages)
                    if message.get("client_message_id") == client_message_id
                ),
                {
                    "role": "user",
                    "content": user_resp,
                    "raw_user_input": user_resp,
                    "audio_file_path": audioFilepPath,
                    "audio_file_paths": audio_file_paths,
                    "audio_recording_ids": audio_recording_ids,
                    "client_message_id": client_message_id,
                    "client_created_at": client_created_at,
                    "input_method": input_method,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "info": response_metadata,
                },
            )
            record_failed_user_input(interviewID, failed_message)
            record_backend_step(
                "api_model_call",
                "failed",
                conversation_id=interviewID,
                message_id=server_message_id,
                client_message_id=client_message_id,
                participant_key=participant_id,
                detail=data.get("error", "Unknown error"),
            )
            logger.error(f"[/chatbot/chat]: {data.get('error', 'Unknown error')}")
            return error_response(500, f"Some error happened for chatting: {data.get('error', 'Unknown error')}")

    except Exception as e:
        if pending_message and pending_message.get("client_message_id"):
            try:
                record_failed_user_input(pending_message["conversation_id"], pending_message)
            except Exception as record_error:
                logger.error(f"Failed to mark user input as failed: {record_error}")
        try:
            record_backend_step(
                "system_error",
                "failed",
                conversation_id=interviewID,
                message_id=server_message_id,
                client_message_id=client_message_id,
                participant_key=participant_id,
                detail=str(e),
            )
        except Exception as record_error:
            logger.error(f"Failed to record backend request log: {record_error}")
        return error_response(500, f"Error for chatting: {str(e)}")
    
@app.post("/chatbot/chat_history")
async def get_chat_history(request: Request):
    try:
        body = await request.json()
        participant_id = body.get("participantID")
        if not participant_id:
            return error_response(400, "Missing participantID in request body")

        metadatas = list_conversation_metadata(participant_id)

        return JSONResponse(
            status_code=200,
            content={"metadata": metadatas}
        )

    except Exception as e:
        logger.error(f"[/chatbot/chat_history]: {str(e)}")
        return error_response(500, f"Internal server error: {str(e)}")



@app.post("/chatbot/load_history_chat")
async def load_history_chat(request: Request):
    try:
        body = await request.json()
        participant_id = body.get("participantID")
        interview_id = body.get("interviewID")

        
        if not participant_id:
            return error_response(400, "Missing participantID in request body")

        if not interview_id:
            return error_response(400, "Missing interviewID in request body")

        if not conversation_belongs_to_participant(interview_id, participant_id):
            return error_response(404, "Conversation not found for participant")

        user_info = {"user_name": participant_id, "uid": participant_id}
        save_path = str(chat_save_path(participant_id, interview_id))

        engine = ConversationEngine.load_conversation_state(
            session_id=interview_id, 
            save_path=save_path, 
            user_info=user_info
        )

        if engine is None:
            return error_response(404, "Chat history not found")

        engines[interview_id] = engine
        engines_last_updated_time[interview_id] = time.time()

        logger.debug(f"Load Conversation: {interview_id}")
        logger.debug(f"Current Activate conversations: {engines_last_updated_time}")

        data = engine.load_history_chat()       

        return {
            "history_messages": data["messages_to_returned"],
            "is_ending": data["is_ending"],
            "group": engine.group,
            "selectionReason": engine.selection_reason,
        }

    except Exception as e:
        logger.error(f"[/chatbot/load_history_chat]: Failed loading chat history: {str(e)}")
        return error_response(500, f"Failed loading chat history: {str(e)}")


@app.post("/chatbot/interaction_event")
async def interaction_event(request: Request):
    try:
        body = await request.json()
        event_type = body.get("event_type")
        client_created_at = body.get("client_created_at")

        if not event_type:
            return error_response(400, "event_type is required")

        try:
            parse_client_timestamp(client_created_at)
        except (TypeError, ValueError):
            return error_response(400, "client_created_at must be a valid ISO-8601 timestamp")

        record_interaction_event(
            participant_key=body.get("participantID"),
            conversation_id=body.get("interviewID"),
            event_type=event_type,
            page=body.get("page"),
            target=body.get("target"),
            client_created_at=client_created_at,
            metadata=body.get("metadata"),
        )
        return {"status": "recorded"}

    except Exception as e:
        logger.error(f"[/chatbot/interaction_event]: {str(e)}")
        return error_response(500, str(e))


@app.get("/chatbot/export")
def export_data(x_export_token: Optional[str] = Header(default=None)):
    expected_token = os.getenv("DATA_EXPORT_TOKEN")
    if not expected_token:
        return error_response(503, "Data export is not configured")
    if not x_export_token or x_export_token != expected_token:
        return error_response(403, "Invalid export token")

    archive = export_database_zip()
    filename = f"chatbot-data-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.zip"
    return StreamingResponse(
        io.BytesIO(archive),
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )




def cleanup_engines():
    while True:
        time.sleep(60)
        keys_to_remove = []

        current_time = time.time()
        for key in list(engines.keys()):  # Iterate over a copy of the keys
            last_updated = engines_last_updated_time.get(key)
            if last_updated and current_time - last_updated >= CACHE_TIME:
                keys_to_remove.append(key)

        logger.debug(f"Existing engines: {engines_last_updated_time}. Cleaning up expired engines: {keys_to_remove}")
        for key in keys_to_remove:
            engines.pop(key, None)
            engines_last_updated_time.pop(key, None)  # Clean up timestamp as well



if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
