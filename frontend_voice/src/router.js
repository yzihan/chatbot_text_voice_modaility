import { BrowserRouter, Routes, Route } from 'react-router-dom';

import LoginPage from './pages/LoginPage';
import ChattingPage from './pages/ChattingPage';
import HomePage from './pages/HomePage';
import HistoryPage from './pages/HistoryPage';
import InputSelectionPage from './pages/InputSelectionPage';


export default function Routers(){  
    return (
        <BrowserRouter basename="/chatbot/voice">
            <Routes>
                <Route path="/" element={<HomePage/>} />
                <Route path="/login" element={<LoginPage/>} />
                <Route path="/chatbot" element={<ChattingPage/>} />
                <Route path="/history" element={<HistoryPage/>} />
                <Route path="/input-select" element={<InputSelectionPage/>} />
                


            </Routes>
        </BrowserRouter>
    )
};