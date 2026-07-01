# Chatbot Modality

This repository contains the Modality chatbot study app: one FastAPI backend and three React frontends for selection, voice, and keyboard response modes. It is a research data-collection system, so the backend SQL database is the authoritative record for participant identity, assigned question order, submitted responses, timing, audio transcription, interaction events, completion status, and failed or partial submissions.

## Project Structure

```text
fastapi/app/                 Backend API, conversation engine, SQL models, export tools
frontend_selection/          Participant chooses keyboard or voice, then starts chat
frontend_voice/              Direct voice-mode entry point
frontend_keyboard/           Direct keyboard-mode entry point
frontend_admin/              Separate admin monitoring dashboard for leaders
question_preparation/        Question-selection provenance and audit materials
nginx.config                 Production nginx example
test_artifacts/              Generated local audit/export fixtures
```

The active question flow is defined in:

- `fastapi/app/conversation_engine/question_list/codes/selected_questions.py`
- `fastapi/app/conversation_engine/question_list/codes/question_list.py`
- `fastapi/app/conversation_engine/question_list/codes/question_nodes.py`
- `fastapi/app/conversation_engine/question_list/codes/welcome_nodes.py`

## Install And Run

Requirements:

- Python 3.11+
- Node.js 18+
- npm
- ffmpeg
- OpenAI API key
- PostgreSQL 14+ for production, or SQLite for local development

Backend setup:

```bash
cp fastapi/app/.env.example fastapi/app/.env
python -m venv .venv
.venv/bin/pip install -r fastapi/app/requirements.txt
.venv/bin/uvicorn main:app --app-dir fastapi/app --host 127.0.0.1 --port 8000 --reload
```

Backend environment variables:

```text
OPENAI_API_KEY=your_openai_api_key
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3001,http://127.0.0.1:3002,http://127.0.0.1:3003,http://127.0.0.1:3010
DATABASE_URL=sqlite:///./database/chatbot.db
DATA_EXPORT_TOKEN=replace_with_a_long_random_secret
ADMIN_AUTH_SECRET=replace_with_a_different_long_random_secret
```

Use PostgreSQL in production:

```text
DATABASE_URL=postgresql+psycopg://chatbot_user:password@127.0.0.1:5432/chatbot_modality
```

Frontend setup:

```bash
cp frontend_selection/.env.example frontend_selection/.env
cp frontend_voice/.env.example frontend_voice/.env
cp frontend_keyboard/.env.example frontend_keyboard/.env
```

Each frontend `.env` should usually contain:

```text
REACT_APP_BACKEND_HOST=http://127.0.0.1:8000
```

Install and run:

```bash
cd frontend_selection && npm install && PORT=3001 HOST=127.0.0.1 BROWSER=none npm start
cd frontend_voice && npm install && PORT=3002 HOST=127.0.0.1 BROWSER=none npm start
cd frontend_keyboard && npm install && PORT=3003 HOST=127.0.0.1 BROWSER=none npm start
```

Local URLs:

- Selection: `http://127.0.0.1:3001/chatbot/selection`
- Voice: `http://127.0.0.1:3002/chatbot/voice`
- Keyboard: `http://127.0.0.1:3003/chatbot/keyboard`

Admin dashboard:

```bash
cd frontend_admin
python3 -m http.server 3010
```

Open `http://127.0.0.1:3010`. The dashboard connects to `http://127.0.0.1:8000` by default, and the API host can be changed from the dashboard top bar.

## Admin Monitoring Dashboard

The separate `frontend_admin/` app lets project leaders monitor authorized chatbot data without manual database exports.

Admin endpoints are under `/admin/*` and use bearer-token authentication. On first use, open the dashboard and create the first admin account from **First Admin Setup**. After one admin user exists, setup is disabled. Admins can create additional users, assign roles, and grant sub-chatbot access.

Roles:

- `admin`: all sub-chatbots, user/access management, CSV export, audit logs.
- `project_leader`: assigned sub-chatbots, unmasked participant/message data, CSV export.
- `viewer`: assigned sub-chatbots only, masked participant/message data, no CSV export.

Sub-chatbot permission keys use the persisted source and modality fields:

```text
source_system:modality_group
```

Examples include `selection:keyboard`, `selection:voice`, `keyboard:keyboard`, and `voice:voice`.

Dashboard features:

- Overview cards for active sessions, completed sessions, total messages, failed requests, average response time, and most recent activity.
- Near real-time polling every 5 seconds for newly submitted participant messages and backend status changes.
- Session search/filter by sub-chatbot, participant/session ID, date range, completion status, and error status.
- Conversation-level chronological view with user messages, chatbot responses, failed rows, timestamps, prompt/question metadata, latency, and backend request timeline.
- Filtered message-level CSV export from `/admin/export/messages.csv`.
- Audit logging for login, data views, session searches, exports, and access changes.

## Participant Flow

Selection entry flow:

1. Participant logs in with a participant ID.
2. Participant chooses `Keyboard` or `Voice`.
3. Participant explains why they chose that response mode. This is required for `frontend_selection`.
4. Backend creates a participant row if needed, creates a conversation row, randomizes the 24 selected scored questions, and stores the exact assigned `question_sequence`.
5. Nova displays introductory and warm-up prompts. Three warm-up prompts require participant responses before scored questions begin.
6. Nova asks 24 scored open-ended personality questions. Each scored question has stable `question_index` metadata and displayed `progress` from 1 to 24.
7. The answer validator classifies each response as `VALID`, `UNINFORMATIVE`, `NONSENSE`, `NEEDS_CLARIFICATION`, or `DECLINE_CONTINUE`.
8. If a response needs follow-up, the engine asks up to two follow-up prompts for that same displayed question. Follow-up responses retain the same `progress` and `question_index`.
9. After the final scored question, Nova shows the completion message and marks the conversation completed.

Direct voice and keyboard frontends skip the modality-selection reason step and start in their fixed mode.

Important current limitation: this repo does not implement a separate post-survey page or post-survey API. The Home page still contains an inactive survey option. Post-survey answers therefore are not collected by the current working flow.

## Participant-Facing Questions

The current scored question set has 24 stable IDs. New sessions receive these same IDs in randomized order.

| ID | Participant-facing wording |
| --- | --- |
| F1Q3 | Sometimes people adjust what they say because they want others to like them or think well of them. In general, when someone close to you asks for your honest opinion but you suspect being fully honest might make you less likable or less accepted, how do you usually respond? Do you tend to be straightforward, or adjust your words to keep harmony? If it helps, you can share an example that shows what’s most typical for you. |
| F2Q2 | There are situations where people can gain an advantage, like a reward, a better grade, or praise, by bending or breaking rules, especially when the risk of getting caught is low. In general, if you face that kind of situation, how do you usually decide what to do? Do you tend to follow the rules, or sometimes consider breaking them? What usually influences your decision? If it helps, you can share an example that reflects what’s most typical for you. |
| F3Q1 | Sometimes people consider buying something expensive, like luxury clothing, new electronics, or a special experience, even if they don’t really need it. When you face that kind of choice, what usually goes through your mind, and what do you usually decide? If it helps, you can share an example that shows what’s most typical for you. |
| F4Q3 | In settings like school, work, or team projects, people often contribute at different levels. For instance, you might work especially hard and contribute more than most people in the group. In general, if you feel you clearly outperformed others around you, what are your usual thoughts and feelings in that situation? How do you usually respond if others don’t notice your contribution? Does it typically influence how you see yourself or how you behave afterward? If it helps, you can share an example that reflects what’s most typical for you. |
| F5Q1 | Sometimes we need to go somewhere despite unsafe or risky conditions, like driving through a snowstorm, walking alone at night, or traveling during a weather alert. In general, if you face that kind of situation, how much fear do you usually feel, and how does it usually affect what you decide to do? If it helps, you can share an example that shows what’s most typical for you. |
| F6Q1 | Waiting to hear back about something important, like an application, a decision, or news, can make some people anxious. In general, if you are waiting for an outcome and aren’t sure what will happen, what thoughts and feelings do you usually have, and how does it affect what you do? If it helps, you can share an example that shows what’s most typical for you. |
| F7Q2 | Sometimes when people feel anxious or worried, they immediately talk to someone they trust, while others keep it to themselves. If you are feeling anxious or worried, how do you usually respond, do you tend to share it or keep it private? How does that choice usually affect how you feel afterward? Could you share an example that reflects your typical response. |
| F8Q3 | Events like weddings, reunions, or even reflecting on old photos can bring up strong feelings for some people, while others stay more neutral. If you are in a symbolic or nostalgic moment with people you care about, how do you usually feel, do you become strongly moved, or stay more neutral? How does it typically affect your sense of closeness or attachment to others? You can share an example that shows how you usually react in those situations. |
| F9Q2 | After social events, like a conversation, party, or class discussion, some people reflect on how they came across, while others don’t think much about it. When you’ve just been in a group interaction, how often do you think about how you came across to others? How does that usually make you feel about yourself, and does it affect what you say or do afterward? You can share an example that shows how you usually respond. |
| F10Q1 | When meeting someone new, at work, events, or in public, some people start conversations easily, while others feel hesitant. In general, when you meet someone new, how do you usually approach the situation, do you introduce yourself and join in easily, or do you feel more hesitant? How comfortable or nervous do you typically feel, and how does that affect what you do? If you’d like, you can share an example that reflects your usual approach. |
| F11Q1 | People differ in how much they enjoy casual conversation in everyday situations, like waiting in line, sitting next to someone, or meeting new people. In general, what do you usually do in those situations, do you strike up small talk or prefer to keep to yourself? How do you usually feel about it? If you’d like, you can share an example that reflects what feels most natural for you. |
| F12Q1 | People vary in how much energy and enthusiasm they bring to daily life. Some tend to feel upbeat and energized, while others are more low-key or subdued most of the time. In general, thinking about your usual routines, whether at work, school, or in daily life, how would you describe your typical mood and energy level? If you’d like, you can share an example that illustrates what feels most typical for you. |
| F13Q1 | Sometimes people hurt or disappoint us, like a friend letting us down, a colleague taking credit, or someone speaking behind our back. In general, when someone hurts or disappoints you like this, how do you usually respond? Are you more likely to forgive the person and rebuild the relationship, or to hold on to the hurt? What usually influences your decision? If you’d like, you can share an example that reflects what’s most typical for you. |
| F14Q1 | In everyday interactions, people sometimes make mistakes or fall short. In general, when you notice this, how do you usually react, do you tend to be more critical, or more understanding? What do you typically do in response? If you’d like, you can share an example that shows what feels most typical for you. |
| F15Q3 | In group decisions, like making plans or agreeing on how to do something, people sometimes have strong preferences for their own way of doing things. In general, when your preference is different from others’, how do you usually respond, do you hold firm to your way, or are you more willing to go along with the group? You might describe a situation that reflects how you usually handle this. |
| F16Q1 | In daily life, we often face delays or situations that don’t go as planned, like waiting in a long line, a late appointment, or traffic jams. When this happens to you, what usually goes through your mind, how do you feel, and how do you tend to respond, do you stay calm or react in some way? Can you share an example that shows what feels most typical for you? |
| F17Q1 | Some people like to return things to their proper place right after using them, while others naturally leave things out and tidy up later. And some people might feel comfortable with a bit of clutter or even see it as part of their style. In general, during a normal day or week, how do you usually keep track of and maintain order with your things, like notebooks, clothes, bags, or supplies? How do you feel when items are left out of place for a while? Can you share what feels most typical for you? |
| F18Q1 | Some people push themselves to do more than required, even when no one is checking, while others do only what’s needed. When you have a task, like a paper, project, or job, how do you usually decide how much effort to put in? What influences your choice, and how much effort do you typically give? If it helps, you can share an example of a time when you had to decide how much effort to put into something. |
| F19Q3 | In everyday tasks, like writing, formatting, or organizing, people sometimes notice small things that could be improved, such as spacing, punctuation, or alignment. When you notice these kinds of small flaws in your own work, what usually goes through your mind, and how do you usually feel and respond, do you feel a strong need to correct them, or are you comfortable letting small imperfections stay? Feel free to share what reflects your typical style. |
| F20Q1 | Sometimes situations arise that might trigger a strong emotional response, such as feeling provoked, pressured, or taken by surprise. When situations like these happen, do you usually pause to think things through, or act quickly on your impulses? What kinds of thoughts and feelings typically guide your response in those moments? You might describe a situation that reflects how you usually respond. |
| F21Q1 | When you’re in a natural setting, like on a hike, in a park, or looking at a scenic view, how do you usually respond? Do you tend to pause and appreciate it, talk about it, take a photo, or move on without much notice? How do those settings typically make you feel? If you’d like, you can share an example that reflects what’s most typical for you. |
| F22Q2 | People often come across things they don’t fully understand, like a scientific idea, a piece of history, or how something works in daily life. In general, how do you usually react when you find something unfamiliar that catches your attention, such as looking into it, asking questions, or letting it go? If it helps, you can describe an example that reflects your usual response. |
| F23Q2 | When people face a challenge, some stick with familiar solutions, while others try new approaches. When you face a challenge, how do you usually respond, and what tends to guide that choice? Feel free to share an example if one comes to mind. |
| F24Q3 | In conversations or media, we sometimes come across viewpoints or practices that challenge traditional norms or beliefs. How do you usually react when something like that happens? Do you feel open, curious, resistant, offended, or indifferent? What thoughts or emotions typically come up, and how do you tend to respond, by discussing, researching, or letting it go? If it helps, you can share an example that shows what’s most typical for you. |

## Data Recorded

The database schema is created automatically at backend startup. Exported CSV files are one table per file:

- `participants.csv`: internal participant UUID, submitted participant ID, sequential `user_index`, created and last-seen timestamps.
- `conversations.csv`: conversation UUID, participant UUID, modality group, source system, selection reason, client timestamps for modality choice and reason submission, status, question code, randomized `question_sequence`, `questions_answered`, created/updated/completed timestamps.
- `messages.csv`: every assistant and user message with sequence number, role, content, raw user input, raw voice transcript, input method, client message ID, client timestamp, server receive timestamp, processing completion timestamp, processing status, and `metadata_json`.
- `audio_recordings.csv`: uploaded voice file metadata, byte size, SHA-256, raw transcript, upload/transcription timestamps, transcription status, and linked message ID.
- `interaction_events.csv`: click/submit/stop/exit events sent by the frontend, with participant/conversation links when available, page, target, client timestamp, server timestamp, and metadata JSON.
- `participant_question_responses.csv`: analysis-ready derived file with one row per assigned scored question per conversation, explicit `missing_response`, primary and follow-up responses, processing statuses, question order, timing, modality, and completion status.

For scored user responses, `messages.metadata_json` includes:

- `question_index`: stable question ID such as `F11Q1`
- `progress`: displayed question number, 1 through 24
- `response_to_node_id`: exact backend node receiving the response
- `response_started_client_at`: browser timestamp when the answer prompt became available
- `response_time_ms`: browser-measured response time for that turn

Follow-up responses keep the same `question_index` and `progress` as the original scored question. The `response_to_node_id` distinguishes the original response node from follow-up nodes.

## Missing Data And Partial Data

Blank or whitespace-only chat responses are rejected with HTTP 400 and are not silently saved as valid answers. Selection-mode conversations require a nonblank selection reason and valid client timestamps.

When a nonblank user response reaches `/chatbot/chat`, the backend first stores it as `processing_status=pending`. If downstream processing fails, the same row is marked `processing_status=failed`, so the submitted input remains in the database and export. Successful turns are marked `completed`.

Participant stops/exits are recorded as interaction events when the frontend can send them. A conversation that is not completed remains `status=in_progress`, with all recorded messages exported.

## Exporting Data

Command-line export:

```bash
.venv/bin/python fastapi/app/export_sql_data.py --output chatbot-data.zip
```

HTTP export:

```bash
curl \
  -H "X-Export-Token: $DATA_EXPORT_TOKEN" \
  http://127.0.0.1:8000/chatbot/export \
  --output chatbot-data.zip
```

Audit an export:

```bash
.venv/bin/python fastapi/app/audit_data_export.py chatbot-data.zip --report audit-report.json
```

Generate and audit a deterministic fixture:

```bash
.venv/bin/python fastapi/app/generate_data_integrity_fixture.py \
  --output-dir test_artifacts/data-integrity-simulation

.venv/bin/python fastapi/app/audit_data_export.py \
  test_artifacts/data-integrity-simulation.zip \
  --report test_artifacts/data-integrity-simulation/audit-report.json
```

## Testing

Backend:

```bash
.venv/bin/pytest -q fastapi/app/tests
```

Frontend builds:

```bash
cd frontend_selection && npm run build
cd ../frontend_voice && npm run build
cd ../frontend_keyboard && npm run build
```

The backend tests include a deterministic full-flow traversal of the 24 scored questions with a follow-up at displayed question 11. This specifically guards against skipped questions, numbering resets, repeated follow-ups leaking into later questions, and question 11-13 state synchronization errors.

The CRA frontend test command currently finds no tests because the existing `__test__` folders are outside CRA's default test match. Use the build checks above until frontend tests are moved under `src/**/*.test.js` or the test configuration is updated.

## Production Notes

The included `nginx.config` serves:

- Backend API through `/chatbot/api/`
- Frontend builds through `/chatbot/selection`, `/chatbot/voice`, and `/chatbot/keyboard`

For production builds, set:

```text
REACT_APP_BACKEND_HOST=https://your-domain.example/chatbot/api
```

Then rebuild all frontends and deploy their `build/` directories.

Runtime data directories are intentionally ignored by git:

- `fastapi/app/database/`
- `fastapi/app/loggings/`
- uploaded audio files under conversation folders

## Known Limitations

- There is no implemented post-survey workflow in the current repo.
- Interaction logging is best-effort from the frontend; failed interaction-event requests do not block participants.
- Voice transcription depends on the configured OpenAI audio API and browser audio support.
- The app still uses Create React App, which emits a maintenance warning during builds.
