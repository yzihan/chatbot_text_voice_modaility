import asyncio
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from conversation_engine.engine import ConversationEngine  # noqa: E402
from conversation_engine.node import NodeType, Signal  # noqa: E402
from conversation_engine.question_list.codes.question_list import create_quetion_nodes  # noqa: E402
from conversation_engine.question_list.codes.question_sequence import get_selected_question_indices  # noqa: E402


def reachable_nodes(root):
    seen = set()
    stack = [root]
    while stack:
        node = stack.pop()
        if node.id in seen:
            continue
        seen.add(node.id)
        yield node
        stack.extend(node.next_nodes.values())
        stack.extend(option.next_node for option in node.options if option.next_node)


def make_follow_up(current_node, condition, **_kwargs):
    next_node = current_node.next_nodes[condition]
    next_node.text = (
        f"Follow-up for displayed question {current_node.info.get('progress')}: "
        "please add a little more detail."
    )


def patch_for_deterministic_validity(root, invalid_first_pass_progress=None):
    invalid_first_pass_progress = set(invalid_first_pass_progress or [])
    attempts_by_progress = {}

    for node in reachable_nodes(root):
        if node.node_type not in {NodeType.DEFAULT_QUESTION, NodeType.NO_CONDITION_CHECK}:
            continue

        progress = node.info.get("progress")

        def condition_check(_messages, node_id=node.id, progress=progress):
            attempts_by_progress[progress] = attempts_by_progress.get(progress, 0) + 1
            if node_id.endswith("_2") and progress in invalid_first_pass_progress:
                return "UNINFORMATIVE"
            return "VALID"

        node.condition_check = condition_check
        node.summary_generators = {
            "NEEDS_CLARIFICATION": Signal.SKIP_SUMMARY_SIGNAL,
            "NONSENSE": Signal.SKIP_SUMMARY_SIGNAL,
            "UNINFORMATIVE": Signal.SKIP_SUMMARY_SIGNAL,
            "VALID": "Thanks. Let's continue.",
            "DECLINE_CONTINUE": Signal.SKIP_SUMMARY_SIGNAL,
            "default": "Thanks. Let's continue.",
        }
        for condition in ("NEEDS_CLARIFICATION", "NONSENSE", "UNINFORMATIVE"):
            node.parallism_works[condition] = [make_follow_up]
        node.parallism_works["VALID"] = []
        node.parallism_works["default"] = []


def test_full_selected_question_flow_preserves_order_and_follow_up_boundaries(tmp_path):
    selected = get_selected_question_indices()
    root = create_quetion_nodes(selected)
    patch_for_deterministic_validity(root, invalid_first_pass_progress={11})

    engine = ConversationEngine(
        session_id="flow-audit-session",
        user_index=1,
        group="keyboard",
        source="selection",
        question_indices=selected,
        user_info={"user_name": "flow-audit", "uid": "flow-audit"},
        root_node=root,
        save_path=str(tmp_path),
        selection_reason="Keyboard is easiest to audit.",
    )

    init = engine.init_conversation()
    assert init["status"] == "success"
    assert init["is_ending"] is False

    seen_progress = []
    seen_question_indices = []
    assistant_contents_by_progress = {}
    user_turns = 0

    while not engine.current_node.node_type == NodeType.END_NODE:
        progress = engine.current_node.info.get("progress")
        question_index = engine.current_node.info.get("question_index")
        response_text = (
            f"Participant answer for displayed question {progress}, "
            f"question id {question_index}."
        )
        if progress == 11 and engine.current_node.id.endswith("_2"):
            response_text = "Brief."

        result = asyncio.run(
            engine.process_user_response(
                user_input=response_text,
                audioFilepPath=None,
                audio_recording_ids=[],
                audio_file_paths=[],
                server_message_id=f"user-{user_turns}",
                client_message_id=f"client-{user_turns}",
                client_created_at="2026-06-21T12:00:00Z",
                input_method="keyboard",
                server_received_at="2026-06-21T12:00:01Z",
                response_metadata={
                    **engine.current_node.info,
                    "response_to_node_id": engine.current_node.id,
                    "response_time_ms": 1000 + user_turns,
                },
            )
        )
        assert result["status"] == "success"
        user_turns += 1

        for message in result["messages_to_returned"]:
            info = message.get("info") or {}
            if info.get("progress"):
                assistant_contents_by_progress.setdefault(info["progress"], []).append(message["content"])
                if message["content"].startswith("Follow-up for displayed question"):
                    continue
                if info["progress"] not in seen_progress:
                    seen_progress.append(info["progress"])
                    seen_question_indices.append(info.get("question_index"))

    assert seen_progress == list(range(1, 25))
    assert seen_question_indices == selected

    assert user_turns == 28
    assert engine._user_responses_received == 28
    assert engine.current_node.node_type == NodeType.END_NODE

    assert any(
        content.startswith("Follow-up for displayed question 11")
        for content in assistant_contents_by_progress[11]
    )
    assert not any(
        content.startswith("Follow-up for displayed question 11")
        for content in assistant_contents_by_progress.get(12, [])
    )
    assert not any(
        content.startswith("Follow-up for displayed question 11")
        for content in assistant_contents_by_progress.get(13, [])
    )

    user_messages = [
        message for message in engine.complete_chatting_messages if message["role"] == "user"
    ]
    scored_user_messages = [
        message for message in user_messages if message.get("info", {}).get("progress")
    ]
    assert [message["info"]["response_to_node_id"] for message in scored_user_messages[:11]][-1].endswith("_2")
    assert [message["info"]["progress"] for message in scored_user_messages].count(11) == 2
    assert [message["info"]["progress"] for message in scored_user_messages].count(12) == 1
    assert [message["info"]["progress"] for message in scored_user_messages].count(13) == 1
