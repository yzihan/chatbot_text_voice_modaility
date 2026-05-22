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
        <div className="bg h-screen min-h-[640px]  w-full min-w-[900px]">
            <div className="w-full h-full max-w-[1240px] min-w-[900px] mx-auto flex flex-col justify-around p-16 items-center relative">
                <div className="text-h2 font-bold">How would you like to engage today?</div>

                <div className="flex flex-row justify-between w-[840px]">
                    <button className={`selction-card ${option==="chatbot" ? "selected-option": ""}`} onClick={() => setOption("chatbot")}>
                        <img src={iconChatBot} alt="chabot" className="w-16 h-16"></img>
                        <div className="text-h4 font-semibold  mt-[-12px]">Chatbot</div>
                        <div>Interactive chat for customized, free response</div>
                    </button>

                    {/* <button className={`selction-card ${option==="survey" ? "selected-option": ""}`} onClick={() => setOption("survey")}>
                        <img src={iconSurvey} alt="survey" className="w-16 h-16"></img>
                        <div className="text-h4 font-semibold mt-[-12px]">Survey</div>
                        <div>Standard click-through questionnaires</div>
                    </button> */}

                    <button className={`selction-card ${option==="history" ? "selected-option": ""}`} onClick={() => setOption("history")}>
                        <img src={iconHisory} alt="survey" className="w-16 h-16"></img>
                        <div className="text-h4 font-semibold mt-[-12px]">History</div>
                        <div>View or continue your history chats</div>
                    </button>

                </div>

                <div className="flex justify-end">
                    <button className="btn btn-black text-lg" onClick={nextPage}>Next</button>
                </div>

                <button className="btn btn-black top-right-btn text-lg" onClick={logout}>Logout</button>      
  
            </div>

        </div>
     );
}

export default HomePage;
