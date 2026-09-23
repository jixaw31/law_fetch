"use client";

import React, { useEffect, useRef, useState } from "react";
import { useRouter, usePathname } from "next/navigation";
import { useMessage } from "../contexts/MessageContext";
import { useUI } from "../contexts/UIContext";
import RSidebarChatInput from "./RSidebarChatInput";

const RSidebar: React.FC = () => {
  const router = useRouter();
  // const { setMessages, setInput, messages } = useMessage();
  const pathname = usePathname();
  const { inputRef, isRightMinimized, setIsRightMinimized } = useUI();
  const sidebarRef = useRef<HTMLDivElement>(null);
  const contentRef = useRef<HTMLDivElement>(null);
  
  // const [sqMessages, setSqMessages] = useState([
  //   { content: "Hello! How can I help you?", type: "ai" },
  //   { content: "I need help with my project", type: "human" },
  //   { content: "Sure! What specific help do you need?", type: "ai" },
  //       { content: `Sure! What specific help do you need? Sure! What specific help do you need? Sure! 
  //         What specific help do you need? Sure! What specific help do you need?`, type: "ai" }


  // ]);
  
  const {sideMessages, loadingSideMessages} = useMessage()


  const handleSidebarClick = () => {
    if (isRightMinimized) {
      setIsRightMinimized(false);
    }
  };

  // Handle clicking outside to close
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (!isRightMinimized) {
        if (sidebarRef.current && !sidebarRef.current.contains(event.target as Node)) {
          setIsRightMinimized(true);
        }
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [isRightMinimized, setIsRightMinimized]);

  return (
    <>
      <div
  ref={sidebarRef}
  onClick={handleSidebarClick}
  className={`fixed right-0 z-40 top-14 transition-all duration-160
    ${isRightMinimized
      ? "w-48 px-0 h-[calc(100vh-3.5rem)] shadow-[-4px_0_6px_-2px_rgba(0,0,0,0.3)] bg-[#1e1e1e]/90 backdrop-blur-sm cursor-pointer hover:bg-[#2a2a2a]/90 hover:backdrop-blur-sm transition-colors"
      : "z-50 w-[43%] h-[calc(100vh-3.5rem)] py-4 bg-[#1e1e1e] shadow-[-4px_0_6px_-2px_rgba(0,0,0,0.3)] cursor-default flex flex-col"
    }
  `}
>
        {isRightMinimized && (
          <div className="flex flex-col items-center text-white my-4">
            <span className="text-sm font-medium">Side Quest</span>
            <span className="text-white text-xl mt-3">◀</span>
            <span className="text-xs mt-3 text-gray-400">Click to expand</span>
          </div>
        )}
        {!isRightMinimized && (
          <>
            {/* Fixed header with H2 */}
            <div className="flex-shrink-0 px-2">
              <h2 className="text-lg text-center font-bold text-white">
                Side Quest
              </h2>
            </div>

            {/* Dynamic content area - grows as messages are added */}
            <div 
              ref={contentRef}
              className="flex-grow overflow-y-auto dark-scrollbar px-2"
            >
              {/* This div will only show when there are messages */}
              {sideMessages && sideMessages.length > 0 && (
                <div className="space-y-4 mt-4">
                  {sideMessages.map((message, idx) => (
                    <div 
                      key={idx} 
                      className={`p-3 rounded-lg ${
                        message.type === 'human' 
                          ? 'bg-gray-600/20 ml-4' 
                          : 'bg-gray-800/50 mr-4'
                      }`}
                    >
                      <div className="text-white text-sm">{message.content}</div>
                    </div>
                  ))}
                </div>
              )}
              <br />
              <hr />
              <RSidebarChatInput />
            </div>

          </>
        )}
      </div>
    </>
  );
};

export default RSidebar;