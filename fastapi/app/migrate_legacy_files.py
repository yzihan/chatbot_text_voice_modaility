"""One-time migration from the legacy JSON/pickle files into the SQL database."""

from __future__ import annotations

import ast
import json
import pickle
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

from sqlalchemy import select

from database_sql import init_database, session_scope
from sql_models import AudioRecording, Conversation, Message, Participant


APP_DIR = Path(__file__).resolve().parent
LEGACY_USER_DIR = APP_DIR / "database" / "user"
LEGACY_CHAT_DIR = APP_DIR / "database" / "chats"


def read_legacy_user(path: Path) -> dict:
    raw = path.read_text()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return ast.literal_eval(raw)


def as_utc(value: Optional[str], fallback: datetime) -> datetime:
    if not value:
        return fallback
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def migrate() -> None:
    init_database()
    participant_map = {}

    with session_scope() as session:
        for user_path in sorted(LEGACY_USER_DIR.glob("*.txt")):
            data = read_legacy_user(user_path)
            participant_key = data["participantID"]
            participant = session.scalar(
                select(Participant).where(Participant.participant_id == participant_key)
            )
            if not participant:
                participant = Participant(
                    id=data.get("_id") or str(uuid.uuid4()),
                    participant_id=participant_key,
                    user_index=int(data["user_index"]),
                )
                session.add(participant)
                session.flush()
            participant_map[participant_key] = participant.id

        for participant_dir in sorted(LEGACY_CHAT_DIR.iterdir() if LEGACY_CHAT_DIR.exists() else []):
            if not participant_dir.is_dir():
                continue
            participant_key = participant_dir.name
            participant_id = participant_map.get(participant_key)
            if not participant_id:
                continue

            for conversation_dir in sorted(participant_dir.iterdir()):
                metadata_path = conversation_dir / "metadata.pkl"
                state_files = list(conversation_dir.glob("*_state.pkl"))
                if not metadata_path.exists() or not state_files:
                    continue

                with metadata_path.open("rb") as metadata_file:
                    metadata = pickle.load(metadata_file)
                with state_files[0].open("rb") as state_file:
                    state = pickle.load(state_file)
                legacy_messages = state.get("complete_chatting_messages", [])

                conversation_id = metadata["session_id"]
                if session.get(Conversation, conversation_id):
                    continue

                created_at = as_utc(metadata.get("created_time"), datetime.now(timezone.utc))
                updated_at = as_utc(metadata.get("updated_time"), created_at)
                conversation = Conversation(
                    id=conversation_id,
                    participant_id=participant_id,
                    modality_group=metadata.get("group") or state.get("group") or "unknown",
                    modality_selected_client_at=None,
                    source_system=metadata.get("source") or state.get("source") or "legacy",
                    selection_reason=metadata.get("selection_reason") or state.get("selection_reason") or "",
                    selection_reason_client_at=None,
                    status="completed" if state.get("is_ending") else "in_progress",
                    question_code=metadata.get("question_code", "HEX"),
                    question_sequence=json.dumps(
                        metadata.get("question_indices") or state.get("question_indices") or []
                    ),
                    questions_answered=sum(
                        1 for message in legacy_messages if message.get("role") == "user"
                    ),
                    created_at=created_at,
                    updated_at=updated_at,
                )
                session.add(conversation)
                session.flush()

                recordings_by_name = {}
                for audio_path in sorted(conversation_dir.glob("*.webm")):
                    content = audio_path.read_bytes()
                    file_time = datetime.fromtimestamp(audio_path.stat().st_mtime, tz=timezone.utc)
                    recording = AudioRecording(
                        conversation_id=conversation_id,
                        participant_id=participant_id,
                        file_path=str(audio_path.resolve()),
                        original_filename=audio_path.name,
                        mime_type="audio/webm",
                        byte_size=len(content),
                        sha256=__import__("hashlib").sha256(content).hexdigest(),
                        raw_transcript=None,
                        upload_started_at=file_time,
                        uploaded_at=file_time,
                        timestamp_source="legacy_filesystem",
                        transcription_succeeded=False,
                    )
                    session.add(recording)
                    session.flush()
                    recordings_by_name[audio_path.name] = recording

                for index, legacy_message in enumerate(legacy_messages, start=1):
                    inferred_at = created_at + timedelta(microseconds=index)
                    audio_path = legacy_message.get("audio_file_path") or legacy_message.get("audioFilepPath")
                    recording = recordings_by_name.get(Path(audio_path).name) if audio_path else None

                    message = Message(
                        id=legacy_message.get("id") or str(uuid.uuid4()),
                        conversation_id=conversation_id,
                        sequence_number=index,
                        role=legacy_message["role"],
                        content=legacy_message.get("content", ""),
                        raw_user_input=(
                            legacy_message.get("content", "")
                            if legacy_message["role"] == "user"
                            else None
                        ),
                        input_method=conversation.modality_group if legacy_message["role"] == "user" else None,
                        server_received_at=inferred_at,
                        timestamp_source="legacy_inferred",
                        processing_completed_at=inferred_at,
                        processing_status="completed",
                        metadata_json=json.dumps(legacy_message.get("info")) if legacy_message.get("info") else None,
                    )
                    session.add(message)
                    session.flush()
                    if recording:
                        recording.message_id = message.id

    print("Legacy migration completed.")


if __name__ == "__main__":
    migrate()
