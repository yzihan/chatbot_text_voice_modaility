import { configureStore } from '@reduxjs/toolkit';
import userSlicer from './reducers/userSlicer';
import chatSlicer from './reducers/chatSlicer';
import speechSlicer from './reducers/speechSlicer';
import storage from 'redux-persist/lib/storage'; // 使用 localStorage 存储数据
import { persistStore, persistReducer } from 'redux-persist';
import { combineReducers } from 'redux';

const rootReducer = combineReducers({
  user : userSlicer,
  chat: chatSlicer,
  speech: speechSlicer
})

// 配置 persist
const persistConfig = {
  key: 'interest_chatbot',
  storage,
};

// 使用 persistReducer 将持久化配置应用到根 reducer 上
const persistedReducer = persistReducer(persistConfig, rootReducer);


// 创建 store 并忽略非序列化值的检查
const store = configureStore({
  reducer: persistedReducer,
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: ['persist/PERSIST', 'persist/REHYDRATE'],
      },
    }),
});


// 创建 persistor，用于在应用启动时恢复状态
export const persistor = persistStore(store);

export default store;