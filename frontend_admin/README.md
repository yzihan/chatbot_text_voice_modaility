# Chatbot Admin Dashboard

This is a separate monitoring frontend for project leaders and admins. It reads from the existing FastAPI backend and SQL database; it does not share code or routes with the participant-facing frontends.

## Run Locally

Start the backend first:

```bash
.venv/bin/uvicorn main:app --app-dir fastapi/app --host 127.0.0.1 --port 8000 --reload
```

Serve this static frontend:

```bash
cd frontend_admin
python3 -m http.server 3010
```

Open `http://127.0.0.1:3010`.

Make sure `fastapi/app/.env` includes the admin frontend origin:

```text
CORS_ALLOWED_ORIGINS=http://127.0.0.1:3010
ADMIN_AUTH_SECRET=replace_with_a_long_random_secret
```

## First Admin Setup

1. Open the dashboard.
2. Use **First Admin Setup** to create the first admin account.
3. After setup, use **Log In** with that account.
4. Admin setup is automatically disabled after the first admin user exists.

Passwords are stored as salted PBKDF2 hashes. Login uses signed bearer tokens.

## Roles

- `admin`: can view all sub-chatbots, create users, assign access, export CSVs, and view audit logs.
- `project_leader`: can view and export only assigned sub-chatbots.
- `viewer`: can view only assigned sub-chatbots with participant/message text masked and cannot export.

Sub-chatbot permissions use this key format:

```text
source_system:modality_group
```

Examples:

```text
selection:keyboard
selection:voice
keyboard:keyboard
voice:voice
```

## Monitoring Workflow

The **Overview** page shows per-sub-chatbot progress:

- active sessions
- completed sessions
- total messages
- failed requests
- average response time
- most recent activity time

The dashboard polls the backend every 5 seconds, so new participant messages and request status changes appear near real time.

The **Sessions** page lets leaders filter by:

- sub-chatbot
- participant/session ID
- date range
- completion status
- error status

Selecting a session opens the full conversation history in chronological order. User messages, assistant responses, failed messages, and backend request timeline events are visually separated.

## CSV Export

Use **Export CSV** from the Sessions page after setting filters. The export includes message-level data plus session metadata:

- chatbot key/name
- session ID
- participant ID, masked for roles that require masking
- conversation status
- message role/content
- request/response/error status
- timestamps
- latency
- prompt/model metadata available in `messages.metadata_json`

Exports are audit logged.

## Security Notes

- The dashboard is not public data access. Every `/admin/*` endpoint requires an authenticated bearer token except setup/login.
- Role and sub-chatbot permissions are enforced by backend SQL queries, not only by the browser UI.
- Admin audit logs record login, views, searches, exports, and access changes.
- Viewer role masks participant IDs and message content in dashboard responses.
