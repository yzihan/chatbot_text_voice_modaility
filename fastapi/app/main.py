import ast
import json
import os
from pathlib import Path
import pickle
import threading
from threading import Lock
import time
import uuid

from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from conversation_engine.engine import ConversationEngine
from conversation_engine.logger import logger
from conversation_engine.openai_api import send_audio
from conversation_engine.question_list.codes.question_list import create_quetion_nodes
from conversation_engine.question_list.codes.question_sequence import get_question_indices


user_count_lock = Lock()  # 用于线程安全的计数器更新

load_dotenv()



CACHE_TIME = 60 * 60  # 1 hour
DATABASE_DIR = Path("./database")
USER_DIR = DATABASE_DIR / "user"
CHAT_DIR = DATABASE_DIR / "chats"
USER_COUNT_FILE = Path("user_count.txt")

USER_DIR.mkdir(parents=True, exist_ok=True)
CHAT_DIR.mkdir(parents=True, exist_ok=True)


def error_response(status_code: int, message: str) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"error": message})


def user_file_path(participant_id: str) -> Path:
    return USER_DIR / f"{participant_id}.txt"


def chat_save_path(participant_id: str, interview_id: str) -> Path:
    return CHAT_DIR / participant_id / interview_id


def read_user_data(participant_id: str) -> dict:
    """Read existing user files saved as JSON or legacy Python dict strings."""
    raw_data = user_file_path(participant_id).read_text()

    try:
        return json.loads(raw_data)
    except json.JSONDecodeError:
        return ast.literal_eval(raw_data)


def write_user_data(participant_id: str, data: dict) -> None:
    user_file_path(participant_id).write_text(json.dumps(data, indent=2))


def record_selection_reason(participant_id: str, group: str, selection_reason: str, interview_id: str, source: str) -> None:
    data = read_user_data(participant_id)
    selection_records = data.get("selection_records", [])
    selection_records.append({
        "interview_id": interview_id,
        "group": group,
        "selection_reason": selection_reason,
        "source": source,
        "created_time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    })
    data["selection_records"] = selection_records
    write_user_data(participant_id, data)


def next_user_index() -> int:
    with user_count_lock:
        if USER_COUNT_FILE.exists():
            user_index = int(USER_COUNT_FILE.read_text().strip() or "0") + 1
        else:
            user_index = 1

        USER_COUNT_FILE.write_text(str(user_index))
        return user_index


def get_all_metadata_by_pid(participant_id: str) -> list:
    base_path = CHAT_DIR / participant_id
    all_metadata = []

    if not base_path.exists():
        return []

    for session_path in base_path.iterdir():
        metadata_path = session_path / "metadata.pkl"

        if session_path.is_dir() and metadata_path.exists():
            with metadata_path.open("rb") as f:
                all_metadata.append(pickle.load(f))

    return all_metadata


def get_cors_allowed_origins() -> list[str]:
    origins = os.getenv("CORS_ALLOWED_ORIGINS", "")
    return [origin.strip() for origin in origins.split(",") if origin.strip()]




app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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

        if user_file_path(participant_id).exists():
            data = read_user_data(participant_id)
            return data["_id"]

        user_index = next_user_index()
        user_id = str(uuid.uuid4())
        data = {
            "_id": user_id,
            "user_index": user_index,
            "participantID": participant_id,
        }
        write_user_data(participant_id, data)

        return user_id

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
        source = body.get("source")

        if not participant_id:
            return error_response(400, "participantID is required")
        
        if not group:
            return error_response(400, "group is required")

        if source == "selection" and not selection_reason.strip():
            return error_response(400, "selectionReason is required")
        

        if not user_file_path(participant_id).exists():
            return error_response(400, "User data is lost. Please re-register.")

        data = read_user_data(participant_id)
        user_index = data["user_index"]


        interview_id = str(uuid.uuid4())
        # TODO: this is hard coded for now, need to be dynamic based on different interview types in the future.
        question_indices = get_question_indices("HEX")

        engine = ConversationEngine(
            session_id=interview_id,
            user_index=user_index,
            group=group,
            source=source,
            selection_reason=selection_reason.strip(),
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
            record_selection_reason(
                participant_id=participant_id,
                group=group,
                selection_reason=selection_reason.strip(),
                interview_id=interview_id,
                source=source,
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
    try:
        unique_id = str(uuid.uuid4())
        save_dir = chat_save_path(participantID, interviewID)
        save_dir.mkdir(parents=True, exist_ok=True)

        webm_path = save_dir / f"{unique_id}.webm"

        with webm_path.open("wb") as buffer:
            content = await audio.read()
            buffer.write(content)

        with webm_path.open("rb") as f:
            transcript = send_audio(f)

        return JSONResponse(content={
            "transcript": transcript,
            "message": "Audio saved and transcribed successfully!",
            "file_path": str(webm_path),
        })

    except Exception as e:
        logger.error(f"[/chatbot/voice-chat]: {str(e)}")
        return error_response(500, f"Error for voice recognition: {str(e)}")


@app.post("/chatbot/chat")
async def continue_conversation(request: Request):
    try:
        body = await request.json()

        interviewID = body.get("interviewID")
        user_resp = body.get("user_resp")
        audioFilepPath = body.get("audioFilepPath")
        

        if not interviewID or not user_resp:
            return error_response(400, "Missing 'interviewID' or 'user_resp'")

        if interviewID not in engines:
            logger.debug(f"Conversation Expired: {interviewID}")
            return error_response(404, "Your session expired! Please go back to home page and restart again!")

        engine = engines[interviewID]
        engines_last_updated_time[interviewID] = time.time()

        logger.debug(f"Chat Conversation: {interviewID}")
        logger.debug(f"Current Activate conversations: {engines_last_updated_time}")

        # Assuming this method is async
        data = await engine.process_user_response(user_resp, audioFilepPath)

        if data.get("status") == "success":
            engine.save_conversation_state()
            return {
                "question_data": data["messages_to_returned"],
                "is_ending": data["is_ending"]
            }
        else:
            logger.error(f"[/chatbot/chat]: {data.get('error', 'Unknown error')}")
            return error_response(500, f"Some error happened for chatting: {data.get('error', 'Unknown error')}")

    except Exception as e:
        return error_response(500, f"Error for chatting: {str(e)}")
    
@app.post("/chatbot/chat_history")
async def get_chat_history(request: Request):
    try:
        body = await request.json()
        participant_id = body.get("participantID")
        if not participant_id:
            return error_response(400, "Missing participantID in request body")

        metadatas = get_all_metadata_by_pid(participant_id)

        # sort by updated time
        metadatas.sort(key=lambda item: item["updated_time"], reverse=True)

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



@app.on_event("startup")
def start_cleanup_thread():
    thread = threading.Thread(target=cleanup_engines, daemon=True)
    thread.start()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
