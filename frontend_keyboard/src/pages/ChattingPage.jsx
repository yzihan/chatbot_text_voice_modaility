import { useCallback, useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";

import ConversationPanel from "../components/ConversationPanel/ConversationPanel";
import { chatActions } from "../reducers/chatSlicer";

const STREAMING_INTERVAL = 45;
const LOADING_TEXTS = [".", "..", "..."];

function splitIntoStreamChunks(text) {
    return text.match(/\S+\s*/g) || [text];
}

function ChattingPage() {
    const dispatch = useDispatch();
    const { interviewMessages, isMessageLoading, isStreaming } = useSelector((state) => state.chat);
    const [streamingText, setStreamingText] = useState(".");

    useEffect(() => {
        if (!isMessageLoading || isStreaming) {
            return undefined;
        }

        let index = 0;
        const interval = setInterval(() => {
            setStreamingText(LOADING_TEXTS[index]);
            index = (index + 1) % LOADING_TEXTS.length;
        }, 500);

        return () => clearInterval(interval);
    }, [isMessageLoading, isStreaming, dispatch]);

    const streamSingleLine = useCallback((content) => {
        let index = 0;
        let nextText = "";
        const chunks = splitIntoStreamChunks(content.content);

        return new Promise((resolve) => {
            const interval = setInterval(() => {
                if (index < chunks.length) {
                    nextText += chunks[index];
                    setStreamingText(nextText);
                    index += 1;
                    return;
                }

                clearInterval(interval);

                setTimeout(() => {
                    dispatch(chatActions.addInterviewMessage(content));
                    setStreamingText(".");
                    resolve();
                }, 100);
            }, STREAMING_INTERVAL);
        });
    }, [dispatch]);

    const streamMultipleLines = useCallback(async (contents) => {
        dispatch(chatActions.setIsStreaming(true));
        dispatch(chatActions.setIsMessageLoading(true));

        for (const content of contents) {
            await streamSingleLine(content);
        }

        dispatch(chatActions.setIsMessageLoading(false));
        dispatch(chatActions.setIsStreaming(false));
    }, [dispatch, streamSingleLine]);

    return (
        <div className="bg h-screen w-full overflow-hidden">
            <div className="w-full h-full max-w-[1240px] mx-auto relative">
                <ConversationPanel
                    messages={interviewMessages}
                    loadingText={streamingText}
                    streamMultipleLines={streamMultipleLines}
                />
            </div>
        </div>
    );
}

export default ChattingPage;
