import { useNavigate } from "react-router-dom";
import { useState } from "react";
import { useDispatch } from 'react-redux';
import { userActions } from "../reducers/userSlicer";
import AnimatedCatHero from "../components/AnimatedCatHero/AnimatedCatHero";

import { userRouter } from "../API/routers";
import axios from "axios";
import { notify } from "../components/Toast/Toast";

function LoginPage() {
    const navigate = useNavigate();
    const [email, setEmail] = useState("");

    const dispatch = useDispatch();

    const nextPage = () => {
        const participantID = email.trim().toLowerCase();

        if(!participantID){
            notify("University email is required!", "warning")
        }else if(!participantID.endsWith(".illinois.edu")){
            notify("Please use your university email ending with .illinois.edu.", "warning")
        }else{
            axios.post(userRouter, {
                task: "SIGN_IN",
                participantID: participantID,
            })
            .then((response) => {
                console.log(response.data)
                const uid = response.data;
                
                dispatch(userActions.setUserInfo({participantID: participantID, uid: uid}))
            })
            .catch((err) => notify(err.message, "error"));

            setTimeout(() => {
                navigate("/");                
            }, 500);

            
        }
    }



    const renderForms = () => {
        return (                
            <div className="login-card">
                <div className="choice-kicker">Psychat study</div>
                <div className="login-title">Discover your personality through conversation</div>
                <div className="login-copy">Enter your university email ending with .illinois.edu so we can connect your responses with extra credit.</div>

                <label className="login-input">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="w-4 h-4 opacity-70"><path d="M3 4.75A2.75 2.75 0 0 1 5.75 2h8.5A2.75 2.75 0 0 1 17 4.75v10.5A2.75 2.75 0 0 1 14.25 18h-8.5A2.75 2.75 0 0 1 3 15.25V4.75Zm2.75-1.25c-.69 0-1.25.56-1.25 1.25v.47l5.5 3.3 5.5-3.3v-.47c0-.69-.56-1.25-1.25-1.25h-8.5Zm9.75 3.47-5.11 3.07a.75.75 0 0 1-.78 0L4.5 6.97v8.28c0 .69.56 1.25 1.25 1.25h8.5c.69 0 1.25-.56 1.25-1.25V6.97Z" /></svg>
                    <input type="email" className="grow" placeholder="University Email" autoComplete="email" value={email} onChange={(e) => setEmail(e.target.value)}/>
                </label>
                <button className="btn btn-black login-primary-btn" onClick={nextPage}>Begin</button>

                
            </div>
        );
    }
    


    return ( 
        <div className="login-page bg h-screen min-h-[640px] w-full min-w-[900px]">
            <div className="login-shell w-full h-full max-w-[1240px] min-w-[900px] mx-auto">

                {renderForms()}


                <div className="login-visual">
                    <AnimatedCatHero />
                </div>

            </div>

        </div>
     );
}

export default LoginPage;
