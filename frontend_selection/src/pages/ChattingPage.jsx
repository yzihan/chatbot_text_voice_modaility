import { useCallback, useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";

import ConversationPanel from "../components/ConversationPanel/ConversationPanel";
import { chatActions } from "../reducers/chatSlicer";

const STREAMING_INTERVAL = 20;
const LOADING_TEXTS = [".", "..", "..."];

function ChattingPage() {
    const dispatch = useDispatch();
    const { interviewMessages, isMessageLoading, isStreaming } = useSelector((state) => state.chat);

    useEffect(() => {
        if (!isMessageLoading || isStreaming) {
            return undefined;
        }

        let index = 0;
        const interval = setInterval(() => {
            dispatch(chatActions.setLoadingText(LOADING_TEXTS[index]));
            index = (index + 1) % LOADING_TEXTS.length;
        }, 500);

        return () => clearInterval(interval);
    }, [isMessageLoading, isStreaming, dispatch]);

    const streamSingleLine = useCallback((content) => {
        let index = 0;

        return new Promise((resolve) => {
            const interval = setInterval(() => {
                if (index < content.content.length) {
                    dispatch(chatActions.setLoadingText(content.content.substring(0, index + 1)));
                    index += 1;
                    return;
                }

                clearInterval(interval);

                setTimeout(() => {
                    dispatch(chatActions.addInterviewMessage(content));
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
        <div className="bg h-screen min-h-[750px] w-full min-w-[1060px]">
            <div className="w-full h-full max-w-[1240px] min-w-[1060px] mx-auto relative">
                <ConversationPanel
                    messages={interviewMessages}
                    streamMultipleLines={streamMultipleLines}
                />
            </div>
        </div>
    );
}

export default ChattingPage;
