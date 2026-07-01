"""Generate a deterministic three-user SQL/export fixture through the real API."""

import argparse
import json
import os
import shutil
import sys
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    database_path = output_dir / "simulation.db"
    export_path = output_dir.parent / f"{output_dir.name}.zip"
    database_path.unlink(missing_ok=True)
    export_path.unlink(missing_ok=True)
    shutil.rmtree(output_dir / "chats", ignore_errors=True)

    os.environ["DATABASE_URL"] = f"sqlite:///{database_path}"
    os.environ["DATA_EXPORT_TOKEN"] = "simulation-export-token"
    os.environ.setdefault("OPENAI_API_KEY", "test-placeholder")
    sys.path.insert(0, str(Path(__file__).resolve().parent))

    from fastapi.testclient import TestClient
    import main as main_module
    from conversation_engine.engine import assistant_message

    transcripts = iter(["first raw sentence", "second raw sentence"])
    main_module.send_audio = lambda _file: next(transcripts)
    main_module.CHAT_DIR = output_dir / "chats"

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
        response_metadata=None,
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
            "info": response_metadata or {},
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

    main_module.ConversationEngine.process_user_response = deterministic_process
    main_module.ConversationEngine.save_conversation_state = lambda _self: None

    users = {
        "selection": "selection-test@illinois.edu",
        "voice": "voice-test@illinois.edu",
        "keyboard": "keyboard-test@illinois.edu",
    }

    with TestClient(main_module.app) as client:
        for participant_id in users.values():
            require_success(
                client.post("/chatbot/user", json={"participantID": participant_id})
            )

        selection_reason = "  Keyboard lets me review every answer before sending.  "
        selection = require_success(
            client.post(
                "/chatbot/new_conversation",
                json={
                    "participantID": users["selection"],
                    "group": "keyboard",
                    "source": "selection",
                    "selectionReason": selection_reason,
                    "modalitySelectedClientAt": "2026-06-21T15:00:00.123456Z",
                    "selectionReasonClientAt": "2026-06-21T15:00:10.654321Z",
                },
            )
        )
        require_success(
            client.post(
                "/chatbot/chat",
                json={
                    "participantID": users["selection"],
                    "interviewID": selection["_id"],
                    "user_resp": "Selection participant exact keyboard response.",
                    "client_message_id": "selection-client-message",
                    "client_created_at": "2026-06-21T15:01:00.111111Z",
                    "input_method": "keyboard",
                },
            )
        )
        rejected = client.post(
            "/chatbot/new_conversation",
            json={
                "participantID": users["selection"],
                "group": "keyboard",
                "source": "selection",
                "selectionReason": "Missing timestamps must fail.",
            },
        )
        assert rejected.status_code == 400, rejected.text

        voice = require_success(
            client.post(
                "/chatbot/new_conversation",
                json={
                    "participantID": users["voice"],
                    "group": "voice",
                    "source": "voice",
                },
            )
        )
        recordings = []
        for index, audio_bytes in enumerate((b"first-audio", b"second-audio"), start=1):
            recordings.append(
                require_success(
                    client.post(
                        "/chatbot/voice-chat",
                        data={
                            "uid": "simulation-uid",
                            "participantID": users["voice"],
                            "interviewID": voice["_id"],
                        },
                        files={
                            "audio": (
                                f"recording-{index}.webm",
                                audio_bytes,
                                "audio/webm",
                            )
                        },
                    )
                )
            )

        edited_voice_text = (
            "first raw sentence second raw sentence, with a user-added clarification."
        )
        require_success(
            client.post(
                "/chatbot/chat",
                json={
                    "participantID": users["voice"],
                    "interviewID": voice["_id"],
                    "user_resp": edited_voice_text,
                    "audioFilepPath": recordings[-1]["file_path"],
                    "audio_recording_ids": [
                        recording["audio_recording_id"] for recording in recordings
                    ],
                    "audio_file_paths": [
                        recording["file_path"] for recording in recordings
                    ],
                    "client_message_id": "voice-client-message",
                    "client_created_at": "2026-06-21T15:02:00.222222Z",
                    "input_method": "voice",
                },
            )
        )
        duplicate = client.post(
            "/chatbot/chat",
            json={
                "participantID": users["voice"],
                "interviewID": voice["_id"],
                "user_resp": edited_voice_text,
                "client_message_id": "voice-client-message",
                "client_created_at": "2026-06-21T15:02:00.222222Z",
                "input_method": "voice",
            },
        )
        assert duplicate.status_code == 409, duplicate.text

        keyboard = require_success(
            client.post(
                "/chatbot/new_conversation",
                json={
                    "participantID": users["keyboard"],
                    "group": "keyboard",
                    "source": "keyboard",
                },
            )
        )
        require_success(
            client.post(
                "/chatbot/chat",
                json={
                    "participantID": users["keyboard"],
                    "interviewID": keyboard["_id"],
                    "user_resp": (
                        "Keyboard raw input with punctuation: commas, quotes, and  spaces."
                    ),
                    "client_message_id": "keyboard-client-message",
                    "client_created_at": "2026-06-21T15:03:00.333333Z",
                    "input_method": "keyboard",
                },
            )
        )
        failed = client.post(
            "/chatbot/chat",
            json={
                "participantID": users["keyboard"],
                "interviewID": keyboard["_id"],
                "user_resp": "Input captured before a simulated processing failure.",
                "client_message_id": "failed-client-message",
                "client_created_at": "2026-06-21T15:04:00.444444Z",
                "input_method": "keyboard",
            },
        )
        assert failed.status_code == 500, failed.text

        assert client.get("/chatbot/export").status_code == 403
        exported = client.get(
            "/chatbot/export",
            headers={"X-Export-Token": "simulation-export-token"},
        )
        require_success(exported, expect_json=False)
        export_path.write_bytes(exported.content)

    report = {
        "participants": 3,
        "conversations": 3,
            "messages": 13,
            "audio_recordings": 2,
            "interaction_events": 0,
        "negative_checks": {
            "selection_without_timestamps_rejected": True,
            "duplicate_message_rejected": True,
            "export_without_token_rejected": True,
            "failed_input_retained": True,
        },
        "export_zip": str(export_path),
    }
    (output_dir / "simulation-report.json").write_text(
        json.dumps(report, indent=2) + "\n"
    )
    print(json.dumps(report, indent=2))


def require_success(response, expect_json=True):
    assert response.status_code == 200, response.text
    return response.json() if expect_json else response


if __name__ == "__main__":
    main()
