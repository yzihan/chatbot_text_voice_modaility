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
        <div className="bg h-screen min-h-[640px] w-full min-w-[900px]">
            <div className="choice-page w-full h-full max-w-[1240px] min-w-[900px] mx-auto relative">
                <div className="choice-header">
                    <div className="choice-kicker">Response mode</div>
                    <div className="choice-title">How would you like to respond?</div>
                </div>

                <div className="choice-grid">
                    <button className={`selction-card ${option==="keyboard" ? "selected-option": ""}`} onClick={() => setOption("keyboard")}>
                        <img src={iconJob} alt="keyboard" className="choice-card-icon choice-card-icon-lg"></img>
                        <div className="choice-card-title">Keyboard</div>
                        <div className="selection-card-description">Type your answers</div>
                    </button>

                    <button className={`selction-card ${option==="voice" ? "selected-option": ""}`} onClick={() => setOption("voice")}>
                        <img src={iconFamily} alt="voice" className="choice-card-icon choice-card-icon-lg"></img>
                        <div className="choice-card-title">Voice</div>
                        <div className="selection-card-description">Speak first, then edit the text before sending</div>
                    </button>
                </div>

                <div className="choice-actions">
                    <button className="btn btn-black choice-primary-btn" onClick={nextPage}>Next</button>
                </div>

                <button className="btn btn-black top-right-btn" onClick={goBack}>Back</button>
            </div>

        </div>
     );
}

export default InputSelectionPage;
