import { createSlice } from '@reduxjs/toolkit'

export const chatSlice = createSlice({
  name: 'chat',
  initialState: {
    //input mode
    // inputMode: "keyboard",  //voice, keyboard
    inputMode: "keyboard",
    audioFilePath: "", //current audio file path in the backend
    audioRecordings: [],

    // data
    interviewID: "",
    interviewMessages: [],


    // chatting message
    isMessageLoading: false,  // for streaming message
    isStreaming: false,   // for streaming message and ...
    loadingText: ".",
    isEnded: false,
    isTranscripting: false,


    // progress
    totalQuestion: 24,
    currentProgress : 0,

  },
  reducers: {
    // set to initial state
    init: (state) => {
        // state.inputMode = "keyboard"; # voice/keyboard
        state.inputMode = "";
        state.audioFilePath = "";
        state.audioRecordings = [];

        state.interviewID = "";
        state.interviewMessages = [];
        state.audioFilePath = "";
        state.audioRecordings = [];

        state.isMessageLoading = false;
        state.isStreaming = false;
        state.loadingText = ".";
        state.isTranscripting = false;
        state.currentProgress = 0;
    },
    // init chat data
    initChattingData: (state) => {
        state.interviewID = "";
        state.interviewMessages = [];
       
        state.isMessageLoading = false;
        state.isStreaming = false;
        state.loadingText = ".";
        state.isTranscripting = false;
        state.currentProgress = 0;
    },
    // set input mode
    setInputMode: (state, action) => {
        state.inputMode = action.payload;
    },
    setAudioFilePath: (state, action) => {
        state.audioFilePath = action.payload;
    },
    addAudioRecording: (state, action) => {
        state.audioRecordings.push(action.payload);
        state.audioFilePath = action.payload.file_path;
    },
    clearAudioRecordings: (state) => {
        state.audioRecordings = [];
        state.audioFilePath = "";
    },
    // for interview data
    setInterviewID: (state, action) => {
        state.interviewID = action.payload;
    },
    addInterviewMessage: (state, action) => {
        state.interviewMessages.push(action.payload)
    },
    addInterviewMessages: (state, action) => {
        state.interviewMessages.push(...action.payload)
    },
    // for chatting messages
    setIsMessageLoading:  (state, action) => {
        state.isMessageLoading = action.payload;
    },
    setIsStreaming:  (state, action) => {
        state.isStreaming = action.payload;
    },
    setLoadingText:  (state, action) => {
        state.loadingText = action.payload;
    },
    setIsTranscripting: (state, action) => {
        state.isTranscripting = action.payload;
    },
    loadHistoryInterviewData: (state, action) => {
        state.interviewID = action.payload.interviewID;
        state.interviewMessages = action.payload.interviewMessages;
        state.isEnded = action.payload.isEnded;
        state.inputMode = action.payload.inputMode;
        console.log("load history interview data,", action.payload);
    },
    setIsEnded: (state, action) => {
        state.isEnded = action.payload.isEnded;
    },
    setCurrentProgress: (state, action) => {
        state.currentProgress = action.payload;
    }
  }
})



export const  chatActions = chatSlice.actions;

export default chatSlice.reducer
