const configuredHost = process.env.REACT_APP_BACKEND_HOST;
const isLocalHost =
  configuredHost?.includes("localhost") || configuredHost?.includes("127.0.0.1");
const host =
  process.env.NODE_ENV === "production" && (!configuredHost || isLocalHost)
    ? `${window.location.origin}/chatbot/api`
    : configuredHost;


// for user credentials
export const userRouter = `${host}/chatbot/user`;
export const newConversationRouter = `${host}/chatbot/new_conversation`;
export const chatRouter = `${host}/chatbot/chat`;
export const voiceChatRouter = `${host}/chatbot/voice-chat`;
export const historyRouter = `${host}/chatbot/chat_history`;
// for interviews
// export const openningQuestionsRouter = `${host}/chatbot/opening-questions`;
// export const interviewQuestionsRouter = `${host}/chatbot/interview-questions`;
export const interviewHistoryRouter = `${host}/chatbot/load_history_chat`;
