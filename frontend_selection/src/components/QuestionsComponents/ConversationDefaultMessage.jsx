import ConversationMessage from "../ConversationPanel/ConversationMessage";

function ConversationDefaultMessage({item}) {
    return ( 
        <ConversationMessage message={{"role":"assistant", "content": item}}></ConversationMessage>
     );
}

export default ConversationDefaultMessage;