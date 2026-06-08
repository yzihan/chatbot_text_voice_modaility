import { BrowserRouter, Routes, Route } from 'react-router-dom';

import LoginPage from './pages/LoginPage';
import ChattingPage from './pages/ChattingPage';
import HomePage from './pages/HomePage';
import HistoryPage from './pages/HistoryPage';
import InputSelectionPage from './pages/InputSelectionPage';
import SelectionReasonPage from './pages/SelectionReasonPage';


export default function Routers(){  
    return (
        <BrowserRouter basename="/chatbot/selection">
            <Routes>
                <Route path="/" element={<HomePage/>} />
                <Route path="/login" element={<LoginPage/>} />
                <Route path="/chatbot" element={<ChattingPage/>} />
                <Route path="/history" element={<HistoryPage/>} />
                <Route path="/input-select" element={<InputSelectionPage/>} />
                <Route path="/selection-reason" element={<SelectionReasonPage/>} />
                


            </Routes>
        </BrowserRouter>
    )
};
