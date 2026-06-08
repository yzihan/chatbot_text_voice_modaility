import React from "react";

import iconPanda from "../../assets/icons/devil-avatar-shadow.svg";
import iconVoice from "../../assets/icons/voice_message.svg"

function ConversationMessage({message}) {
    function NewlineText({ text, isVoice }) {
        const newText = text.split('\n').map((item, i) => (
          <React.Fragment key={i}>
            {item}
            {i !== text.split('\n').length - 1 && <br />}
          </React.Fragment>
        ));
      
        return <div className="message-body">{newText}</div>;
      }

    function calculateEmptyLength(){
      const length = Math.ceil(message.duration);

      if (length <= 4){
        return 16;
      }else if (length <= 6){
        return 32;
      }else if(length <= 8){
        return 48;
      }else{
        return 64;
      }
    }


    return ( 
        <div className={`conversation-message ${message.role === "user" ? "message-right-message" : "message-left-message"} ${message.isStreaming ? "message-streaming" : ""}`}>
            {message.role !== "user" &&  (
                <div className="message-avatar">
                    <img src={iconPanda} alt="a panda"></img>
                </div>
            )}
           <div className="message-body-container">
                {/* <div className="message-body">{message.content}</div> */}
                {/* <NewlineText text={message.content} /> */}
                {message.isVoice ? <div className="message-body flex flex-row gap-2 items-center"><div style={{width:`${calculateEmptyLength()}px`}}></div> {`${Math.ceil(message.duration)}" `}<img src={iconVoice} alt="voice" className="h-4"></img></div> : <NewlineText text={message.content} />}
           </div>
            
        </div>
     );
}

export default ConversationMessage;
