import imgSection2 from "../assets/imgs/landing-2.png"
import iconStar8 from "../assets/icons/star-8.svg";
import iconStar4 from "../assets/icons/star-4.svg";
import { useNavigate } from "react-router-dom";
import { useState } from "react";
import { useDispatch } from 'react-redux';
import { userActions } from "../reducers/userSlicer";

import { userRouter } from "../API/routers";
import axios from "axios";
import { notify } from "../components/Toast/Toast";

function LoginPage() {
    const navigate = useNavigate();
    const [participantID, setParticipantID] = useState("");

    const dispatch = useDispatch();

    const nextPage = () => {
        if(!participantID){
            notify("UIN ID is required!", "warning")
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
            <div className="w-5/12 flex flex-col gap-8">
                <div className="text-h1 font-bold">Let’s Discover Your Personality!</div>
                <div className="text-h5 font-bold">To make sure you receive the extra credit, please enter your UIN.</div>
                
                <label className="input input-bordered flex items-center gap-8">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" className="w-4 h-4 opacity-70"><path d="M8 8a3 3 0 1 0 0-6 3 3 0 0 0 0 6ZM12.735 14c.618 0 1.093-.561.872-1.139a6.002 6.002 0 0 0-11.215 0c-.22.578.254 1.139.872 1.139h9.47Z" /></svg>
                    <input type="text" className="grow" placeholder="UIN" value={participantID} onChange={(e) => setParticipantID(e.target.value)}/>
                </label>
                <button className="btn btn-black mt-4" onClick={nextPage}>Get Started</button>

                
            </div>
        );
    }
    


    return ( 
        <div className="login-page bg h-screen min-h-[640px]  w-full min-w-[900px]">
            <div className="w-full h-full max-w-[1240px] min-w-[900px] mx-auto flex flex-row gap-16 p-16 items-center">

                {renderForms()}


                <div className="w-[480px] relative aspect-square landing-border">
                    <img src={iconStar8} className="w-[15%] absolute left-[8%] top-[8%]" alt="a star with eight lines"></img>
                    <img src={iconStar4} className="w-[24%] absolute bottom-[3%] right-[3%]" alt="a star with four lines"></img>
                    <div className="w-full h-full rounded-inf p-8 border-landing-section2"><img src={imgSection2} alt="kids are laughing"></img></div>
                </div>

            </div>

        </div>
     );
}

export default LoginPage;