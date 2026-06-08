import React, { useEffect, useState, useRef } from 'react';
import { useReactMediaRecorder } from 'react-media-recorder';
import { Mic, MicOff, Volume2 } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { useSelector } from 'react-redux';

import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";


export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}



const VoiceRecorder = ({userInput, setUserInput, sendUserInput, onStop, disabled = false }) => {
  const [isListening, setIsListening] = useState(false);
  const hasSentRef = useRef(false);
  // redux
  const {isTranscripting} = useSelector((state) => state.chat);

    const {
    startRecording,
    stopRecording,
    mediaBlobUrl,
  } = useReactMediaRecorder({ audio: true });

  const toggleListening = () => {
    if (isTranscripting || disabled) {
      return;
    }

    if (isListening) {
      stopRecording();
    } else {
       hasSentRef.current = false; // 重置发送标志
      startRecording();
    }
    setIsListening(!isListening);
  };


  useEffect(() => {
    let isMounted = true;

    if (mediaBlobUrl && onStop && !hasSentRef.current) {
      hasSentRef.current = true;
      fetch(mediaBlobUrl)
        .then(res => res.blob())
        .then(blob => {
          if (isMounted) {
            onStop(blob);
          }
        });
    }

    return () => {
      isMounted = false;
    };
  }, [mediaBlobUrl, onStop]);

    const renderInfo = () => {
      if (isTranscripting) {
        return "Transcribing..."
      }else if(disabled) {
        return "Please wait for Nova to finish";
      }else if(isListening) {
        return "Tap again to stop recording";
      }else{
        return "Click the button and start speaking";
      }
    }


  return (
    <div className="conversation-bottom flex flex-col gap-1"  id="conversation-bottom">
          <AnimatePresence>
          {userInput && (
          <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              exit={{ opacity: 0, height: 0 }}
              className="bg-white/70 border border-purple-200 rounded-3xl p-4 py-2 shadow-sm backdrop-blur-sm"
          >
              <div className="flex items-center gap-1 mb-2">
              <Volume2 className="w-2 h-2 text-purple-400" />
              <span className="text-sm font-medium text-voice-text">
                  Transcript
              </span>
              </div>
              <textarea 
                  className="text-voice-text leading-relaxed min-h-[2rem] w-full p-2 rounded focus:outline-none  resize-none overflow-y-auto" 
                  placeholder="Send your messages here"               
                  value={userInput}
                  onChange={(e) => setUserInput(e.target.value)}>
              </textarea>

              {!isListening && (
              <motion.button
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  onClick={sendUserInput}
                  className="px-2 py-2 bg-gradient-to-r from-purple-300 to-pink-300 text-purple-800 rounded-2xl text-sm font-medium hover:shadow-md transition-all duration-200 hover:from-purple-400 hover:to-pink-400"
              >
                  Send Message
              </motion.button>
              )}
          </motion.div>
          )}
      </AnimatePresence>
      <div className="flex flex-col items-center space-y-4">
        <motion.button
          onClick={toggleListening}
          disabled={isTranscripting || disabled}
          className={cn(
            "relative w-16 h-16 rounded-full flex items-center justify-center transition-all duration-300 shadow-lg",
            isListening
              ? "bg-gradient-to-br from-pink-200 to-rose-300 hover:shadow-xl"
              : "bg-gradient-to-br from-purple-200 to-pink-200 hover:shadow-xl hover:from-purple-300 hover:to-pink-300",
            (isTranscripting || disabled) && "cursor-not-allowed opacity-60",
          )}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          {/* 录音中动画圈圈 */}
          {isListening && (
            <motion.div
              className="absolute inset-0 rounded-full bg-pink-300/40"
              animate={{
                scale: [1, 1.3, 1],
                opacity: [0.6, 0.2, 0.6],
              }}
              transition={{
                duration: 2,
                repeat: Infinity,
                ease: "easeInOut",
              }}
            />
          )}

          <motion.div
            animate={isListening ? { scale: [1, 1.1, 1] } : {}}
            transition={{ duration: 0.8, repeat: Infinity }}
          >
            {isListening ? (
              <MicOff className="w-6 h-6 text-purple-700" />
            ) : (
              <Mic className="w-6 h-6 text-purple-700" />
            )}
          </motion.div>
        </motion.button>

        {/* 状态文本 */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-center"
        >
          <p className="text-voice-text font-medium text-sm">
            {/* {isListening ? "Listening..." : "Tap to speak"} */}
            {renderInfo()}
          </p>
          {/* <p className="text-voice-text-muted text-sm mt-1">
            {renderInfo()}
          </p> */}
        </motion.div>

        {/* 录音中 Indicator */}
        {isListening && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 10 }}
            className="flex items-center gap-1 text-voice-recording"
          >
            <motion.div
              className="w-2 h-2 bg-voice-recording rounded-full"
              animate={{ opacity: [1, 0.3, 1] }}
              transition={{ duration: 1, repeat: Infinity }}
            />
            <span className="text-sm font-medium">Recording</span>
          </motion.div>
        )}
      </div>
    </div>
  );
};

export default VoiceRecorder;
