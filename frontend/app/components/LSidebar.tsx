"use client";

import React from "react";
import { useRouter, usePathname } from "next/navigation";

import { useMessage } from "../contexts/MessageContext";
import { useUI } from "../contexts/UIContext";

const LSidebar: React.FC = () => {
  const router = useRouter();
  
  const { setMessages, setInput } = useMessage();

  const pathname = usePathname();
  const sectionFromPath = pathname.split("/")[1] || "general";

  const { inputRef, setIsLeftMinimized, isLeftMinimized } = useUI();

  // useEffect(() => {
  //   fetchConversations();
  // }, []);

  const handleNewConversation = () => {
    router.push(`/${sectionFromPath}/new`);
    sessionStorage.removeItem("activeConversationId");
    sessionStorage.removeItem("uploadedFiles");
    setMessages([]);
    setInput("");
    // 👈 clears the conversationId from the URL
    inputRef.current?.focus();
  };

  return (
    <div
      onMouseEnter={() => setIsLeftMinimized(false)}
      onMouseLeave={() => setIsLeftMinimized(true)}
      className={`fixed left-0 z-40 h-screen top-14 transition-all duration-300 
        ${
          isLeftMinimized
            ? "w-14 px-0  shadow-[inset_-4px_0_6px_-2px_rgba(255,255,255,0.4)]"
            : "z-50 w-[18%] py-4 bg-[#1e1e1e] shadow-[inset_-4px_0_6px_-2px_rgba(255,255,255,0.4)]"
        }
      `}
    >
      {isLeftMinimized && (
        <div className="flex flex-col animate-pulse items-center text-white my-4 pr-2">
          <span className="text-sm">History</span>
          <span className="text-white text-sm">&#10148;</span>
        </div>
      )}

      <h2
        className={`text-lg text-center font-bold mb-4 text-white transition-opacity duration-300 ${
          isLeftMinimized ? "opacity-0" : "opacity-100"
        }`}
      >
        History
      </h2>

      {!isLeftMinimized && (
        <button
          className="w-full px-0 bg-slate-500/30 cursor-pointer mb-1 py-2 text-sm 
           hover:bg-gray-400/80 text-white mr-2 transition"
          onClick={handleNewConversation}
        >
          new
        </button>
      )}

      {/* Scrollable container for conversation list */}
      <div
        className={`transition-all duration-300 ${
          isLeftMinimized
            ? "overflow-hidden "
            : "dark-scrollbar  overflow-y-auto  max-h-[calc(100vh-200px)] pr-1 pb-[50%]"
        }`}
      >
        {/* Your conversation items go here */}
      </div>
    </div>
  );
};

export default LSidebar;