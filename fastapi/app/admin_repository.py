from __future__ import annotations

import csv
import io
import json
from datetime import datetime, timezone
from statistics import median
from typing import Iterable, Optional

from sqlalchemy import func, or_, select

from admin_auth import hash_password, verify_password
from database_sql import session_scope
from sql_models import (
    AdminAuditLog,
    AdminChatbotPermission,
    AdminUser,
    BackendRequestLog,
    Conversation,
    Message,
    Participant,
    utc_now,
)
from sql_repository import parse_client_timestamp


ADMIN_ROLES = {"admin", "project_leader", "viewer"}
EXPORT_ROLES = {"admin", "project_leader"}
UNMASKED_ROLES = {"admin", "project_leader"}


def chatbot_key(source_system: str, modality_group: str) -> str:
    return f"{source_system}:{modality_group}"


def create_admin_user(
    email: str,
    password: str,
    display_name: str,
    role: str,
    chatbot_keys: Optional[list[str]] = None,
) -> dict:
    if role not in ADMIN_ROLES:
        raise ValueError("Invalid admin role")
    normalized_email = email.strip().lower()
    if not normalized_email or "@" not in normalized_email:
        raise ValueError("A valid email is required")
    if len(password) < 10:
        raise ValueError("Password must be at least 10 characters")
    user_id = ""
    with session_scope() as session:
        if session.scalar(select(AdminUser.id).where(AdminUser.email == normalized_email)):
            raise ValueError("An admin user with this email already exists")
        user = AdminUser(
            email=normalized_email,
            display_name=display_name.strip() or normalized_email,
            role=role,
            password_hash=hash_password(password),
        )
        session.add(user)
        session.flush()
        user_id = user.id
        for key in sorted(set(chatbot_keys or [])):
            session.add(AdminChatbotPermission(user_id=user.id, chatbot_key=key))
    with session_scope() as session:
        return serialize_admin_user(session.get(AdminUser, user_id), include_permissions=True)


def authenticate_admin(email: str, password: str) -> Optional[AdminUser]:
    with session_scope() as session:
        user = session.scalar(select(AdminUser).where(AdminUser.email == email.strip().lower()))
        if not user or not user.is_active or not verify_password(password, user.password_hash):
            return None
        return user


def has_admin_users() -> bool:
    with session_scope() as session:
        return bool(session.scalar(select(func.count(AdminUser.id))))


def list_admin_users() -> list[dict]:
    with session_scope() as session:
        users = session.scalars(select(AdminUser).order_by(AdminUser.email)).all()
        return [serialize_admin_user(user, include_permissions=True) for user in users]


def update_user_access(
    user_id: str,
    role: str,
    chatbot_keys: list[str],
    is_active: bool,
) -> dict:
    if role not in ADMIN_ROLES:
        raise ValueError("Invalid admin role")
    with session_scope() as session:
        user = session.get(AdminUser, user_id)
        if not user:
            raise ValueError("Admin user not found")
        user.role = role
        user.is_active = bool(is_active)
        session.query(AdminChatbotPermission).filter(
            AdminChatbotPermission.user_id == user_id
        ).delete()
        for key in sorted(set(chatbot_keys)):
            session.add(AdminChatbotPermission(user_id=user_id, chatbot_key=key))
    with session_scope() as session:
        return serialize_admin_user(session.get(AdminUser, user_id), include_permissions=True)


def serialize_admin_user(user: AdminUser, include_permissions: bool = False) -> dict:
    data = {
        "id": user.id,
        "email": user.email,
        "display_name": user.display_name,
        "role": user.role,
        "is_active": user.is_active,
        "created_at": _iso_timestamp(user.created_at),
        "last_login_at": _iso_timestamp(user.last_login_at),
    }
    if include_permissions:
        with session_scope() as session:
            data["chatbot_keys"] = sorted(
                session.scalars(
                    select(AdminChatbotPermission.chatbot_key).where(
                        AdminChatbotPermission.user_id == user.id
                    )
                ).all()
            )
    return data


def get_accessible_chatbot_keys(user: AdminUser) -> Optional[set[str]]:
    if user.role == "admin":
        return None
    with session_scope() as session:
        rows = session.scalars(
            select(AdminChatbotPermission.chatbot_key).where(
                AdminChatbotPermission.user_id == user.id
            )
        ).all()
        return set(rows)


def list_chatbots(user: AdminUser) -> list[dict]:
    allowed = get_accessible_chatbot_keys(user)
    with session_scope() as session:
        rows = session.execute(
            select(
                Conversation.source_system,
                Conversation.modality_group,
                func.count(Conversation.id),
                func.max(Conversation.updated_at),
            )
            .group_by(Conversation.source_system, Conversation.modality_group)
            .order_by(Conversation.source_system, Conversation.modality_group)
        ).all()
    chatbots = []
    for source_system, modality_group, session_count, last_activity in rows:
        key = chatbot_key(source_system, modality_group)
        if allowed is not None and key not in allowed:
            continue
        chatbots.append({
            "key": key,
            "name": _chatbot_name(source_system, modality_group),
            "source_system": source_system,
            "modality_group": modality_group,
            "session_count": session_count,
            "last_activity_at": _iso_timestamp(last_activity),
        })
    return chatbots


def get_dashboard_summary(user: AdminUser) -> dict:
    allowed = get_accessible_chatbot_keys(user)
    with session_scope() as session:
        conversations = _allowed_conversations_query(allowed)
        rows = session.scalars(conversations.order_by(Conversation.updated_at.desc())).all()
        message_counts = dict(
            session.execute(
                select(Message.conversation_id, func.count(Message.id))
                .where(Message.conversation_id.in_([row.id for row in rows] or [""]))
                .group_by(Message.conversation_id)
            ).all()
        )
        failed_counts = dict(
            session.execute(
                select(Message.conversation_id, func.count(Message.id))
                .where(
                    Message.conversation_id.in_([row.id for row in rows] or [""]),
                    Message.processing_status == "failed",
                )
                .group_by(Message.conversation_id)
            ).all()
        )
    by_chatbot: dict[str, dict] = {}
    for conversation in rows:
        key = chatbot_key(conversation.source_system, conversation.modality_group)
        entry = by_chatbot.setdefault(
            key,
            {
                "key": key,
                "name": _chatbot_name(conversation.source_system, conversation.modality_group),
                "source_system": conversation.source_system,
                "modality_group": conversation.modality_group,
                "active_sessions": 0,
                "completed_sessions": 0,
                "total_messages": 0,
                "failed_requests": 0,
                "average_response_time_ms": None,
                "most_recent_activity_at": None,
            },
        )
        if conversation.status == "completed":
            entry["completed_sessions"] += 1
        else:
            entry["active_sessions"] += 1
        entry["total_messages"] += message_counts.get(conversation.id, 0)
        entry["failed_requests"] += failed_counts.get(conversation.id, 0)
        entry["most_recent_activity_at"] = max(
            filter(None, [entry["most_recent_activity_at"], _iso_timestamp(conversation.updated_at)]),
            default=None,
        )
    _attach_average_response_times(by_chatbot)
    return {
        "chatbots": sorted(by_chatbot.values(), key=lambda item: item["name"]),
        "updated_at": _iso_timestamp(utc_now()),
    }


def search_sessions(user: AdminUser, filters: dict) -> list[dict]:
    allowed = get_accessible_chatbot_keys(user)
    with session_scope() as session:
        query = (
            _allowed_conversations_query(allowed)
            .join(Participant)
            .order_by(Conversation.updated_at.desc())
        )
        query = _apply_conversation_filters(query, filters)
        rows = session.scalars(query.limit(250)).all()
        conversation_ids = [row.id for row in rows]
        message_counts = dict(
            session.execute(
                select(Message.conversation_id, func.count(Message.id))
                .where(Message.conversation_id.in_(conversation_ids or [""]))
                .group_by(Message.conversation_id)
            ).all()
        )
        failed_counts = dict(
            session.execute(
                select(Message.conversation_id, func.count(Message.id))
                .where(
                    Message.conversation_id.in_(conversation_ids or [""]),
                    Message.processing_status == "failed",
                )
                .group_by(Message.conversation_id)
            ).all()
        )
        participants = {row.participant_id: row.participant for row in rows}
    return [
        _session_payload(row, participants.get(row.participant_id), message_counts, failed_counts, user)
        for row in rows
    ]


def search_selection_sessions(user: AdminUser, filters: dict) -> list[dict]:
    allowed = get_accessible_chatbot_keys(user)
    with session_scope() as session:
        query = (
            _allowed_conversations_query(allowed)
            .join(Participant)
            .where(Conversation.source_system == "selection")
        )
        selected_mode = filters.get("selected_mode")
        if selected_mode:
            query = query.where(Conversation.modality_group == selected_mode)
        query = _apply_conversation_filters(query, filters)
        rows = session.scalars(query.order_by(Conversation.updated_at.desc()).limit(500)).all()
        conversation_ids = [row.id for row in rows]
        message_counts = dict(
            session.execute(
                select(Message.conversation_id, func.count(Message.id))
                .where(Message.conversation_id.in_(conversation_ids or [""]))
                .group_by(Message.conversation_id)
            ).all()
        )
        failed_counts = dict(
            session.execute(
                select(Message.conversation_id, func.count(Message.id))
                .where(
                    Message.conversation_id.in_(conversation_ids or [""]),
                    Message.processing_status == "failed",
                )
                .group_by(Message.conversation_id)
            ).all()
        )
        backend_error_counts = dict(
            session.execute(
                select(BackendRequestLog.conversation_id, func.count(BackendRequestLog.id))
                .where(
                    BackendRequestLog.conversation_id.in_(conversation_ids or [""]),
                    BackendRequestLog.status == "failed",
                )
                .group_by(BackendRequestLog.conversation_id)
            ).all()
        )
        participants = {row.participant_id: row.participant for row in rows}
    payloads = [
        _selection_session_payload(
            row,
            participants.get(row.participant_id),
            message_counts.get(row.id, 0),
            failed_counts.get(row.id, 0),
            backend_error_counts.get(row.id, 0),
            user,
        )
        for row in rows
    ]
    return sorted(payloads, key=lambda item: (not item["needs_attention"], item["last_activity_at"] or ""), reverse=False)


def export_selection_sessions_csv(user: AdminUser, filters: dict) -> str:
    if user.role not in EXPORT_ROLES:
        raise PermissionError("This role cannot export data")
    selection_sessions = search_selection_sessions(user, filters)
    conversation_ids = [row["session_id"] for row in selection_sessions]
    with session_scope() as session:
        rows = session.execute(
            select(Message, Conversation)
            .join(Conversation, Message.conversation_id == Conversation.id)
            .where(Message.conversation_id.in_(conversation_ids or [""]))
            .order_by(Message.conversation_id, Message.sequence_number)
        ).all()
    transcript_by_conversation: dict[str, list[str]] = {}
    for message, _conversation in rows:
        transcript_by_conversation.setdefault(message.conversation_id, []).append(
            f"{message.sequence_number}. {message.role}: {message.content}"
        )

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "participant_id",
        "session_id",
        "selection_status",
        "selected_mode",
        "selection_reason",
        "selection_reason_timestamp",
        "selection_reason_status",
        "handoff_status",
        "message_count",
        "failure_count",
        "backend_error_count",
        "needs_attention",
        "status_tags",
        "start_time",
        "end_time",
        "duration_seconds",
        "last_activity_time",
        "conversation_transcript",
    ])
    for row in selection_sessions:
        writer.writerow([
            row["participant_id"],
            row["session_id"],
            row["selection_status"],
            row["selected_mode"],
            row["selection_reason"],
            row["selection_reason_timestamp"],
            row["selection_reason_status"],
            row["handoff_status"],
            row["message_count"],
            row["failure_count"],
            row["backend_error_count"],
            "true" if row["needs_attention"] else "false",
            "|".join(row["status_tags"]),
            row["start_time"],
            row["end_time"],
            row["duration_seconds"],
            row["last_activity_at"],
            "\n".join(transcript_by_conversation.get(row["session_id"], [])),
        ])
    return output.getvalue()


def search_interview_sessions(user: AdminUser, filters: dict) -> list[dict]:
    allowed = get_accessible_chatbot_keys(user)
    with session_scope() as session:
        query = (
            _allowed_conversations_query(allowed)
            .join(Participant)
            .where(Conversation.modality_group.in_(["voice", "keyboard"]))
        )
        chatbot_type = filters.get("chatbot_type")
        if chatbot_type in {"voice", "keyboard"}:
            query = query.where(Conversation.modality_group == chatbot_type)
        input_method = filters.get("input_method")
        query = _apply_conversation_filters(query, filters)
        rows = session.scalars(query.order_by(Conversation.updated_at.desc()).limit(500)).all()
        conversation_ids = [row.id for row in rows]
        messages = session.scalars(
            select(Message)
            .where(Message.conversation_id.in_(conversation_ids or [""]))
            .order_by(Message.conversation_id, Message.sequence_number)
        ).all()
        logs = session.scalars(
            select(BackendRequestLog)
            .where(BackendRequestLog.conversation_id.in_(conversation_ids or [""]))
            .order_by(BackendRequestLog.created_at)
        ).all()
        participants = {row.participant_id: row.participant for row in rows}
    messages_by_conversation: dict[str, list[Message]] = {}
    for message in messages:
        if input_method and message.input_method and message.input_method != input_method:
            continue
        messages_by_conversation.setdefault(message.conversation_id, []).append(message)
    logs_by_conversation: dict[str, list[BackendRequestLog]] = {}
    for log in logs:
        if log.conversation_id:
            logs_by_conversation.setdefault(log.conversation_id, []).append(log)
    payloads = [
        _interview_session_payload(
            row,
            participants.get(row.participant_id),
            messages_by_conversation.get(row.id, []),
            logs_by_conversation.get(row.id, []),
            user,
        )
        for row in rows
    ]
    payloads = _apply_interview_payload_filters(payloads, filters)
    return sorted(payloads, key=_interview_sort_key)


def export_interview_sessions_csv(user: AdminUser, filters: dict) -> str:
    if user.role not in EXPORT_ROLES:
        raise PermissionError("This role cannot export data")
    sessions = search_interview_sessions(user, filters)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "participant_id",
        "session_id",
        "chatbot_type",
        "source_system",
        "status",
        "progress",
        "last_completed_question",
        "last_node",
        "last_speaker",
        "message_count",
        "user_message_count",
        "assistant_message_count",
        "failure_count",
        "backend_error_count",
        "average_latency_ms",
        "median_latency_ms",
        "start_time",
        "end_time",
        "duration_seconds",
        "last_activity_time",
        "needs_attention",
        "status_tags",
        "voice_raw_transcripts",
        "stored_user_messages",
        "conversation_transcript",
    ])
    for session in sessions:
        writer.writerow([
            session["participant_id"],
            session["session_id"],
            session["chatbot_type"],
            session["source_system"],
            session["status"],
            session["progress_label"],
            session["last_completed_question"],
            session["last_node"],
            session["last_speaker"],
            session["message_count"],
            session["user_message_count"],
            session["assistant_message_count"],
            session["failure_count"],
            session["backend_error_count"],
            session["average_latency_ms"],
            session["median_latency_ms"],
            session["start_time"],
            session["end_time"],
            session["duration_seconds"],
            session["last_activity_at"],
            "true" if session["needs_attention"] else "false",
            "|".join(session["status_tags"]),
            "\n".join(session["voice_raw_transcripts"]),
            "\n".join(session["stored_user_messages"]),
            session["conversation_transcript"],
        ])
    return output.getvalue()


def get_conversation_detail(user: AdminUser, conversation_id: str) -> dict:
    allowed = get_accessible_chatbot_keys(user)
    with session_scope() as session:
        conversation = session.scalar(
            _allowed_conversations_query(allowed).where(Conversation.id == conversation_id)
        )
        if not conversation:
            raise PermissionError("Conversation not found or not authorized")
        participant = session.get(Participant, conversation.participant_id)
        messages = session.scalars(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.sequence_number)
        ).all()
        logs = session.scalars(
            select(BackendRequestLog)
            .where(BackendRequestLog.conversation_id == conversation_id)
            .order_by(BackendRequestLog.created_at)
        ).all()
    return {
        "session": _session_payload(conversation, participant, {}, {}, user),
        "selection_summary": (
            _selection_session_payload(
                conversation,
                participant,
                len(messages),
                len([message for message in messages if message.processing_status == "failed"]),
                len([log for log in logs if log.status == "failed"]),
                user,
            )
            if conversation.source_system == "selection"
            else None
        ),
        "interview_summary": (
            _interview_session_payload(conversation, participant, messages, logs, user)
            if conversation.modality_group in {"voice", "keyboard"}
            else None
        ),
        "messages": [_message_payload(message, user) for message in messages],
        "request_logs": [_request_log_payload(log) for log in logs],
    }


def record_admin_audit(
    user_id: Optional[str],
    action: str,
    resource_type: Optional[str] = None,
    resource_id: Optional[str] = None,
    metadata: Optional[dict] = None,
) -> None:
    with session_scope() as session:
        session.add(
            AdminAuditLog(
                user_id=user_id,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                metadata_json=json.dumps(metadata or {}),
            )
        )


def record_backend_step(
    step: str,
    status: str,
    conversation_id: Optional[str] = None,
    message_id: Optional[str] = None,
    client_message_id: Optional[str] = None,
    participant_key: Optional[str] = None,
    detail: Optional[str] = None,
    metadata: Optional[dict] = None,
) -> None:
    with session_scope() as session:
        session.add(
            BackendRequestLog(
                conversation_id=conversation_id,
                message_id=message_id,
                client_message_id=client_message_id,
                participant_key=participant_key,
                step=step,
                status=status,
                detail=detail,
                metadata_json=json.dumps(metadata or {}),
            )
        )


def export_messages_csv(user: AdminUser, filters: dict) -> str:
    if user.role not in EXPORT_ROLES:
        raise PermissionError("This role cannot export data")
    sessions = search_sessions(user, filters)
    allowed_conversation_ids = [session["session_id"] for session in sessions]
    with session_scope() as session:
        rows = session.execute(
            select(Message, Conversation, Participant)
            .join(Conversation, Message.conversation_id == Conversation.id)
            .join(Participant, Conversation.participant_id == Participant.id)
            .where(Message.conversation_id.in_(allowed_conversation_ids or [""]))
            .order_by(Conversation.updated_at.desc(), Message.sequence_number)
        ).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "chatbot_key",
        "chatbot_name",
        "session_id",
        "participant_id",
        "conversation_status",
        "selection_reason",
        "modality_selected_client_at",
        "selection_reason_client_at",
        "sequence_number",
        "role",
        "content",
        "raw_user_input",
        "raw_transcript",
        "input_method",
        "request_status",
        "response_status",
        "error_status",
        "client_message_id",
        "client_created_at",
        "server_received_at",
        "processing_completed_at",
        "latency_ms",
        "model_api_info",
        "prompt_version",
    ])
    for message, conversation, participant in rows:
        metadata = _json_dict(message.metadata_json)
        key = chatbot_key(conversation.source_system, conversation.modality_group)
        writer.writerow([
            key,
            _chatbot_name(conversation.source_system, conversation.modality_group),
            conversation.id,
            _participant_label(participant, user),
            conversation.status,
            conversation.selection_reason,
            _iso_timestamp(conversation.modality_selected_client_at),
            _iso_timestamp(conversation.selection_reason_client_at),
            message.sequence_number,
            message.role,
            message.content,
            message.raw_user_input or "",
            message.raw_transcript or "",
            message.input_method or "",
            message.processing_status,
            "returned" if message.role == "assistant" else message.processing_status,
            "true" if message.processing_status == "failed" else "false",
            message.client_message_id or "",
            _iso_timestamp(message.client_created_at),
            _iso_timestamp(message.server_received_at),
            _iso_timestamp(message.processing_completed_at),
            metadata.get("response_time_ms", ""),
            json.dumps({
                "response_to_node_id": metadata.get("response_to_node_id"),
                "question_index": metadata.get("question_index"),
                "progress": metadata.get("progress"),
            }),
            metadata.get("prompt_version") or metadata.get("question_index") or "",
        ])
    return output.getvalue()


def list_audit_logs(user: AdminUser) -> list[dict]:
    if user.role != "admin":
        raise PermissionError("Only admins can view audit logs")
    with session_scope() as session:
        logs = session.scalars(
            select(AdminAuditLog).order_by(AdminAuditLog.created_at.desc()).limit(200)
        ).all()
    return [
        {
            "id": log.id,
            "user_id": log.user_id,
            "action": log.action,
            "resource_type": log.resource_type,
            "resource_id": log.resource_id,
            "created_at": _iso_timestamp(log.created_at),
            "metadata": _json_dict(log.metadata_json),
        }
        for log in logs
    ]


def _allowed_conversations_query(allowed_keys: Optional[set[str]]):
    query = select(Conversation)
    if allowed_keys is not None:
        if not allowed_keys:
            return query.where(False)
        conditions = []
        for key in allowed_keys:
            if ":" not in key:
                continue
            source_system, modality_group = key.split(":", 1)
            conditions.append(
                (Conversation.source_system == source_system)
                & (Conversation.modality_group == modality_group)
            )
        query = query.where(or_(*conditions) if conditions else False)
    return query


def _apply_conversation_filters(query, filters: dict):
    chatbot = filters.get("chatbot_key")
    if chatbot and ":" in chatbot:
        source_system, modality_group = chatbot.split(":", 1)
        query = query.where(
            Conversation.source_system == source_system,
            Conversation.modality_group == modality_group,
        )
    session_id = (filters.get("session_id") or "").strip()
    if session_id:
        query = query.where(Conversation.id.contains(session_id))
    participant_id = (filters.get("participant_id") or "").strip()
    if participant_id:
        query = query.where(Participant.participant_id.contains(participant_id))
    status = filters.get("completion_status")
    if status in {"completed", "in_progress"}:
        query = query.where(Conversation.status == status)
    start = parse_client_timestamp(filters.get("date_start"))
    end = parse_client_timestamp(filters.get("date_end"))
    if start:
        query = query.where(Conversation.updated_at >= start)
    if end:
        query = query.where(Conversation.updated_at <= end)
    return query


def _selection_session_payload(
    conversation: Conversation,
    participant: Optional[Participant],
    message_count: int,
    failure_count: int,
    backend_error_count: int,
    user: AdminUser,
) -> dict:
    selected_mode = conversation.modality_group or ""
    reason = conversation.selection_reason or ""
    reason_present = bool(reason.strip())
    selected_mode_present = selected_mode in {"voice", "keyboard"}
    handoff_completed = selected_mode_present and message_count > 0
    has_error = failure_count > 0 or backend_error_count > 0
    start_time = conversation.modality_selected_client_at or conversation.created_at
    end_time = conversation.selection_reason_client_at or conversation.completed_at
    selection_completed = selected_mode_present and reason_present and handoff_completed
    tags = ["selection_completed" if selection_completed else "selection_in_progress"]
    tags.append("selection_reason_present" if reason_present else "missing_selection_reason")
    if not selected_mode_present:
        tags.append("missing_selected_mode")
    tags.append("handoff_completed" if handoff_completed else "handoff_failed")
    if message_count < 3:
        tags.append("low_message_count")
    if has_error:
        tags.append("has_error")
    if _is_stalled(conversation):
        tags.append("selection_stalled")
    needs_attention = any(
        tag in set(tags)
        for tag in {
            "missing_selection_reason",
            "missing_selected_mode",
            "handoff_failed",
            "low_message_count",
            "has_error",
            "selection_stalled",
        }
    ) or (conversation.status == "completed" and not selection_completed)
    return {
        "participant_id": _participant_label(participant, user),
        "session_id": conversation.id,
        "short_session_id": _short_id(conversation.id),
        "selection_status": "selection_completed" if selection_completed else "selection_in_progress",
        "conversation_status": conversation.status,
        "selected_mode": selected_mode,
        "selection_reason": _mask_if_needed(reason, user),
        "selection_reason_timestamp": _iso_timestamp(conversation.selection_reason_client_at),
        "selection_reason_status": "present" if reason_present else "missing",
        "handoff_status": "handoff_completed" if handoff_completed else "handoff_failed",
        "message_count": message_count,
        "failure_count": failure_count,
        "backend_error_count": backend_error_count,
        "needs_attention": needs_attention,
        "status_tags": tags,
        "start_time": _iso_timestamp(start_time),
        "end_time": _iso_timestamp(end_time),
        "duration_seconds": _duration_seconds(start_time, end_time),
        "last_activity_at": _iso_timestamp(conversation.updated_at),
    }


def _interview_session_payload(
    conversation: Conversation,
    participant: Optional[Participant],
    messages: list[Message],
    logs: list[BackendRequestLog],
    user: AdminUser,
) -> dict:
    user_messages = [message for message in messages if message.role == "user"]
    assistant_messages = [message for message in messages if message.role == "assistant"]
    failed_messages = [message for message in messages if message.processing_status == "failed"]
    backend_errors = [log for log in logs if log.status == "failed"]
    latencies = []
    progress_values = []
    last_question = ""
    last_node = ""
    for message in user_messages:
        metadata = _json_dict(message.metadata_json)
        try:
            latencies.append(int(metadata.get("response_time_ms")))
        except (TypeError, ValueError):
            pass
        progress = metadata.get("progress")
        if isinstance(progress, int):
            progress_values.append(progress)
        elif isinstance(progress, str) and progress.isdigit():
            progress_values.append(int(progress))
        if metadata.get("question_index"):
            last_question = metadata["question_index"]
        if metadata.get("response_to_node_id"):
            last_node = metadata["response_to_node_id"]
    last_message = messages[-1] if messages else None
    start_time = conversation.created_at
    end_time = conversation.completed_at
    tags = [conversation.status if conversation.status == "completed" else "in_progress"]
    if conversation.modality_group == "voice":
        tags.append("voice_session")
    if conversation.modality_group == "keyboard":
        tags.append("keyboard_session")
    has_error = bool(failed_messages or backend_errors)
    if has_error:
        tags.extend(["failed", "has_error"])
    if _is_stalled(conversation):
        tags.append("stalled")
    if len(messages) < 6:
        tags.append("low_message_count")
    if user_messages and len(assistant_messages) == 0:
        tags.append("missing_assistant_response")
    if assistant_messages and len(user_messages) == 0 and conversation.status != "completed":
        tags.append("missing_user_response")
    voice_transcript_missing = (
        conversation.modality_group == "voice"
        and any(not (message.raw_transcript or "").strip() for message in user_messages)
    )
    if voice_transcript_missing:
        tags.append("voice_transcript_missing")
    voice_transcript_error = (
        conversation.modality_group == "voice"
        and any(message.processing_status == "failed" for message in user_messages)
    )
    if voice_transcript_error:
        tags.append("voice_transcript_error")
    keyboard_short = (
        conversation.modality_group == "keyboard"
        and any(len((message.raw_user_input or message.content or "").strip()) < 5 for message in user_messages)
    )
    if keyboard_short:
        tags.append("very_short_response")
    if latencies and max(latencies) >= 30000:
        tags.append("long_latency")
    progress_max = max(progress_values) if progress_values else None
    progress_label = f"Question {progress_max} / 24" if progress_max else ""
    transcript = "\n".join(
        f"{message.sequence_number}. {message.role} [{message.processing_status}] {message.content}"
        for message in messages
    )
    needs_attention = any(
        tag in set(tags)
        for tag in {
            "failed",
            "has_error",
            "stalled",
            "long_latency",
            "low_message_count",
            "missing_user_response",
            "missing_assistant_response",
            "voice_transcript_missing",
            "voice_transcript_error",
            "very_short_response",
        }
    )
    return {
        "participant_id": _participant_label(participant, user),
        "session_id": conversation.id,
        "short_session_id": _short_id(conversation.id),
        "chatbot_type": conversation.modality_group,
        "source_system": conversation.source_system,
        "status": conversation.status,
        "progress": progress_max,
        "progress_label": progress_label,
        "last_completed_question": last_question,
        "last_node": last_node,
        "last_speaker": last_message.role if last_message else "",
        "message_count": len(messages),
        "user_message_count": len(user_messages),
        "assistant_message_count": len(assistant_messages),
        "failure_count": len(failed_messages),
        "backend_error_count": len(backend_errors),
        "error_status": "has_error" if has_error else "ok",
        "average_latency_ms": round(sum(latencies) / len(latencies)) if latencies else None,
        "median_latency_ms": round(median(latencies)) if latencies else None,
        "input_method": conversation.modality_group,
        "needs_attention": needs_attention,
        "status_tags": tags,
        "start_time": _iso_timestamp(start_time),
        "end_time": _iso_timestamp(end_time),
        "duration_seconds": _duration_seconds(start_time, end_time or conversation.updated_at),
        "last_activity_at": _iso_timestamp(conversation.updated_at),
        "voice_raw_transcripts": [
            _mask_if_needed(message.raw_transcript, user)
            for message in user_messages
            if message.raw_transcript
        ],
        "stored_user_messages": [
            _mask_if_needed(message.content, user)
            for message in user_messages
        ],
        "conversation_transcript": _mask_if_needed(transcript, user),
    }


def _apply_interview_payload_filters(payloads: list[dict], filters: dict) -> list[dict]:
    if filters.get("has_failures") == "true":
        payloads = [row for row in payloads if row["failure_count"] > 0 or row["backend_error_count"] > 0]
    if filters.get("stalled_only") == "true":
        payloads = [row for row in payloads if "stalled" in row["status_tags"]]
    if filters.get("low_message_count") == "true":
        payloads = [row for row in payloads if "low_message_count" in row["status_tags"]]
    if filters.get("long_latency") == "true":
        payloads = [row for row in payloads if "long_latency" in row["status_tags"]]
    return payloads


def _interview_sort_key(row: dict):
    priority = 0
    tags = set(row["status_tags"])
    if {"failed", "has_error"} & tags:
        priority = 4
    elif "stalled" in tags:
        priority = 3
    elif row["status"] == "in_progress":
        priority = 2
    elif row["status"] == "completed":
        priority = 1
    return (-priority, row["last_activity_at"] or "")


def _session_payload(
    conversation: Conversation,
    participant: Optional[Participant],
    message_counts: dict[str, int],
    failed_counts: dict[str, int],
    user: AdminUser,
) -> dict:
    return {
        "session_id": conversation.id,
        "chatbot_key": chatbot_key(conversation.source_system, conversation.modality_group),
        "chatbot_name": _chatbot_name(conversation.source_system, conversation.modality_group),
        "participant_id": _participant_label(participant, user),
        "source_system": conversation.source_system,
        "modality_group": conversation.modality_group,
        "status": conversation.status,
        "selection_reason": conversation.selection_reason,
        "modality_selected_client_at": _iso_timestamp(conversation.modality_selected_client_at),
        "selection_reason_client_at": _iso_timestamp(conversation.selection_reason_client_at),
        "questions_answered": conversation.questions_answered,
        "message_count": message_counts.get(conversation.id, 0),
        "failed_requests": failed_counts.get(conversation.id, 0),
        "created_at": _iso_timestamp(conversation.created_at),
        "updated_at": _iso_timestamp(conversation.updated_at),
        "completed_at": _iso_timestamp(conversation.completed_at),
    }


def _message_payload(message: Message, user: AdminUser) -> dict:
    metadata = _json_dict(message.metadata_json)
    return {
        "id": message.id,
        "sequence_number": message.sequence_number,
        "role": message.role,
        "content": _mask_if_needed(message.content, user),
        "raw_user_input": _mask_if_needed(message.raw_user_input, user),
        "raw_transcript": _mask_if_needed(message.raw_transcript, user),
        "input_method": message.input_method,
        "client_message_id": message.client_message_id,
        "client_created_at": _iso_timestamp(message.client_created_at),
        "server_received_at": _iso_timestamp(message.server_received_at),
        "processing_completed_at": _iso_timestamp(message.processing_completed_at),
        "processing_status": message.processing_status,
        "latency_ms": metadata.get("response_time_ms"),
        "prompt_version": metadata.get("prompt_version") or metadata.get("question_index"),
        "model_api_info": {
            "response_to_node_id": metadata.get("response_to_node_id"),
            "question_index": metadata.get("question_index"),
            "progress": metadata.get("progress"),
        },
    }


def _request_log_payload(log: BackendRequestLog) -> dict:
    return {
        "id": log.id,
        "message_id": log.message_id,
        "client_message_id": log.client_message_id,
        "step": log.step,
        "status": log.status,
        "detail": log.detail,
        "created_at": _iso_timestamp(log.created_at),
        "metadata": _json_dict(log.metadata_json),
    }


def _attach_average_response_times(by_chatbot: dict[str, dict]) -> None:
    if not by_chatbot:
        return
    with session_scope() as session:
        rows = session.execute(
            select(Message.metadata_json, Conversation.source_system, Conversation.modality_group)
            .join(Conversation, Message.conversation_id == Conversation.id)
            .where(Message.role == "user", Message.metadata_json.is_not(None))
        ).all()
    totals: dict[str, list[int]] = {}
    for metadata_json, source_system, modality_group in rows:
        metadata = _json_dict(metadata_json)
        value = metadata.get("response_time_ms")
        try:
            value = int(value)
        except (TypeError, ValueError):
            continue
        key = chatbot_key(source_system, modality_group)
        if key in by_chatbot:
            totals.setdefault(key, []).append(value)
    for key, values in totals.items():
        if values:
            by_chatbot[key]["average_response_time_ms"] = round(sum(values) / len(values))


def _participant_label(participant: Optional[Participant], user: AdminUser) -> str:
    if not participant:
        return ""
    if user.role in UNMASKED_ROLES:
        return participant.participant_id
    digest = hashlib_sha(participant.participant_id)
    return f"masked-{digest[:10]}"


def _mask_if_needed(value: Optional[str], user: AdminUser) -> str:
    if not value:
        return ""
    return value if user.role in UNMASKED_ROLES else "[masked for viewer role]"


def _short_id(value: str) -> str:
    return f"{value[:8]}...{value[-4:]}" if value and len(value) > 14 else value


def _duration_seconds(start: Optional[datetime], end: Optional[datetime]) -> Optional[int]:
    if not start or not end:
        return None
    if start.tzinfo is None:
        start = start.replace(tzinfo=timezone.utc)
    if end.tzinfo is None:
        end = end.replace(tzinfo=timezone.utc)
    return max(0, round((end - start).total_seconds()))


def _is_stalled(conversation: Conversation) -> bool:
    if conversation.status == "completed":
        return False
    updated_at = conversation.updated_at
    if updated_at.tzinfo is None:
        updated_at = updated_at.replace(tzinfo=timezone.utc)
    return (utc_now() - updated_at).total_seconds() > 30 * 60


def hashlib_sha(value: str) -> str:
    import hashlib

    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _chatbot_name(source_system: str, modality_group: str) -> str:
    return f"{source_system.title()} / {modality_group.title()}"


def _json_dict(value: Optional[str]) -> dict:
    if not value:
        return {}
    try:
        parsed = json.loads(value)
        return parsed if isinstance(parsed, dict) else {}
    except json.JSONDecodeError:
        return {}


def _iso_timestamp(value: Optional[datetime]) -> Optional[str]:
    if value is None:
        return None
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
