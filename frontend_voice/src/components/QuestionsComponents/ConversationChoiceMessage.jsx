
import { useState } from "react";
import iconPanda from "../../assets/icons/panda-avatar-shadow.svg";



function ConversationChoiceMessage({item, getChoiceNextQuestion}) {
    const [userChoiceIndex, setUserChoiceIndex] = useState("");
    const [userChoiceContent, setUserChoiceContent] = useState("");

    // const handleUserClick = (e) => {
    //     if (item.user_choice){
    //         e.preventDefault();
    //     }else{
    //         setUserChoiceIndex(key);
    //         setUserChoiceContent(value);
    //     }
    // }

    const renderButtonColor = (choiceIndex) => {
        if (item.user_choice && item.user_choice === choiceIndex){
            return "bg-amber-600 hover:bg-amber-600 cursor-default";
        }else if (item.user_choice){
            return "bg-amber-400 hover:bg-amber-400  cursor-default";
        }else if (!item.user_choice && userChoiceIndex === choiceIndex){
            return "bg-amber-600 hover:bg-amber-500";
        }else{
            return "bg-amber-400 hover:bg-amber-500";
        }
    }


    return (
        <div className="conversation-mcq conversation-message message-left-message">
            <div className="message-avatar">
                <img src={iconPanda} alt="a panda"></img>
            </div>


            <div className="flex flex-col items gap-8 conversation-mcq-body">
                <div className="conversation-mcq-question message-body">
                    {item.question}
                </div>
                <div className="conversation-mcq-choices flex flex-col gap-4 w-full items-center">
                    {
                        Object.entries(item.choices).map(([key, value]) => (
                            <button
                                key={key}
                                className={`btn btn-active w-64 border-none ${renderButtonColor(key)}`}
                                onClick={(e) => {
                                    if (item.user_choice){
                                        e.preventDefault();
                                    }else{
                                        setUserChoiceIndex(key);
                                        setUserChoiceContent(value);
                                    }
                                }}

                                // disabled={
                                //     item.user_choice
                                // }
                            >
                                {value}
                            </button>
                        ))
                    }
                </div>

                {
                    !item.user_choice  &&  <button className="btn btn-accent" onClick={() => getChoiceNextQuestion(userChoiceIndex, userChoiceContent)}>Confirm</button>
                }
               

            </div>
            
        </div>
    );
}

export default ConversationChoiceMessage;