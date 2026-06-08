import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useDispatch, useSelector } from "react-redux";

import { notify } from "../components/Toast/Toast";
import { chatActions } from "../reducers/chatSlicer";

function SelectionReasonPage() {
    const dispatch = useDispatch();
    const navigate = useNavigate();
    const [reason, setReason] = useState("");

    const { uid } = useSelector((state) => state.user);
    const { inputMode } = useSelector((state) => state.chat);

    const modeLabel = useMemo(() => {
        if (inputMode === "voice") return "Voice";
        if (inputMode === "keyboard") return "Keyboard";
        return "this option";
    }, [inputMode]);

    useEffect(() => {
        if (!uid) {
            navigate("/login");
            return;
        }

        if (!inputMode) {
            navigate("/input-select");
        }
    }, [uid, inputMode, navigate]);

    const nextPage = () => {
        const trimmedReason = reason.trim();
        if (!trimmedReason) {
            notify("Please briefly tell us why you selected this option.", "warning");
            return;
        }

        dispatch(chatActions.setSelectionReason(trimmedReason));
        navigate("/chatbot");
    };

    const goBack = () => {
        navigate("/input-select");
    };

    return (
        <div className="bg h-screen min-h-[640px] w-full min-w-[900px]">
            <div className="reason-page w-full h-full max-w-[1240px] min-w-[900px] mx-auto relative">
                <section className="reason-card">
                    <div className="choice-kicker">Response mode</div>
                    <h1 className="reason-title">Why did you choose {modeLabel}?</h1>
                    <p className="reason-copy">
                        Please briefly explain what made this response mode feel like the right choice for you today.
                    </p>
                    <textarea
                        className="reason-input"
                        value={reason}
                        onChange={(e) => setReason(e.target.value)}
                        placeholder="Type your reason here"
                        rows={5}
                    />
                    <div className="reason-actions">
                        <button className="btn btn-black reason-secondary-btn" onClick={goBack}>Back</button>
                        <button className="btn btn-black choice-primary-btn" onClick={nextPage}>Next</button>
                    </div>
                </section>
            </div>
        </div>
    );
}

export default SelectionReasonPage;
