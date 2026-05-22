// speechSlice.js
import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  // transcript: "",
  // isListening: false,
  // startTime: null,
  // duration: 0,
  // transcriptRedux: '', // Add transcript to the initial state
};

const speechSlice = createSlice({
  name: 'speech',
  initialState,
  reducers: {    
    // setIsListening: (state, action) => {
    //   state.isListening = action.payload;
    // },
    // setStartTime: (state, action) => {
    //   state.startTime = action.payload;
    // },
    // setDuration: (state, action) => {
    //   state.duration = action.payload;
    // },
    // setTranscript: (state, action) => {
    //   console.log("trans to redux:", action.payload);
    //   state.transcript = action.payload;
    // },
    // resetTranscript: (state) => {
    //   state.transcript = '';
    // },
    // resetSpeechState: (state) => {
    //   state.sendAudio = false;
    //   // state.startTime = null;
    //   // state.duration = 0;
    //   // state.transcript = ''; // Reset transcript
    // },
  },
});

export const speechActions = speechSlice.actions;

export default speechSlice.reducer;