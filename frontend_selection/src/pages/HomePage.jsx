import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useDispatch, useSelector } from 'react-redux';

import { notify } from "../components/Toast/Toast";
import { chatActions } from "../reducers/chatSlicer";

import iconChatBot from "../assets/icons/chatbot.svg";
import iconHisory from "../assets/icons/history.svg";
import { userActions } from "../reducers/userSlicer";




function HomePage() {
    const dispatch = useDispatch();
    const navigate = useNavigate();
    const [option, setOption] = useState("");

    // user  redux states
    const { uid} = useSelector((state) => state.user);

    //redirect if user info is empty
    useEffect(() => {
        if (!uid){
            navigate("/login");
        }
    }, [uid, navigate])




    const nextPage = () => {
        if(!option){
            notify("Please select a option first!", "warning")
        }else if(option === "chatbot"){
            dispatch(chatActions.init());
            dispatch(chatActions.initChattingData());
            navigate("/input-select");

            // dispatch(chatActions.initChattingData());
            // dispatch(chatActions.setInputMode(option));
            // navigate("/chatbot");

            // temperaly disable input selection
            // dispatch(chatActions.setInputMode("keyboard"));
            // navigate("/chatbot");
        }else if(option === "survey"){
            notify("We are still working on this page...", "info")
            return;
        }else if(option === "history"){
            navigate("/history");
            return;
        }

    } 


    const logout = () => {
        dispatch(chatActions.init());
        dispatch(userActions.init());
    }


    return ( 
        <div className="bg h-screen min-h-[640px] w-full min-w-[900px]">
            <div className="choice-page w-full h-full max-w-[1240px] min-w-[900px] mx-auto relative">
                <div className="choice-header">
                    <div className="choice-kicker">Modality</div>
                    <div className="choice-title">What would you like to do today?</div>
                </div>

                <div className="choice-grid">
                    <button className={`selction-card ${option==="chatbot" ? "selected-option": ""}`} onClick={() => setOption("chatbot")}>
                        <img src={iconChatBot} alt="chatbot" className="choice-card-icon"></img>
                        <div className="choice-card-title">Start Chat</div>
                        <div className="selection-card-description">Start a new conversation</div>
                    </button>

                    {/* <button className={`selction-card ${option==="survey" ? "selected-option": ""}`} onClick={() => setOption("survey")}>
                        <img src={iconSurvey} alt="survey" className="w-16 h-16"></img>
                        <div className="text-h4 font-semibold mt-[-12px]">Survey</div>
                        <div>Standard click-through questionnaires</div>
                    </button> */}

                    <button className={`selction-card ${option==="history" ? "selected-option": ""}`} onClick={() => setOption("history")}>
                        <img src={iconHisory} alt="history" className="choice-card-icon"></img>
                        <div className="choice-card-title">History</div>
                        <div className="selection-card-description">View or continue past chats</div>
                    </button>

                </div>

                <div className="choice-actions">
                    <button className="btn btn-black choice-primary-btn" onClick={nextPage}>Next</button>
                </div>

                <button className="btn btn-black top-right-btn" onClick={logout}>Logout</button>

            </div>

        </div>
     );
}

export default HomePage;
