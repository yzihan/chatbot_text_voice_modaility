const host = process.env.REACT_APP_BACKEND_HOST;


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

