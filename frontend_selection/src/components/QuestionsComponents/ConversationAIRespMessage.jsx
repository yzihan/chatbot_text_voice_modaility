import { useState } from "react";
import ConversationMessage from "../ConversationPanel/ConversationMessage";



function ConversationAIRespMessage({item}) {

    return ( 
        <>
            <ConversationMessage message={{"role":"assistant", "content": item.question}}></ConversationMessage>
            {item.user_resp && <ConversationMessage message={{"role":"user", "content": item.user_resp}}></ConversationMessage>}
            {item.ai_resp_to_user_input && <ConversationMessage message={{"role":"assistant", "content": item.ai_resp_to_user_input}}></ConversationMessage>}
        </>
     );
}

export default ConversationAIRespMessage;