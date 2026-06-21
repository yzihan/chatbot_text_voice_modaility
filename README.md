# Chatbot Modality

This repository contains the Modality chatbot study app. It has one FastAPI backend and three React frontends for the supported interaction modes:

- `frontend_selection`: selection entry point at `/chatbot/selection`
- `frontend_voice`: voice entry point at `/chatbot/voice`
- `frontend_keyboard`: keyboard entry point at `/chatbot/keyboard`
- `fastapi/app`: backend API, conversation engine, question flow, and persistence logic

## Project Structure

```text
.
├── fastapi/app/                 # FastAPI backend
│   ├── main.py                  # API routes and app setup
│   ├── conversation_engine/     # Conversation logic and question flow
│   ├── requirements.txt         # Python dependencies
│   └── Final question list - 48.xlsx
├── frontend_selection/          # React app for selection modality
├── frontend_voice/              # React app for voice modality
├── frontend_keyboard/           # React app for keyboard modality
├── nginx.config                 # Production nginx example
└── README.md
```

## Requirements

- Python 3.11+
- Node.js 18+
- npm
- ffmpeg
- OpenAI API key
- PostgreSQL 14+ for production (SQLite is supported for local development)

## Environment Files

Create the backend environment file:

```bash
cp fastapi/app/.env.example fastapi/app/.env
```

Set:

```text
OPENAI_API_KEY=your_openai_api_key
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3001,http://127.0.0.1:3002,http://127.0.0.1:3003
DATABASE_URL=sqlite:///./database/chatbot.db
DATA_EXPORT_TOKEN=replace_with_a_long_random_secret
```

Use PostgreSQL in production:

```text
DATABASE_URL=postgresql+psycopg://chatbot_user:password@127.0.0.1:5432/chatbot_modality
```

Create each frontend environment file:

```bash
cp frontend_selection/.env.example frontend_selection/.env
cp frontend_voice/.env.example frontend_voice/.env
cp frontend_keyboard/.env.example frontend_keyboard/.env
```

For local development, each frontend should use:

```text
REACT_APP_BACKEND_HOST=http://localhost:8000
```

## Backend Setup

```bash
cd fastapi/app
python -m venv ../../.venv
../../.venv/bin/pip install -r requirements.txt
../../.venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

Health check:

```bash
curl http://127.0.0.1:8000/
```

Expected response:

```json
{"message":"Hello Nova!"}
```

The backend creates the SQL schema at startup. The database contains:

- `participants`: participant identity and registration timestamps
- `conversations`: modality, source system, selection reason, and session timestamps
- `messages`: every user and assistant message in sequence
- `audio_recordings`: every uploaded recording, SHA-256 hash, raw transcript, and timestamps

Every new message records a server UTC timestamp. User messages also record the browser timestamp, exact submitted input, input method, and an idempotent client message ID. Voice messages retain both the original transcription and the final edited text.

## Frontend Setup

Install dependencies for each app:

```bash
cd frontend_selection && npm install
cd ../frontend_voice && npm install
cd ../frontend_keyboard && npm install
```

Run locally:

```bash
cd frontend_selection
PORT=3001 HOST=127.0.0.1 BROWSER=none npm start
```

```bash
cd frontend_voice
PORT=3002 HOST=127.0.0.1 BROWSER=none npm start
```

```bash
cd frontend_keyboard
PORT=3003 HOST=127.0.0.1 BROWSER=none npm start
```

Local URLs:

- Selection: `http://127.0.0.1:3001/chatbot/selection`
- Voice: `http://127.0.0.1:3002/chatbot/voice`
- Keyboard: `http://127.0.0.1:3003/chatbot/keyboard`

## Build

Build all frontends before deployment:

```bash
cd frontend_selection && npm run build
cd ../frontend_voice && npm run build
cd ../frontend_keyboard && npm run build
```

## Production Notes

The included `nginx.config` is an example for serving:

- Backend API through `/chatbot/api/`
- Frontend builds through `/chatbot/selection`, `/chatbot/voice`, and `/chatbot/keyboard`

For production, set the frontend environment variable to the public API path before building:

```text
REACT_APP_BACKEND_HOST=https://your-domain.example/chatbot/api
```

Then rebuild the frontends and deploy the generated `build/` directories.

## Runtime Data

The SQL database is the authoritative research data store. The backend also keeps operational conversation-state files so an unfinished conversation can be resumed:

- `fastapi/app/database/`
- `fastapi/app/loggings/`
- uploaded audio files under conversation folders

These files are intentionally ignored by git.

## Exporting Data

Export all SQL tables to a ZIP containing CSV files:

```bash
cd fastapi/app
../../.venv/bin/python export_sql_data.py --output chatbot-data.zip
```

The protected HTTP export endpoint is:

```bash
curl \
  -H "X-Export-Token: $DATA_EXPORT_TOKEN" \
  http://127.0.0.1:8000/chatbot/export \
  --output chatbot-data.zip
```

The ZIP contains `participants.csv`, `conversations.csv`, `messages.csv`, and `audio_recordings.csv`.

## Migrating Legacy File Data

Back up the complete `fastapi/app/database` directory first, then run:

```bash
cd fastapi/app
../../.venv/bin/python migrate_legacy_files.py
```

Legacy message files did not contain per-message timestamps. Migrated timestamps are therefore marked `legacy_inferred` in `messages.timestamp_source`; new timestamps are marked `server`.

## Data Integrity Tests

```bash
../../.venv/bin/pytest -q fastapi/app/tests/test_sql_persistence.py
```

The tests verify raw user input, edited voice text, multiple source recordings, timestamps, duplicate prevention, and CSV export.

Generate a deterministic three-user audit fixture:

```bash
../../.venv/bin/python fastapi/app/generate_data_integrity_fixture.py \
  --output-dir test_artifacts/data-integrity-simulation
```

Audit any exported ZIP independently:

```bash
../../.venv/bin/python fastapi/app/audit_data_export.py \
  test_artifacts/data-integrity-simulation.zip \
  --report test_artifacts/data-integrity-simulation/audit-report.json
```

The fixture covers the selection, voice, and keyboard systems; selection reason timestamps; multiple voice recordings; edited voice text; duplicate submissions; unauthorized exports; and inputs retained after a simulated processing failure.
