import { useState, useEffect } from "react";
import iconJob from "../assets/icons/context_job.svg";
import iconFamily from "../assets/icons/context_family.svg";
import { useNavigate } from "react-router-dom";

import { notify } from "../components/Toast/Toast";

import { useDispatch, useSelector } from 'react-redux';
import { chatActions } from "../reducers/chatSlicer";


function InputSelectionPage() {
    const dispatch = useDispatch();

    const navigate = useNavigate();
    const [option, setOption] = useState("");

    // user  redux states
    const { uid } = useSelector((state) => state.user);

    // redirect if user info is empty
    useEffect(() => {
        if (!uid){
            navigate("/login");
        }
    }, [uid, navigate])



    const nextPage = () => {
        if(!option){
            notify("Please select a option first!", "warning")
        }else{
            dispatch(chatActions.initChattingData());
            dispatch(chatActions.setInputMode(option));
            navigate("/chatbot");
        }
    } 

    const goBack = () => {
        navigate("/");
    }


    return ( 
        <div className="bg h-screen min-h-[640px]  w-full min-w-[900px]">
            <div className="w-full h-full max-w-[1240px] min-w-[900px] mx-auto flex flex-col justify-around p-16 items-center relative">
                <div className="text-h2 font-bold">Select a way to chat!</div>

                <div className="flex flex-row justify-between w-[840px]">
                    <button className={`selction-card ${option==="keyboard" ? "selected-option": ""}`} onClick={() => setOption("keyboard")}>
                        <img src={iconJob} alt="jon" className="w-32 h-32"></img>
                        <div className="text-h4 font-semibold  mt-[-12px]">Keyboard</div>
                       
                    </button>

                    <button className={`selction-card ${option==="voice" ? "selected-option": ""}`} onClick={() => setOption("voice")}>
                        <img src={iconFamily} alt="family" className="w-32 h-32"></img>
                        <div className="text-h4 font-semibold mt-[-12px]">Voice</div>
                    </button>
                </div>

                <div className="flex justify-end">
                    <button className="btn btn-black" onClick={nextPage}>Next</button>
                </div>

                <button className="btn btn-black top-right-btn" onClick={goBack}>Back</button>
            </div>

        </div>
     );
}

export default InputSelectionPage;