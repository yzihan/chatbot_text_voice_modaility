# Chatbot Modality

This repository contains the Psychat chatbot modality study app. It has one FastAPI backend and three React frontends for the supported interaction modes:

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

## Environment Files

Create the backend environment file:

```bash
cp fastapi/app/.env.example fastapi/app/.env
```

Set:

```text
OPENAI_API_KEY=your_openai_api_key
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3001,http://127.0.0.1:3002,http://127.0.0.1:3003
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

The backend creates local runtime files during use:

- `fastapi/app/database/`
- `fastapi/app/loggings/`
- `fastapi/app/user_count.txt`
- uploaded audio files under conversation folders

These files are intentionally ignored by git.
