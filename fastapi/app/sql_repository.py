from __future__ import annotations

import csv
import hashlib
import io
import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError

from database_sql import session_scope
from sql_models import AudioRecording, Conversation, InteractionEvent, Message, Participant, utc_now


def parse_client_timestamp(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def get_or_create_participant(participant_key: str) -> Participant:
    for _attempt in range(5):
        try:
            with session_scope() as session:
                participant = session.scalar(
                    select(Participant).where(Participant.participant_id == participant_key)
                )
                if participant:
                    participant.last_seen_at = utc_now()
                    return participant

                next_index = (session.scalar(select(func.max(Participant.user_index))) or 0) + 1
                participant = Participant(participant_id=participant_key, user_index=next_index)
                session.add(participant)
                session.flush()
                return participant
        except IntegrityError:
            continue
    raise RuntimeError("Could not allocate a unique participant index")


def get_participant(participant_key: str) -> Optional[Participant]:
    with session_scope() as session:
        return session.scalar(
            select(Participant).where(Participant.participant_id == participant_key)
        )


def create_conversation(
    conversation_id: str,
    participant_key: str,
    modality_group: str,
    source_system: str,
    selection_reason: str,
    modality_selected_client_at: Optional[str],
    selection_reason_client_at: Optional[str],
    question_code: str,
    question_sequence: list[str],
    initial_messages: list[dict],
) -> None:
    with session_scope() as session:
        participant = session.scalar(
            select(Participant).where(Participant.participant_id == participant_key)
        )
        if not participant:
            raise ValueError("Participant does not exist")

        conversation = Conversation(
            id=conversation_id,
            participant_id=participant.id,
            modality_group=modality_group,
            modality_selected_client_at=parse_client_timestamp(modality_selected_client_at),
            source_system=source_system,
            selection_reason=selection_reason,
            selection_reason_client_at=parse_client_timestamp(selection_reason_client_at),
            question_code=question_code,
            question_sequence=json.dumps(question_sequence),
        )
        session.add(conversation)
        session.flush()
        _append_messages(session, conversation_id, initial_messages, start_sequence=1)


def list_conversation_metadata(participant_key: str) -> list[dict]:
    with session_scope() as session:
        rows = session.execute(
            select(Conversation)
            .join(Participant)
            .where(Participant.participant_id == participant_key)
            .order_by(Conversation.updated_at.desc())
        ).scalars().all()
        return [
            {
                "session_id": row.id,
                "group": row.modality_group,
                "source": row.source_system,
                "selection_reason": row.selection_reason,
                "questions_answered": row.questions_answered,
                "created_time": _iso_timestamp(row.created_at),
                "updated_time": _iso_timestamp(row.updated_at),
                "status": row.status,
            }
            for row in rows
        ]


def conversation_belongs_to_participant(conversation_id: str, participant_key: str) -> bool:
    with session_scope() as session:
        return bool(
            session.scalar(
                select(Conversation.id)
                .join(Participant)
                .where(
                    Conversation.id == conversation_id,
                    Participant.participant_id == participant_key,
                )
            )
        )


def client_message_exists(conversation_id: str, client_message_id: str) -> bool:
    with session_scope() as session:
        return bool(
            session.scalar(
                select(Message.id).where(
                    Message.conversation_id == conversation_id,
                    Message.client_message_id == client_message_id,
                )
            )
        )


def record_audio_upload(
    conversation_id: str,
    participant_key: str,
    file_path: str,
    original_filename: Optional[str],
    mime_type: Optional[str],
    content: bytes,
    upload_started_at: datetime,
    uploaded_at: datetime,
) -> AudioRecording:
    with session_scope() as session:
        participant = session.scalar(
            select(Participant).where(Participant.participant_id == participant_key)
        )
        if not participant:
            raise ValueError("Participant does not exist")

        recording = AudioRecording(
            conversation_id=conversation_id,
            participant_id=participant.id,
            file_path=file_path,
            original_filename=original_filename,
            mime_type=mime_type,
            byte_size=len(content),
            sha256=hashlib.sha256(content).hexdigest(),
            raw_transcript=None,
            upload_started_at=upload_started_at,
            uploaded_at=uploaded_at,
            transcribed_at=None,
            transcription_succeeded=False,
        )
        session.add(recording)
        session.flush()
        return recording


def complete_audio_transcription(recording_id: str, transcript: str) -> AudioRecording:
    with session_scope() as session:
        recording = session.get(AudioRecording, recording_id)
        if not recording:
            raise ValueError("Audio recording does not exist")
        recording.raw_transcript = transcript
        recording.transcribed_at = utc_now()
        recording.transcription_succeeded = True
        session.flush()
        return recording


def record_conversation_turn(
    conversation_id: str,
    user_message: dict,
    assistant_messages: list[dict],
    questions_answered: int,
    is_ending: bool,
) -> None:
    with session_scope() as session:
        conversation = session.scalar(
            select(Conversation)
            .where(Conversation.id == conversation_id)
            .with_for_update()
        )
        if not conversation:
            raise ValueError("Conversation does not exist")

        existing = session.scalar(
            select(Message).where(
                Message.conversation_id == conversation_id,
                Message.client_message_id == user_message.get("client_message_id"),
            )
        )
        last_sequence = session.scalar(
            select(func.max(Message.sequence_number)).where(
                Message.conversation_id == conversation_id
            )
        ) or 0

        if existing:
            existing.content = user_message.get("content", "")
            existing.raw_user_input = user_message.get("raw_user_input")
            existing.input_method = user_message.get("input_method")
            existing.processing_status = "completed"
            existing.processing_completed_at = utc_now()
            _link_audio_recordings(session, existing, user_message)
            _append_messages(
                session,
                conversation_id,
                assistant_messages,
                start_sequence=last_sequence + 1,
            )
        else:
            _append_messages(
                session,
                conversation_id,
                [user_message, *assistant_messages],
                start_sequence=last_sequence + 1,
            )

        conversation.questions_answered = questions_answered
        conversation.updated_at = utc_now()
        if is_ending:
            conversation.status = "completed"
            conversation.completed_at = utc_now()


def record_pending_user_input(conversation_id: str, user_message: dict) -> None:
    pending_message = dict(user_message)
    pending_message["processing_status"] = "pending"
    with session_scope() as session:
        conversation = session.scalar(
            select(Conversation)
            .where(Conversation.id == conversation_id)
            .with_for_update()
        )
        if not conversation:
            raise ValueError("Conversation does not exist")
        if session.scalar(
            select(Message.id).where(
                Message.conversation_id == conversation_id,
                Message.client_message_id == pending_message.get("client_message_id"),
            )
        ):
            raise ValueError("Duplicate client_message_id")
        last_sequence = session.scalar(
            select(func.max(Message.sequence_number)).where(
                Message.conversation_id == conversation_id
            )
        ) or 0
        _append_messages(session, conversation_id, [pending_message], last_sequence + 1)


def record_failed_user_input(conversation_id: str, user_message: dict) -> None:
    failed_message = dict(user_message)
    failed_message["processing_status"] = "failed"
    with session_scope() as session:
        conversation = session.scalar(
            select(Conversation)
            .where(Conversation.id == conversation_id)
            .with_for_update()
        )
        if not conversation:
            raise ValueError("Conversation does not exist")
        existing = session.scalar(
            select(Message).where(
                Message.conversation_id == conversation_id,
                Message.client_message_id == failed_message.get("client_message_id"),
            )
        )
        if existing:
            existing.processing_status = "failed"
            existing.processing_completed_at = utc_now()
            return
        last_sequence = session.scalar(
            select(func.max(Message.sequence_number)).where(
                Message.conversation_id == conversation_id
            )
        ) or 0
        _append_messages(session, conversation_id, [failed_message], last_sequence + 1)


def record_interaction_event(
    participant_key: Optional[str],
    conversation_id: Optional[str],
    event_type: str,
    page: Optional[str],
    target: Optional[str],
    client_created_at: Optional[str],
    metadata: Optional[dict],
) -> None:
    with session_scope() as session:
        participant = None
        if participant_key:
            participant = session.scalar(
                select(Participant).where(Participant.participant_id == participant_key)
            )

        event = InteractionEvent(
            conversation_id=conversation_id or None,
            participant_id=participant.id if participant else None,
            event_type=event_type,
            page=page,
            target=target,
            client_created_at=parse_client_timestamp(client_created_at),
            server_received_at=utc_now(),
            metadata_json=json.dumps(metadata or {}),
        )
        session.add(event)


def _append_messages(session, conversation_id: str, messages: list[dict], start_sequence: int) -> None:
    for offset, message in enumerate(messages):
        metadata = message.get("info")
        row = Message(
            id=message.get("id"),
            conversation_id=conversation_id,
            sequence_number=start_sequence + offset,
            role=message["role"],
            content=message.get("content", ""),
            raw_user_input=message.get("raw_user_input"),
            raw_transcript=None,
            input_method=message.get("input_method"),
            client_message_id=message.get("client_message_id"),
            client_created_at=parse_client_timestamp(message.get("client_created_at")),
            server_received_at=parse_client_timestamp(message.get("created_at")) or utc_now(),
            timestamp_source=message.get("timestamp_source", "server"),
            processing_completed_at=(
                None if message.get("processing_status") == "pending" else utc_now()
            ),
            processing_status=message.get("processing_status", "completed"),
            metadata_json=json.dumps(metadata) if metadata is not None else None,
        )
        session.add(row)
        session.flush()
        _link_audio_recordings(session, row, message)


def _link_audio_recordings(session, message_row: Message, message: dict) -> None:
    audio_recordings = []
    audio_recording_ids = message.get("audio_recording_ids") or []
    if audio_recording_ids:
        fetched_recordings = session.scalars(
            select(AudioRecording).where(
                AudioRecording.id.in_(audio_recording_ids),
                AudioRecording.conversation_id == message_row.conversation_id,
                (AudioRecording.message_id.is_(None)) | (AudioRecording.message_id == message_row.id),
            )
        ).all()
        recordings_by_id = {recording.id: recording for recording in fetched_recordings}
        audio_recordings = [
            recordings_by_id[recording_id]
            for recording_id in audio_recording_ids
            if recording_id in recordings_by_id
        ]
        if len(audio_recordings) != len(audio_recording_ids):
            raise ValueError("One or more audio recordings are invalid")

    audio_path = message.get("audio_file_path") or message.get("audioFilepPath")
    if audio_path and not audio_recordings:
        recording = session.scalar(
            select(AudioRecording).where(
                AudioRecording.file_path == audio_path,
                (AudioRecording.message_id.is_(None)) | (AudioRecording.message_id == message_row.id),
            )
        )
        if recording:
            audio_recordings = [recording]

    message_row.raw_transcript = " ".join(
        recording.raw_transcript.strip()
        for recording in audio_recordings
        if recording.raw_transcript and recording.raw_transcript.strip()
    ) or None
    for recording in audio_recordings:
        recording.message_id = message_row.id


def export_database_zip() -> bytes:
    with session_scope() as session:
        tables = {
            "participants.csv": (
                Participant,
                session.scalars(select(Participant).order_by(Participant.created_at)).all(),
            ),
            "conversations.csv": (
                Conversation,
                session.scalars(select(Conversation).order_by(Conversation.created_at)).all(),
            ),
            "messages.csv": (
                Message,
                session.scalars(
                    select(Message).order_by(Message.conversation_id, Message.sequence_number)
                ).all(),
            ),
            "audio_recordings.csv": (
                AudioRecording,
                session.scalars(
                    select(AudioRecording).order_by(AudioRecording.uploaded_at)
                ).all(),
            ),
            "interaction_events.csv": (
                InteractionEvent,
                session.scalars(
                    select(InteractionEvent).order_by(InteractionEvent.server_received_at)
                ).all(),
            ),
        }

        output = io.BytesIO()
        with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for filename, (model, rows) in tables.items():
                text_buffer = io.StringIO()
                writer = csv.writer(text_buffer)
                columns = [column.name for column in model.__table__.columns]
                writer.writerow(columns)
                for row in rows:
                    writer.writerow([_csv_value(getattr(row, column)) for column in columns])
                archive.writestr(filename, text_buffer.getvalue())
            archive.writestr(
                "participant_question_responses.csv",
                _participant_question_response_csv(session),
            )
        return output.getvalue()


def _participant_question_response_csv(session) -> str:
    conversations = session.scalars(
        select(Conversation).order_by(Conversation.created_at)
    ).all()
    messages = session.scalars(
        select(Message).order_by(Message.conversation_id, Message.sequence_number)
    ).all()
    participants = {
        participant.id: participant
        for participant in session.scalars(select(Participant)).all()
    }
    user_messages_by_conversation_question: dict[tuple[str, str], list[Message]] = {}

    for message in messages:
        if message.role != "user" or not message.metadata_json:
            continue
        try:
            metadata = json.loads(message.metadata_json)
        except json.JSONDecodeError:
            continue
        question_index = metadata.get("question_index")
        if not question_index:
            continue
        key = (message.conversation_id, question_index)
        user_messages_by_conversation_question.setdefault(key, []).append(message)

    columns = [
        "conversation_id",
        "participant_id",
        "modality_group",
        "source_system",
        "conversation_status",
        "assigned_order",
        "question_index",
        "response_count",
        "missing_response",
        "primary_response",
        "followup_response_1",
        "followup_response_2",
        "processing_statuses",
        "primary_response_time_ms",
        "primary_client_created_at",
        "primary_server_received_at",
        "primary_response_to_node_id",
    ]
    text_buffer = io.StringIO()
    writer = csv.writer(text_buffer)
    writer.writerow(columns)

    for conversation in conversations:
        participant = participants.get(conversation.participant_id)
        try:
            question_sequence = json.loads(conversation.question_sequence)
        except json.JSONDecodeError:
            question_sequence = []
        for assigned_order, question_index in enumerate(question_sequence, start=1):
            question_messages = user_messages_by_conversation_question.get(
                (conversation.id, question_index),
                [],
            )
            primary = question_messages[0] if question_messages else None
            primary_metadata = {}
            if primary and primary.metadata_json:
                try:
                    primary_metadata = json.loads(primary.metadata_json)
                except json.JSONDecodeError:
                    primary_metadata = {}
            writer.writerow([
                conversation.id,
                participant.participant_id if participant else "",
                conversation.modality_group,
                conversation.source_system,
                conversation.status,
                assigned_order,
                question_index,
                len(question_messages),
                "true" if not question_messages else "false",
                question_messages[0].raw_user_input if len(question_messages) > 0 else "",
                question_messages[1].raw_user_input if len(question_messages) > 1 else "",
                question_messages[2].raw_user_input if len(question_messages) > 2 else "",
                "|".join(message.processing_status for message in question_messages),
                primary_metadata.get("response_time_ms", ""),
                _csv_value(primary.client_created_at) if primary else "",
                _csv_value(primary.server_received_at) if primary else "",
                primary_metadata.get("response_to_node_id", ""),
            ])

    return text_buffer.getvalue()


def _csv_value(value):
    if isinstance(value, datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    if value is None:
        return ""
    return value


def _iso_timestamp(value: datetime) -> str:
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
