import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useDispatch, useSelector } from 'react-redux';

import { notify } from "../components/Toast/Toast";
import { chatActions } from "../reducers/chatSlicer";
import chatIcon from "../assets/icons/ui-color-2_chat-round.svg";

import axios from "axios";
import { historyRouter, interviewHistoryRouter } from "../API/routers";


function HistoryPage() {
    const dispatch = useDispatch();
    const navigate = useNavigate();
    const [selectedHistory, setSelectedHistory] = useState("");
    const [histories, setHistories] = useState([]);
    // user  redux states
    const { uid, participantID } = useSelector((state) => state.user);

    // redirect if user info is empty
    useEffect(() => {
        if (!uid){
            navigate("/login");
        }
    }, [uid, navigate])


    useEffect(() => {
        axios.post(historyRouter, {
            participantID: participantID,
        })
        .then((response) => {
            console.log(response.data.metadata);
            setHistories(response.data.metadata);
        })
        .catch((err) => notify(err.message, "error"));

    }, [participantID])


    const onClickInterview = (interviewId) => {
        if (interviewId !== selectedHistory){
            setSelectedHistory(interviewId);
        }else{
            setSelectedHistory("");
        }
    }
    


    const nextPage = () => {
        if(!selectedHistory){
            notify("Please select a history first!", "warning")
        }else {
            axios.post(interviewHistoryRouter, {
                participantID: participantID,
                interviewID: selectedHistory
            })
            .then((resp)=>{
                console.log(resp.data);
                dispatch(chatActions.loadHistoryInterviewData({
                    interviewID: selectedHistory,
                    interviewMessages: resp.data.history_messages,
                    isEnded: resp.data.is_ending,
                    inputMode: resp.data.group
                }))
            })
            .then(() => {
                navigate("/chatbot")
            })
            .catch((err) => notify(err.message, 'error'));
      
        }
    } 
   
    function formatToCentralTime(utcTimeString) {
        // Strip microseconds (JavaScript only supports milliseconds)
        const trimmedUtcString = utcTimeString.split('.')[0] + 'Z';
    
        // Create a Date object in UTC
        const utcDate = new Date(trimmedUtcString);
    
        // Format to Central Time using Intl API
        const formatter = new Intl.DateTimeFormat('en-US', {
            timeZone: 'America/Chicago',
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit',
            hour12: false
        });
    
        // Format and reorder date
        const parts = formatter.formatToParts(utcDate);
        const getPart = (type) => parts.find(p => p.type === type)?.value;
    
        return `${getPart('year')}-${getPart('month')}-${getPart('day')} ${getPart('hour')}:${getPart('minute')}`;
    }
    

    const goBack = () => {
        navigate("/");
    }

    return ( 
        <div className="bg h-screen min-h-[640px]  w-full min-w-[900px]">
            <div className="w-full h-full max-w-[1240px] min-w-[900px] mx-auto flex flex-col justify-around p-16 items-center relative">
                <div className="text-h2 font-bold">Check your previous chatbot histories</div>

                <div className="flex flex-col justify-start gap-8 w-[840px] h-[580px] overflow-auto">

                    {histories.map((interview, i) => {
                        return (
                            <button key={`history-${i}`} className={`${interview.session_id === selectedHistory && "bg-history-choosen"} flex flex-row items-center gap-2 h-20 border-yellow-500 border-2 rounded-lg py-2 px-4 text-h5 font-semibold shadow-card-hover hover:cursor-pointer`} onClick={() => onClickInterview(interview.session_id)}>
                                <div className="w-16"><img src={chatIcon} alt="a chat bubble"></img></div>
                                <div className="w-64">{interview.questions_answered} questions answered.</div>
                                <div className="grow text-right">Last updated time: {formatToCentralTime(interview.updated_time)}</div>
                            </button>
                        );
                    })}
                 
                </div>

                <div className="flex justify-end h-[48px]">
                    {selectedHistory && <button className="btn btn-black" onClick={nextPage}>Continue Interview</button>}
                </div>

                <button className="btn btn-black top-right-btn" onClick={goBack}>Back</button>
            </div>

        </div>
     );
}

export default HistoryPage;