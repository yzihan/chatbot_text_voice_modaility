"""Validate referential integrity, timestamps, and required research fields in an export ZIP."""

import argparse
import csv
import io
import json
import zipfile
from collections import defaultdict
from datetime import datetime
from pathlib import Path


REQUIRED_FILES = {
    "participants.csv",
    "conversations.csv",
    "messages.csv",
    "audio_recordings.csv",
}


def parse_timestamp(value: str, field: str, errors: list[str]):
    if not value:
        errors.append(f"Missing timestamp: {field}")
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        errors.append(f"Invalid timestamp: {field}={value}")
        return None


def audit(export_path: Path) -> dict:
    errors = []
    with zipfile.ZipFile(export_path) as archive:
        names = set(archive.namelist())
        if names != REQUIRED_FILES:
            errors.append(f"Unexpected export files: {sorted(names)}")
        tables = {
            name: list(csv.DictReader(io.StringIO(archive.read(name).decode("utf-8"))))
            for name in REQUIRED_FILES
        }

    participants = {row["id"]: row for row in tables["participants.csv"]}
    conversations = {row["id"]: row for row in tables["conversations.csv"]}
    messages = tables["messages.csv"]
    audio_rows = tables["audio_recordings.csv"]
    messages_by_id = {row["id"]: row for row in messages}

    if len(participants) != len(tables["participants.csv"]):
        errors.append("Duplicate participant IDs")
    if len(conversations) != len(tables["conversations.csv"]):
        errors.append("Duplicate conversation IDs")
    if len(messages_by_id) != len(messages):
        errors.append("Duplicate message IDs")

    sequences = defaultdict(list)
    client_ids = set()
    for conversation in conversations.values():
        if conversation["participant_id"] not in participants:
            errors.append(f"Conversation has missing participant: {conversation['id']}")
        created = parse_timestamp(
            conversation["created_at"],
            f"conversation {conversation['id']} created_at",
            errors,
        )
        updated = parse_timestamp(
            conversation["updated_at"],
            f"conversation {conversation['id']} updated_at",
            errors,
        )
        if created and updated and updated < created:
            errors.append(f"Conversation updated before creation: {conversation['id']}")
        if conversation["source_system"] == "selection":
            if not conversation["selection_reason"]:
                errors.append(f"Selection reason missing: {conversation['id']}")
            selected = parse_timestamp(
                conversation["modality_selected_client_at"],
                f"conversation {conversation['id']} modality_selected_client_at",
                errors,
            )
            reason = parse_timestamp(
                conversation["selection_reason_client_at"],
                f"conversation {conversation['id']} selection_reason_client_at",
                errors,
            )
            if selected and reason and reason < selected:
                errors.append(f"Selection reason predates mode selection: {conversation['id']}")

    for message in messages:
        conversation_id = message["conversation_id"]
        if conversation_id not in conversations:
            errors.append(f"Message has missing conversation: {message['id']}")
        sequences[conversation_id].append(int(message["sequence_number"]))
        received = parse_timestamp(
            message["server_received_at"],
            f"message {message['id']} server_received_at",
            errors,
        )
        completed = None
        if message["processing_completed_at"]:
            completed = parse_timestamp(
                message["processing_completed_at"],
                f"message {message['id']} processing_completed_at",
                errors,
            )
        if received and completed and completed < received:
            errors.append(f"Message completed before receipt: {message['id']}")
        if message["role"] == "user":
            if not message["raw_user_input"]:
                errors.append(f"User raw input missing: {message['id']}")
            if not message["client_message_id"]:
                errors.append(f"Client message ID missing: {message['id']}")
            if not message["client_created_at"]:
                errors.append(f"Client timestamp missing: {message['id']}")
            key = (conversation_id, message["client_message_id"])
            if key in client_ids:
                errors.append(f"Duplicate client message ID: {key}")
            client_ids.add(key)

    for conversation_id, values in sequences.items():
        if sorted(values) != list(range(1, len(values) + 1)):
            errors.append(f"Non-contiguous message sequence: {conversation_id}={values}")

    for audio in audio_rows:
        if audio["conversation_id"] not in conversations:
            errors.append(f"Audio has missing conversation: {audio['id']}")
        if audio["participant_id"] not in participants:
            errors.append(f"Audio has missing participant: {audio['id']}")
        if audio["message_id"] and audio["message_id"] not in messages_by_id:
            errors.append(f"Audio has missing message: {audio['id']}")
        if len(audio["sha256"]) != 64:
            errors.append(f"Audio SHA-256 invalid: {audio['id']}")
        started = parse_timestamp(
            audio["upload_started_at"],
            f"audio {audio['id']} upload_started_at",
            errors,
        )
        uploaded = parse_timestamp(
            audio["uploaded_at"],
            f"audio {audio['id']} uploaded_at",
            errors,
        )
        transcribed = None
        if audio["transcribed_at"]:
            transcribed = parse_timestamp(
                audio["transcribed_at"],
                f"audio {audio['id']} transcribed_at",
                errors,
            )
        if started and uploaded and uploaded < started:
            errors.append(f"Audio uploaded before upload started: {audio['id']}")
        if uploaded and transcribed and transcribed < uploaded:
            errors.append(f"Audio transcribed before upload completed: {audio['id']}")
        if audio["transcription_succeeded"] == "True" and not audio["raw_transcript"]:
            errors.append(f"Successful audio transcript is empty: {audio['id']}")

    return {
        "passed": not errors,
        "counts": {
            "participants": len(participants),
            "conversations": len(conversations),
            "messages": len(messages),
            "audio_recordings": len(audio_rows),
        },
        "errors": errors,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("export_zip", type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    report = audit(args.export_zip)
    rendered = json.dumps(report, indent=2) + "\n"
    if args.report:
        args.report.write_text(rendered)
    print(rendered, end="")
    if not report["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
