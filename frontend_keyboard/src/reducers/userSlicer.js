import { createSlice } from '@reduxjs/toolkit';

export const userSlice = createSlice({
  name: 'user',
  initialState: {
    // user data
    uid: "",
    participantID: "",
  },
  reducers: {
    init: (state) => {
      state.participantID =  "";
      state.uid =  "";
    },
    setUserInfo: (state, action) => {
      state.participantID = action.payload.participantID;
      state.uid = action.payload.uid;
    },
  }
})



// or
export const  userActions = userSlice.actions;

export default userSlice.reducer