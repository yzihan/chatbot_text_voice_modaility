import csv
import io
import json
import os
import sys
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import pytest
from sqlalchemy import func, select


TEST_DB = Path(tempfile.gettempdir()) / "chatbot_modality_sql_test.db"
TEST_DB.unlink(missing_ok=True)
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB}"
os.environ["DATA_EXPORT_TOKEN"] = "integration-export-token"
os.environ["OPENAI_API_KEY"] = "test-placeholder"
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient  # noqa: E402
from database_sql import Base, engine, init_database, session_scope  # noqa: E402
from conversation_engine.engine import assistant_message  # noqa: E402
import main as main_module  # noqa: E402
from sql_models import AudioRecording, Conversation, Message, Participant  # noqa: E402
from sql_repository import (  # noqa: E402
    create_conversation,
    complete_audio_transcription,
    export_database_zip,
    get_or_create_participant,
    record_audio_upload,
    record_conversation_turn,
    record_pending_user_input,
    record_failed_user_input,
)


@pytest.fixture(autouse=True)
def clean_database():
    Base.metadata.drop_all(bind=engine)
    init_database()
    yield


def test_complete_turn_audio_and_export_are_persisted():
    participant = get_or_create_participant("audit@illinois.edu")
    conversation_id = "11111111-1111-1111-1111-111111111111"
    initial_time = "2026-06-21T12:00:00.000001Z"

    create_conversation(
        conversation_id=conversation_id,
        participant_key=participant.participant_id,
        modality_group="voice",
        source_system="selection",
        selection_reason="Voice is faster for me.",
        modality_selected_client_at="2026-06-21T11:59:00Z",
        selection_reason_client_at="2026-06-21T11:59:30Z",
        question_code="HEX",
        question_sequence=["F1Q3", "F2Q2"],
        initial_messages=[
            {
                "id": "22222222-2222-2222-2222-222222222222",
                "role": "assistant",
                "content": "First question",
                "created_at": initial_time,
            }
        ],
    )

    recording = record_audio_upload(
        conversation_id=conversation_id,
        participant_key=participant.participant_id,
        file_path="/tmp/audit.webm",
        original_filename="recording.webm",
        mime_type="audio/webm",
        content=b"audio-bytes",
        upload_started_at=datetime(2026, 6, 21, 12, 1, tzinfo=timezone.utc),
        uploaded_at=datetime(2026, 6, 21, 12, 1, 0, 500000, tzinfo=timezone.utc),
    )
    recording = complete_audio_transcription(recording.id, "raw voice transcript")
    second_recording = record_audio_upload(
        conversation_id=conversation_id,
        participant_key=participant.participant_id,
        file_path="/tmp/audit-2.webm",
        original_filename="recording-2.webm",
        mime_type="audio/webm",
        content=b"more-audio-bytes",
        upload_started_at=datetime(2026, 6, 21, 12, 1, 1, tzinfo=timezone.utc),
        uploaded_at=datetime(2026, 6, 21, 12, 1, 1, 500000, tzinfo=timezone.utc),
    )
    second_recording = complete_audio_transcription(
        second_recording.id,
        "additional sentence",
    )

    user_message = {
            "id": "33333333-3333-3333-3333-333333333333",
            "role": "user",
            "content": "raw voice transcript with my edit",
            "raw_user_input": "raw voice transcript with my edit",
            "audio_file_path": "/tmp/audit.webm",
            "audio_recording_ids": [recording.id, second_recording.id],
            "client_message_id": "client-message-1",
            "client_created_at": "2026-06-21T12:01:02.000003Z",
            "input_method": "voice",
            "created_at": "2026-06-21T12:01:02.100004Z",
        }
    record_pending_user_input(conversation_id, user_message)
    record_conversation_turn(
        conversation_id=conversation_id,
        user_message=user_message,
        assistant_messages=[
            {
                "id": "44444444-4444-4444-4444-444444444444",
                "role": "assistant",
                "content": "Thanks for sharing.",
                "created_at": "2026-06-21T12:01:03.000005Z",
            }
        ],
        questions_answered=1,
        is_ending=False,
    )

    with session_scope() as session:
        messages = session.scalars(
            select(Message).order_by(Message.sequence_number)
        ).all()
        assert len(messages) == 3
        assert messages[1].raw_user_input == "raw voice transcript with my edit"
        assert messages[1].raw_transcript == "raw voice transcript additional sentence"
        assert messages[1].client_message_id == "client-message-1"
        assert messages[1].client_created_at is not None
        assert messages[1].server_received_at is not None
        assert messages[1].timestamp_source == "server"
        assert [item.id for item in messages[1].audio_recordings] == [
            recording.id,
            second_recording.id,
        ]
        assert messages[2].server_received_at is not None

        conversation = session.get(Conversation, conversation_id)
        assert conversation.selection_reason == "Voice is faster for me."
        assert conversation.modality_selected_client_at is not None
        assert conversation.selection_reason_client_at is not None
        assert json.loads(conversation.question_sequence) == ["F1Q3", "F2Q2"]
        assert conversation.questions_answered == 1

    archive = zipfile.ZipFile(io.BytesIO(export_database_zip()))
    assert set(archive.namelist()) == {
        "participants.csv",
        "conversations.csv",
        "messages.csv",
        "audio_recordings.csv",
    }
    exported_messages = list(
        csv.DictReader(io.StringIO(archive.read("messages.csv").decode()))
    )
    assert len(exported_messages) == 3
    assert exported_messages[1]["raw_user_input"] == "raw voice transcript with my edit"
    assert exported_messages[1]["raw_transcript"] == "raw voice transcript additional sentence"
    assert exported_messages[1]["server_received_at"].endswith("Z")
    exported_conversations = list(
        csv.DictReader(io.StringIO(archive.read("conversations.csv").decode()))
    )
    assert json.loads(exported_conversations[0]["question_sequence"]) == ["F1Q3", "F2Q2"]


def test_duplicate_client_message_id_is_rejected_without_duplicate_row():
    participant = get_or_create_participant("duplicate@illinois.edu")
    conversation_id = "55555555-5555-5555-5555-555555555555"
    create_conversation(
        conversation_id=conversation_id,
        participant_key=participant.participant_id,
        modality_group="keyboard",
        source_system="keyboard",
        selection_reason="",
        modality_selected_client_at=None,
        selection_reason_client_at=None,
        question_code="HEX",
        question_sequence=["F1Q3", "F2Q2"],
        initial_messages=[
            {
                "id": "66666666-6666-6666-6666-666666666666",
                "role": "assistant",
                "content": "Question",
                "created_at": "2026-06-21T12:00:00Z",
            }
        ],
    )
    user_message = {
        "id": "77777777-7777-7777-7777-777777777777",
        "role": "user",
        "content": "Exact keyboard input",
        "raw_user_input": "Exact keyboard input",
        "client_message_id": "same-client-id",
        "client_created_at": "2026-06-21T12:01:00Z",
        "input_method": "keyboard",
        "created_at": "2026-06-21T12:01:00.100000Z",
    }
    record_pending_user_input(conversation_id, user_message)
    record_conversation_turn(conversation_id, user_message, [], 1, False)

    duplicate = dict(user_message)
    duplicate["id"] = "88888888-8888-8888-8888-888888888888"
    with pytest.raises(ValueError, match="Duplicate client_message_id"):
        record_pending_user_input(conversation_id, duplicate)

    with session_scope() as session:
        count = session.scalar(
            select(func.count(Message.id)).where(Message.conversation_id == conversation_id)
        )
        assert count == 2


def test_pending_input_survives_and_can_be_marked_failed():
    participant = get_or_create_participant("failure@illinois.edu")
    conversation_id = "99999999-9999-9999-9999-999999999999"
    create_conversation(
        conversation_id=conversation_id,
        participant_key=participant.participant_id,
        modality_group="keyboard",
        source_system="keyboard",
        selection_reason="",
        modality_selected_client_at=None,
        selection_reason_client_at=None,
        question_code="HEX",
        question_sequence=["F1Q3", "F2Q2"],
        initial_messages=[],
    )
    message = {
        "id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        "role": "user",
        "content": "Input that must survive a processing failure",
        "raw_user_input": "Input that must survive a processing failure",
        "client_message_id": "failure-client-id",
        "client_created_at": "2026-06-21T12:01:00Z",
        "input_method": "keyboard",
        "created_at": "2026-06-21T12:01:00.100000Z",
    }
    record_pending_user_input(conversation_id, message)

    with session_scope() as session:
        row = session.scalar(
            select(Message).where(Message.client_message_id == "failure-client-id")
        )
        assert row.raw_user_input == "Input that must survive a processing failure"
        assert row.processing_status == "pending"
        assert row.processing_completed_at is None

    record_failed_user_input(conversation_id, message)
    with session_scope() as session:
        row = session.scalar(
            select(Message).where(Message.client_message_id == "failure-client-id")
        )
        assert row.processing_status == "failed"
        assert row.processing_completed_at is not None


def test_three_user_end_to_end_capture_and_protected_export(monkeypatch, tmp_path):
    main_module.engines.clear()
    main_module.engines_last_updated_time.clear()
    monkeypatch.setattr(main_module, "CHAT_DIR", tmp_path / "chats")

    transcripts = iter(["first raw sentence", "second raw sentence"])
    monkeypatch.setattr(main_module, "send_audio", lambda _file: next(transcripts))

    async def deterministic_process(
        engine_self,
        user_input,
        audioFilepPath,
        audio_recording_ids,
        audio_file_paths,
        server_message_id,
        client_message_id,
        client_created_at,
        input_method,
        server_received_at,
    ):
        if user_input == "Input captured before a simulated processing failure.":
            return {
                "status": "error",
                "error": "simulated processing failure",
            }
        user_message = {
            "id": server_message_id,
            "role": "user",
            "content": user_input,
            "raw_user_input": user_input,
            "audio_file_path": audioFilepPath,
            "audio_file_paths": audio_file_paths,
            "audio_recording_ids": audio_recording_ids,
            "client_message_id": client_message_id,
            "client_created_at": client_created_at,
            "input_method": input_method,
            "created_at": server_received_at,
        }
        response = assistant_message(f"Recorded: {user_input}")
        engine_self.complete_chatting_messages.extend([user_message, response])
        engine_self._questions_finished += 1
        engine_self._user_responses_received += 1
        return {
            "status": "success",
            "user_message": user_message,
            "messages_to_returned": [response],
            "is_ending": False,
        }

    monkeypatch.setattr(
        main_module.ConversationEngine,
        "process_user_response",
        deterministic_process,
    )
    monkeypatch.setattr(
        main_module.ConversationEngine,
        "save_conversation_state",
        lambda _self: None,
    )

    with TestClient(main_module.app) as client:
        users = [
            "selection-test@illinois.edu",
            "voice-test@illinois.edu",
            "keyboard-test@illinois.edu",
        ]
        for participant_id in users:
            response = client.post("/chatbot/user", json={"participantID": participant_id})
            assert response.status_code == 200

        selection_reason = "  Keyboard lets me review every answer before sending.  "
        selection_response = client.post(
            "/chatbot/new_conversation",
            json={
                "participantID": users[0],
                "group": "keyboard",
                "source": "selection",
                "selectionReason": selection_reason,
                "modalitySelectedClientAt": "2026-06-21T15:00:00.123456Z",
                "selectionReasonClientAt": "2026-06-21T15:00:10.654321Z",
            },
        )
        assert selection_response.status_code == 200, selection_response.text
        selection_conversation_id = selection_response.json()["_id"]
        selection_chat = client.post(
            "/chatbot/chat",
            json={
                "participantID": users[0],
                "interviewID": selection_conversation_id,
                "user_resp": "Selection participant exact keyboard response.",
                "client_message_id": "selection-client-message",
                "client_created_at": "2026-06-21T15:01:00.111111Z",
                "input_method": "keyboard",
            },
        )
        assert selection_chat.status_code == 200, selection_chat.text

        missing_selection_timestamps = client.post(
            "/chatbot/new_conversation",
            json={
                "participantID": users[0],
                "group": "keyboard",
                "source": "selection",
                "selectionReason": "This must be rejected without timestamps.",
            },
        )
        assert missing_selection_timestamps.status_code == 400

        voice_response = client.post(
            "/chatbot/new_conversation",
            json={
                "participantID": users[1],
                "group": "voice",
                "source": "voice",
            },
        )
        assert voice_response.status_code == 200, voice_response.text
        voice_conversation_id = voice_response.json()["_id"]

        recording_responses = []
        for index, audio_bytes in enumerate((b"first-audio", b"second-audio"), start=1):
            recording_response = client.post(
                "/chatbot/voice-chat",
                data={
                    "uid": "test-uid",
                    "participantID": users[1],
                    "interviewID": voice_conversation_id,
                },
                files={
                    "audio": (
                        f"recording-{index}.webm",
                        audio_bytes,
                        "audio/webm",
                    )
                },
            )
            assert recording_response.status_code == 200, recording_response.text
            recording_responses.append(recording_response.json())

        edited_voice_text = (
            "first raw sentence second raw sentence, with a user-added clarification."
        )
        voice_chat = client.post(
            "/chatbot/chat",
            json={
                "participantID": users[1],
                "interviewID": voice_conversation_id,
                "user_resp": edited_voice_text,
                "audioFilepPath": recording_responses[-1]["file_path"],
                "audio_recording_ids": [
                    response["audio_recording_id"] for response in recording_responses
                ],
                "audio_file_paths": [
                    response["file_path"] for response in recording_responses
                ],
                "client_message_id": "voice-client-message",
                "client_created_at": "2026-06-21T15:02:00.222222Z",
                "input_method": "voice",
            },
        )
        assert voice_chat.status_code == 200, voice_chat.text

        duplicate_voice_chat = client.post(
            "/chatbot/chat",
            json={
                "participantID": users[1],
                "interviewID": voice_conversation_id,
                "user_resp": edited_voice_text,
                "client_message_id": "voice-client-message",
                "client_created_at": "2026-06-21T15:02:00.222222Z",
                "input_method": "voice",
            },
        )
        assert duplicate_voice_chat.status_code == 409

        keyboard_response = client.post(
            "/chatbot/new_conversation",
            json={
                "participantID": users[2],
                "group": "keyboard",
                "source": "keyboard",
            },
        )
        assert keyboard_response.status_code == 200, keyboard_response.text
        keyboard_conversation_id = keyboard_response.json()["_id"]
        keyboard_input = "Keyboard raw input with punctuation: commas, quotes, and  spaces."
        keyboard_chat = client.post(
            "/chatbot/chat",
            json={
                "participantID": users[2],
                "interviewID": keyboard_conversation_id,
                "user_resp": keyboard_input,
                "client_message_id": "keyboard-client-message",
                "client_created_at": "2026-06-21T15:03:00.333333Z",
                "input_method": "keyboard",
            },
        )
        assert keyboard_chat.status_code == 200, keyboard_chat.text
        failed_chat = client.post(
            "/chatbot/chat",
            json={
                "participantID": users[2],
                "interviewID": keyboard_conversation_id,
                "user_resp": "Input captured before a simulated processing failure.",
                "client_message_id": "failed-client-message",
                "client_created_at": "2026-06-21T15:04:00.444444Z",
                "input_method": "keyboard",
            },
        )
        assert failed_chat.status_code == 500

        assert client.get("/chatbot/export").status_code == 403
        export_response = client.get(
            "/chatbot/export",
            headers={"X-Export-Token": "integration-export-token"},
        )
        assert export_response.status_code == 200

    archive = zipfile.ZipFile(io.BytesIO(export_response.content))
    exported = {
        filename: list(
            csv.DictReader(io.StringIO(archive.read(filename).decode("utf-8")))
        )
        for filename in archive.namelist()
    }
    assert len(exported["participants.csv"]) == 3
    assert len(exported["conversations.csv"]) == 3
    assert all(len(json.loads(row["question_sequence"])) == 24 for row in exported["conversations.csv"])
    # Each conversation begins with two assistant messages, followed by one
    # user message and one deterministic assistant response.
    assert len(exported["messages.csv"]) == 13
    assert len(exported["audio_recordings.csv"]) == 2

    conversations_by_source = {
        row["source_system"]: row for row in exported["conversations.csv"]
    }
    selection_row = conversations_by_source["selection"]
    assert selection_row["modality_group"] == "keyboard"
    assert selection_row["selection_reason"] == selection_reason
    assert selection_row["modality_selected_client_at"].endswith("Z")
    assert selection_row["selection_reason_client_at"].endswith("Z")
    assert selection_row["questions_answered"] == "1"
    assert (
        selection_row["modality_selected_client_at"]
        < selection_row["selection_reason_client_at"]
    )

    user_messages = {
        row["client_message_id"]: row
        for row in exported["messages.csv"]
        if row["role"] == "user"
    }
    assert set(user_messages) == {
        "selection-client-message",
        "voice-client-message",
        "keyboard-client-message",
        "failed-client-message",
    }
    for message_id, row in user_messages.items():
        assert row["client_created_at"].endswith("Z")
        assert row["server_received_at"].endswith("Z")
        assert row["processing_completed_at"].endswith("Z")
        expected_status = "failed" if message_id == "failed-client-message" else "completed"
        assert row["processing_status"] == expected_status
        assert row["timestamp_source"] == "server"

    assert (
        user_messages["selection-client-message"]["raw_user_input"]
        == "Selection participant exact keyboard response."
    )
    assert user_messages["keyboard-client-message"]["raw_user_input"] == keyboard_input
    assert (
        user_messages["failed-client-message"]["raw_user_input"]
        == "Input captured before a simulated processing failure."
    )
    assert user_messages["voice-client-message"]["raw_user_input"] == edited_voice_text
    assert (
        user_messages["voice-client-message"]["raw_transcript"]
        == "first raw sentence second raw sentence"
    )

    voice_audio_rows = exported["audio_recordings.csv"]
    assert all(row["message_id"] == user_messages["voice-client-message"]["id"] for row in voice_audio_rows)
    assert {row["raw_transcript"] for row in voice_audio_rows} == {
        "first raw sentence",
        "second raw sentence",
    }
    assert all(row["sha256"] for row in voice_audio_rows)
    assert all(row["uploaded_at"].endswith("Z") for row in voice_audio_rows)
    assert all(row["transcribed_at"].endswith("Z") for row in voice_audio_rows)
