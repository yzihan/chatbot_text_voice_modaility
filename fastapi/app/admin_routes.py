from __future__ import annotations

from datetime import datetime, timezone
import io

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from admin_auth import create_token, get_current_admin, touch_login
from admin_repository import (
    authenticate_admin,
    create_admin_user,
    export_interview_sessions_csv,
    export_messages_csv,
    export_selection_sessions_csv,
    get_conversation_detail,
    get_dashboard_summary,
    has_admin_users,
    list_admin_users,
    list_audit_logs,
    list_chatbots,
    record_admin_audit,
    search_interview_sessions,
    search_selection_sessions,
    search_sessions,
    serialize_admin_user,
    update_user_access,
)
from sql_models import AdminUser


router = APIRouter(prefix="/admin", tags=["admin"])


class BootstrapRequest(BaseModel):
    email: str
    password: str
    display_name: str = ""


class LoginRequest(BaseModel):
    email: str
    password: str


class CreateUserRequest(BaseModel):
    email: str
    password: str
    display_name: str = ""
    role: str = "viewer"
    chatbot_keys: list[str] = []


class UpdateAccessRequest(BaseModel):
    role: str
    chatbot_keys: list[str] = []
    is_active: bool = True


def _filters_from_query(request: Request) -> dict:
    return {
        "chatbot_key": request.query_params.get("chatbot_key"),
        "participant_id": request.query_params.get("participant_id"),
        "session_id": request.query_params.get("session_id"),
        "date_start": request.query_params.get("date_start"),
        "date_end": request.query_params.get("date_end"),
        "completion_status": request.query_params.get("completion_status"),
        "error_status": request.query_params.get("error_status"),
        "selected_mode": request.query_params.get("selected_mode"),
        "chatbot_type": request.query_params.get("chatbot_type"),
        "input_method": request.query_params.get("input_method"),
        "has_failures": request.query_params.get("has_failures"),
        "stalled_only": request.query_params.get("stalled_only"),
        "low_message_count": request.query_params.get("low_message_count"),
        "long_latency": request.query_params.get("long_latency"),
    }


@router.get("/setup/status")
def setup_status():
    return {"has_admin_users": has_admin_users()}


@router.post("/setup/bootstrap")
def bootstrap_admin(payload: BootstrapRequest):
    if has_admin_users():
        raise HTTPException(status_code=409, detail="Admin setup is already complete")
    try:
        user = create_admin_user(
            email=payload.email,
            password=payload.password,
            display_name=payload.display_name,
            role="admin",
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    record_admin_audit(user["id"], "bootstrap_admin", "admin_user", user["id"])
    return {"user": user}


@router.post("/login")
def login(payload: LoginRequest):
    user = authenticate_admin(payload.email, payload.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    touch_login(user.id)
    token = create_token(user)
    record_admin_audit(user.id, "login", "admin_user", user.id)
    return {"token": token, "user": serialize_admin_user(user, include_permissions=True)}


@router.get("/me")
def me(user: AdminUser = Depends(get_current_admin)):
    return {"user": serialize_admin_user(user, include_permissions=True)}


@router.get("/chatbots")
def chatbots(user: AdminUser = Depends(get_current_admin)):
    record_admin_audit(user.id, "view_chatbots", "chatbot")
    return {"chatbots": list_chatbots(user)}


@router.get("/summary")
def summary(user: AdminUser = Depends(get_current_admin)):
    record_admin_audit(user.id, "view_summary", "dashboard")
    return get_dashboard_summary(user)


@router.get("/sessions")
def sessions(request: Request, user: AdminUser = Depends(get_current_admin)):
    filters = _filters_from_query(request)
    rows = search_sessions(user, filters)
    if filters.get("error_status") == "failed":
        rows = [row for row in rows if row["failed_requests"] > 0]
    elif filters.get("error_status") == "ok":
        rows = [row for row in rows if row["failed_requests"] == 0]
    record_admin_audit(user.id, "search_sessions", "conversation", metadata=filters)
    return {"sessions": rows}


@router.get("/selection/sessions")
def selection_sessions(request: Request, user: AdminUser = Depends(get_current_admin)):
    filters = _filters_from_query(request)
    rows = search_selection_sessions(user, filters)
    record_admin_audit(user.id, "search_selection_sessions", "conversation", metadata=filters)
    return {"sessions": rows}


@router.get("/interviews/sessions")
def interview_sessions(request: Request, user: AdminUser = Depends(get_current_admin)):
    filters = _filters_from_query(request)
    rows = search_interview_sessions(user, filters)
    record_admin_audit(user.id, "search_interview_sessions", "conversation", metadata=filters)
    return {"sessions": rows}


@router.get("/sessions/{conversation_id}")
def conversation_detail(conversation_id: str, user: AdminUser = Depends(get_current_admin)):
    try:
        detail = get_conversation_detail(user, conversation_id)
    except PermissionError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    record_admin_audit(user.id, "view_conversation", "conversation", conversation_id)
    return detail


@router.get("/export/messages.csv")
def export_messages(request: Request, user: AdminUser = Depends(get_current_admin)):
    filters = _filters_from_query(request)
    try:
        csv_text = export_messages_csv(user, filters)
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    record_admin_audit(user.id, "export_messages_csv", "message", metadata=filters)
    filename = f"admin-message-export-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.csv"
    return StreamingResponse(
        io.BytesIO(csv_text.encode("utf-8")),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/selection/export.csv")
def export_selection(request: Request, user: AdminUser = Depends(get_current_admin)):
    filters = _filters_from_query(request)
    try:
        csv_text = export_selection_sessions_csv(user, filters)
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    record_admin_audit(user.id, "export_selection_csv", "conversation", metadata=filters)
    filename = f"selection-session-export-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.csv"
    return StreamingResponse(
        io.BytesIO(csv_text.encode("utf-8")),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/interviews/export.csv")
def export_interviews(request: Request, user: AdminUser = Depends(get_current_admin)):
    filters = _filters_from_query(request)
    try:
        csv_text = export_interview_sessions_csv(user, filters)
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    record_admin_audit(user.id, "export_interviews_csv", "conversation", metadata=filters)
    filename = f"interview-session-export-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.csv"
    return StreamingResponse(
        io.BytesIO(csv_text.encode("utf-8")),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/users")
def users(user: AdminUser = Depends(get_current_admin)):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can manage users")
    return {"users": list_admin_users()}


@router.post("/users")
def create_user(payload: CreateUserRequest, user: AdminUser = Depends(get_current_admin)):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can create users")
    try:
        created = create_admin_user(
            email=payload.email,
            password=payload.password,
            display_name=payload.display_name,
            role=payload.role,
            chatbot_keys=payload.chatbot_keys,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    record_admin_audit(user.id, "create_admin_user", "admin_user", created["id"])
    return {"user": created}


@router.put("/users/{user_id}/access")
def update_access(user_id: str, payload: UpdateAccessRequest, user: AdminUser = Depends(get_current_admin)):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can manage access")
    try:
        updated = update_user_access(
            user_id=user_id,
            role=payload.role,
            chatbot_keys=payload.chatbot_keys,
            is_active=payload.is_active,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    record_admin_audit(
        user.id,
        "update_admin_access",
        "admin_user",
        user_id,
        metadata={"role": payload.role, "chatbot_keys": payload.chatbot_keys},
    )
    return {"user": updated}


@router.get("/audit-logs")
def audit_logs(user: AdminUser = Depends(get_current_admin)):
    try:
        logs = list_audit_logs(user)
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    return {"audit_logs": logs}
