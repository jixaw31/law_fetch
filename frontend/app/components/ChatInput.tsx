'use client';

import {
  useRef, useState, useEffect
} from 'react';
import CustomScroll from 'react-customscroll';

import { motion } from 'framer-motion';
import { useMessage } from '../contexts/MessageContext';

const ChatInput: React.FC = () => {
  
  const inputRef = useRef<HTMLTextAreaElement>(null!);
  const [messageSubmitted, setMessageSubmitted] = useState(false);
  const {sendMessage, stopMessage, input, setInput, spinnerLoading, isStreaming} = useMessage()  // ← Use spinnerLoading instead

  // Auto-resize function
  const autoResize = () => {
    const textarea = inputRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      const newHeight = Math.min(textarea.scrollHeight, 200);
      textarea.style.height = `${newHeight}px`;
    }
  };

  useEffect(() => {
    autoResize();
  }, [input]);

  useEffect(() => {
    autoResize();
  }, []);

  useEffect(() => {
    if (!spinnerLoading) {
      setMessageSubmitted(false);
    }
  }, [spinnerLoading]);

  const handleSendMessage = async () => {
    if (!input.trim()) return;

    setMessageSubmitted(true);
    sendMessage();  // Note: sendMessage is not async in your code
    setInput("");
    
    setTimeout(() => {
      if (inputRef.current) {
        inputRef.current.style.height = 'auto';
      }
    }, 0);
  };

  const handleStopMessage = () => {
    if (stopMessage) {
      stopMessage();
    }
  };

  const handleButtonClick = () => {
    if (isStreaming) {
      handleStopMessage();
    } else {
      handleSendMessage();
    }
  };

  const shouldShowInput = true;
  if (!shouldShowInput) return null;

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    // Don't send message with Enter if streaming (only stop button works)
    if (e.key === 'Enter' && !e.shiftKey && !spinnerLoading) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  // Determine button styling based on state
  const getButtonClasses = () => {
    if (isStreaming) {
      return "bg-red-600 text-white hover:bg-red-700 hover:scale-105 cursor-pointer";
    }
    return input.trim()
      ? 'bg-blue-600 text-white hover:bg-blue-500 hover:scale-105 cursor-pointer'
      : 'bg-gray-600 text-gray-400 cursor-not-allowed';
  };

  const isButtonDisabled = !isStreaming && !input.trim();

  return (
    <motion.div
      
      initial={{
        bottom: '5rem',
        left: '50%',
        translateX: '-50%',
        translateY: '0%',
        position: 'fixed',
      }}
      animate={
        messageSubmitted
          ? {
              bottom: '5rem',
              transition: { duration: 0.2 },
            }
          : {}
      }
      transition={{ duration: 0.3, ease: 'easeInOut' }}
      className="w-[45%] mx-auto mb-1"
    >
      <div className="relative">
        <textarea
          dir='auto'
          ref={inputRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          rows={1}
          disabled={spinnerLoading}
          className={`w-full resize-none bg-gray-700
            rounded-xl px-8 py-3 pr-12 text-gray-100
            focus:outline-none focus:ring-1 focus:ring-gray-120 text-sm
            transition-all duration-200 custom-scrollbar-textarea
            ${spinnerLoading ? 'opacity-50 cursor-not-allowed' : ''}`}
          placeholder={spinnerLoading ? "AI is responding... (Click stop to interrupt)" : "Ask your question..."}
        />

        <button
  onClick={handleButtonClick}
  disabled={isButtonDisabled}
  className={`absolute mr-1 right-3 bottom-3 w-8 h-8 rounded-full 
    transition-all duration-200 flex items-center justify-center z-10 
    ${getButtonClasses()}`}
>
  {isStreaming ? (
    // Stop icon - white background with blue square
    <div className="w-5 h-5 bg-white rounded-sm flex items-center justify-center">
      <div className="w-3 h-3 bg-blue-600 rounded-sm"></div>
    </div>
  ) : (
    // Send icon (arrow)
    <svg 
      className="w-4 h-4" 
      fill="none" 
      stroke="currentColor" 
      viewBox="0 0 24 24"
    >
      <path 
        strokeLinecap="round" 
        strokeLinejoin="round" 
        strokeWidth={2} 
        d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" 
      />
    </svg>
  )}
</button>
      </div>
      
      {/* Optional: Show streaming indicator */}
      {spinnerLoading && (
        <div className="text-xs text-gray-400 mt-2 text-center">
          <span className="animate-pulse">●</span> AI is generating... 
          <button 
            onClick={handleStopMessage}
            className="ml-2 text-red-400 hover:text-red-300 underline"
          >
            Stop
          </button>
        </div>
      )}
    </motion.div>
  );
};

export default ChatInput;