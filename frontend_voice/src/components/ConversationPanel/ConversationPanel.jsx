import { useRef, useState, useEffect } from "react";
import "./conversation-panel.css";
import SpeechRecognition from 'react-speech-recognition';


import { notify } from "../Toast/Toast";
import { useDispatch, useSelector } from 'react-redux';
import { chatActions } from "../../reducers/chatSlicer";


import ConversationMessage from "./ConversationMessage";
import axios from "axios";
import { chatRouter, newConversationRouter, voiceChatRouter } from "../../API/routers";
import { useNavigate } from "react-router-dom";

import VoiceRecorder from "../VoiceRecorder/VoiceRecorder";
import { motion, AnimatePresence } from "framer-motion";



function ConversationPanel({messages, streamMultipleLines}) {
    const dispatch = useDispatch();
    const navigate = useNavigate();
    // user  redux states
    const { uid, participantID} = useSelector((state) => state.user);
    // redux
    const {interviewID, inputMode, audioFilePath, interviewMessages, loadingText, isMessageLoading, isEnded, totalQuestion, currentProgress} = useSelector((state) => state.chat);
    // useStates
    const [userInput, setUserInput] = useState("");
    const [submittedInput, setSubmittedInput] = useState("");
    // useRef
    const effectRan = useRef(false);  // make usre init only once
    const [submitTrigger, setSubmitTrigger] = useState(false); // trigger for submit user resp to backend
  

    const onStop = async (blob) => {
        const formData = new FormData();
        formData.append('audio', blob, 'recording.webm'); 
        formData.append('uid', uid);
        formData.append('interviewID', interviewID);
        formData.append('participantID', participantID);

        dispatch(chatActions.setIsTranscripting(true));

        axios.post(voiceChatRouter, formData, {
            headers: {
            'Content-Type': 'multipart/form-data'
            }
        })
        .then(response => {
            console.log(response.data);
            if (response.data.transcript === ""){
                setUserInput(" ")
            }else{
                setUserInput(response.data.transcript)
            };
            dispatch(chatActions.setAudioFilePath(response.data.file_path))
        })
        .catch(err => {
            console.log(err);
            const errorMsg =
            err.response?.data?.error ||         // 后端返回的 { error: "something" }
            err.response?.data?.message ||       // 或者 { message: "something" }
            err.message ||                       // axios 自带的错误消息
            'Unkown error';   
            notify(errorMsg, 'error');
        })
        .finally(() => {
            dispatch(chatActions.setIsTranscripting(false));
        });
    };



    // 0. load openning sentences once
    useEffect(() => {
        if (effectRan.current) return; // avoid repeated request
        if(interviewMessages.length > 0) return;


        axios
        .post(newConversationRouter, {
            uid: uid,
            participantID: participantID,
            group: inputMode,
            source: "voice"
        })
        .then((response) => {
            console.log(response.data)
            dispatch(chatActions.setInterviewID(response.data._id));
            streamMultipleLines(response.data.question_data);
        })
        .catch((err) => {
            console.log(err);
            const errorMsg =
            err.response?.data?.error ||         // 后端返回的 { error: "something" }
            err.response?.data?.message ||       // 或者 { message: "something" }
            err.message ||                       // axios 自带的错误消息
             'Unkown error';   
            notify(errorMsg, 'error');
        });

        effectRan.current = true; 
    // eslint-disable-next-line
    }, [uid, participantID, dispatch]);


    const sendUserInput = (e) => {
        e.preventDefault();
        if (!userInput) {
            notify('Please enter your response!', 'warning');
            return;
        }

        dispatch(chatActions.addInterviewMessage({
            role: "user", 
            content: userInput
        }));

        setSubmittedInput(userInput);
        setUserInput('');
        setSubmitTrigger(true); // Trigger useEffect to run after state update
    };


    useEffect(() => {
        if (submitTrigger) {
            console.log("Send input to AI agents.");
            const handleSubmission = async () => {
                try {
                    const response = await axios.post(chatRouter, {
                        interviewID: interviewID,
                        participantID: participantID,
                        user_resp: submittedInput,
                        audioFilepPath: audioFilePath
                    });
    
                    console.log("==================================================================");
                    const data = response.data.question_data;
                    if (Array.isArray(data) && data.length > 0) {
                        const lastItem = data[data.length - 1];
                        const progress = lastItem?.info?.progress;

                        console.log("Progress: ", progress);

                        if (progress) {
                            dispatch(chatActions.setCurrentProgress(progress));
                        }
                    } else {
                        console.log('question_data is empty or not an array');
                    }

                    console.log(response.data);


                    streamMultipleLines(response.data.question_data);  // This runs after streamToLastSection
                    dispatch(chatActions.setIsEnded({isEnded: response.data.is_ending}))
                    console.log(response.data.question_data);
                } catch (err) {
                   console.log(err);
                    const errorMsg =
                    err.response?.data?.error ||         // 后端返回的 { error: "something" }
                    err.response?.data?.message ||       // 或者 { message: "something" }
                    err.message ||                       // axios 自带的错误消息
                    'Unkown error';   
                    notify(errorMsg, 'error');
                } finally {
                    setSubmitTrigger(false);  // Reset the trigger
                    dispatch(chatActions.setAudioFilePath(""));
                }
            };
    
            handleSubmission();  // Call the async function
        }
    }, [audioFilePath, dispatch, interviewID, participantID, streamMultipleLines, submitTrigger, submittedInput]);
    

    const goBack = () => {
        navigate("/")
    }




    const scrollRef = useRef();
    const inputRef = useRef();
    const conversationBodyRef = useRef();

    useEffect(() => {
    const inputHeight = inputRef.current?.offsetHeight || 0;
    if (conversationBodyRef.current) {
        conversationBodyRef.current.style.paddingBottom = `${inputHeight}px`;
    }

    scrollRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages, loadingText, isEnded, isMessageLoading]);




    const renderInputPart = () => {
        if (inputMode === "keyboard"){
            return (
                <div className="conversation-bottom conversation-bottom-keyboard"  id="conversation-bottom">
                    {/* <form className="conversation-input">
                        <textarea
                            placeholder="Send your messages here"
                            value={userInput}
                            onChange={(e) => setUserInput(e.target.value)}
                            rows={2}
                            className="w-full p-2 rounded focus:outline-none  resize-none overflow-y-auto"
                        />
                        <button onClick={(e) => sendUserInput(e)} type="submit">
                            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6">
                                <path strokeLinecap="round" strokeLinejoin="round" d="M6 12 3.269 3.125A59.769 59.769 0 0 1 21.485 12 59.768 59.768 0 0 1 3.27 20.875L5.999 12Zm0 0h7.5" />
                            </svg>
                        </button>
                    </form> */}
                     <AnimatePresence>
                        {(
                        <motion.div
                            initial={{ opacity: 0, height: 0 }}
                            animate={{ opacity: 1, height: "auto" }}
                            exit={{ opacity: 0, height: 0 }}
                            className="bg-white/70 border border-purple-200 rounded-3xl p-4 shadow-sm backdrop-blur-sm"
                        >
                            <textarea 
                                className="text-voice-text leading-relaxed min-h-[2rem] w-full p-2 rounded focus:outline-none  resize-none overflow-y-auto" 
                                placeholder="Send your messages here"               
                                value={userInput}
                                onChange={(e) => setUserInput(e.target.value)}>
                            </textarea>

                            {(
                            <motion.button
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                onClick={sendUserInput}
                                className="mt-3 px-4 py-2 bg-gradient-to-r from-purple-300 to-pink-300 text-purple-800 rounded-2xl text-sm font-medium hover:shadow-md transition-all duration-200 hover:from-purple-400 hover:to-pink-400"
                            >
                                Send Message
                            </motion.button>
                            )}
                        </motion.div>
                        )}
                    </AnimatePresence>
                </div>
            );
        }else if (inputMode === "voice"){
            return <VoiceRecorder 
                        onStop={onStop} 
                        userInput={userInput} 
                        sendUserInput={sendUserInput} 
                        setUserInput={setUserInput}
                    ></VoiceRecorder>
        }
    }


    if (inputMode === "voice" && !SpeechRecognition.browserSupportsSpeechRecognition()) {
        return <p>Your browser does not support speech recognition.</p>;
      }


    return ( 
        <div className="conversation-panel relative">
            <div className="conversation-header text-h5 font-semibold">
                Nova
            </div>

            <span className="conversation-divider"></span>

            <div className="conversation-body" ref={conversationBodyRef}>
                {
                    messages.map((item, i) => {
                        return <ConversationMessage message={item} key={`message-index-${i+1}`}/>
                    })
                   
                }   
                {/* while loading */}
                {isMessageLoading && <ConversationMessage message={{role:"assistant", "content":loadingText}}></ConversationMessage>}


                {/* next button */}
                <div className="h-2"></div>
                <div ref={scrollRef}></div>
            </div>
            
            <div ref={inputRef}>{!isEnded &&  !isMessageLoading && renderInputPart()}</div>
            

            <button className="btn btn-black top-right-btn-chat text-lg" onClick={goBack}>{isEnded ? "Exit" : "Stop"}</button>
            

            {/* <div className="badge badge-dash badge-primary top-left-progress-chat">{`Question: ${currentProgress}/${totalQuestion}` }</div> */}
            <div className="badge badge-info top-left-progress-chat">
                <svg className="size-[1em]" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><g fill="currentColor" strokeLinejoin="miter" strokeLinecap="butt"><circle cx="12" cy="12" r="10" fill="none" stroke="currentColor" strokeLinecap="square" stroke-miterlimit="10" strokeWidth="2"></circle><path d="m12,17v-5.5c0-.276-.224-.5-.5-.5h-1.5" fill="none" stroke="currentColor" strokeLinecap="square" stroke-miterlimit="10" strokeWidth="2"></path><circle cx="12" cy="7.25" r="1.25" fill="currentColor" strokeWidth="2"></circle></g></svg>
                {`Question: ${currentProgress}/${totalQuestion}` }
            </div>
            {/* <div className="top-right-progress-chat ">Progress <progress className="progress progress-info w-56" value={currentProgress} max={totalQuestion}></progress></div> */}
        </div>
     );
}

export default ConversationPanel;
