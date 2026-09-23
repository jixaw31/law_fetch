"use client";

import React, { useRef, useState } from "react";
import { useMessage } from "../contexts/MessageContext";




const RSidebarChatInput: React.FC = () => {
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  
  // ✅ Get sidebar message sender from context
  const { sendSidebarMessage, wsConnected, isStreaming, sideInput, setSideInput } = useMessage();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!sideInput.trim() || !wsConnected || isStreaming) return;

    try {
      // ✅ Send message to sidebar context
      sendSidebarMessage();
      setSideInput("");
      
      if (textareaRef.current) {
        textareaRef.current.style.height = "auto";
      }
    } catch (error) {
      console.error("Error sending message:", error);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setSideInput(e.target.value);
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  };

  return (
    <form onSubmit={handleSubmit} className="w-full p-3">
      <div className="relative">
        <textarea
          ref={textareaRef}
          value={sideInput}
          onChange={handleInputChange}
          onKeyDown={handleKeyDown}
          placeholder={wsConnected ? "Quick Search..." : "Connecting..."}
          rows={1}
          className="w-full bg-gray-800/50 text-white rounded-xl pl-4 pr-12 py-3 
            resize-none focus:outline-none focus:ring-2 focus:ring-purple-500 
            focus:bg-gray-800 placeholder-gray-400 text-sm transition-all duration-200
            border border-gray-700 hover:border-gray-600"
          disabled={!wsConnected || isStreaming}
        />
        <button
          type="submit"
          disabled={!sideInput.trim() || !wsConnected || isStreaming}
          className={`absolute right-2 bottom-2 p-1.5 rounded-lg transition-all duration-200
            ${sideInput.trim() && wsConnected && !isStreaming
              ? 'bg-purple-600 hover:bg-purple-700 text-white shadow-lg hover:shadow-purple-500/30 cursor-pointer' 
              : 'bg-gray-700 text-gray-500 cursor-not-allowed'
            }`}
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
              d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
          </svg>
        </button>
      </div>
      
      {!wsConnected && (
        <div className="text-xs text-yellow-500 mt-2 text-right">
          Connecting...
        </div>
      )}
      
      {sideInput.length > 0 && wsConnected && (
        <div className="text-xs text-gray-500 mt-2 text-right">
          Press Enter to send
        </div>
      )}
    </form>
  );
};

export default RSidebarChatInput;