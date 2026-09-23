"use client";

import React, { useRef, useEffect, useState } from "react";
import { useMessage } from "../contexts/MessageContext";
import MemoryPopup from "./MemoryPopup";
import RetrievedContentModal from "./RetrievedContentModal"
import { Message } from "../contexts/MessageContext";
import MarkdownRenderer from "./MarkdownRender"; 

const ChatMessages: React.FC = () => {
  const containerRef = useRef<HTMLDivElement>(null!);
  const bottomRef = useRef<HTMLDivElement>(null!);
  const [collapsed, setCollapsed] = useState<{ [key: string]: boolean }>({});
  const spinnerStart = useRef<number | null>(null);
  const { loadingMessages, messages, spinnerLoading, setIsRetrievedModalOpen,
    confirmation, candidateDoctors, setDoctorChoice
   } = useMessage();

  const isCollapsed = (id: string) => collapsed[id] ?? false;

  const toggleCollapse = (id: string) => {
    setCollapsed((prev) => ({
      ...prev,
      [id]: !prev[id],
    }));
  };

  // Scroll to bottom if near bottom
  useEffect(() => {
    const container = containerRef.current;
    const bottom = bottomRef.current;
    if (!container || !bottom) return;

    const isNearBottom =
      container.scrollHeight - container.scrollTop - container.clientHeight < 150;

    if (isNearBottom) {
      requestAnimationFrame(() => {
        bottom.scrollIntoView({ behavior: "smooth", block: "end" });
        container.scrollBy({ top: -50, left: 0, behavior: "smooth" });
      });
    }
  }, [messages.length]);

  useEffect(() => {
    if (spinnerLoading) {
      spinnerStart.current = Date.now();
    } else if (spinnerStart.current) {
      const elapsed = Date.now() - spinnerStart.current;
      console.log(`⏱ Spinner was active for ${elapsed} ms`);
      spinnerStart.current = null;
    }
  }, [spinnerLoading]);

 

  // Group consecutive reasoning_ai messages
  const groupedMessages = React.useMemo(() => {
    const result: typeof messages = [];
    let buffer: string[] = [];

    messages
      .filter((msg) => msg.content && String(msg.content).trim() !== "")
      .forEach((msg, index, arr) => {
        if (msg.type === "reasoning_ai") {
          buffer.push(String(msg.content).replace(/\\n/g, "\n"));
          if (!arr[index + 1] || arr[index + 1].type !== "reasoning_ai") {
            result.push({
              id: `reasoning_ai_${index}`,
              type: "reasoning_ai",
              content: buffer.join("\n"),
            } as Message);
            buffer = [];
          }
        } else {
          result.push(msg as Message);
        }
      });

    return result;
  }, [messages]);

  // Initialize collapsed defaults for new messages
  useEffect(() => {
    setCollapsed((prev) => {
      const next = { ...prev };
      let changed = false;

      for (const msg of groupedMessages) {
        if (!(msg.id in next)) {
          if (msg.type === "reasoning_ai") {
            next[msg.id] = true; // collapsed by default
            changed = true;
          } else if (msg.type === "tool") {
            next[msg.id] = false; // open by default
            changed = true;
          }
        }
      }

      const currentIds = new Set(groupedMessages.map((m) => m.id));
      for (const k of Object.keys(next)) {
        if (!currentIds.has(k)) {
          delete next[k];
          changed = true;
        }
      }

      return changed ? next : prev;
    });
  }, [groupedMessages]);

  // Handle resume button click
  const handleResume = (messageId: string) => {
    // TODO: Implement resume functionality
    console.log(`Resume streaming for message: ${messageId}`);
    // You'll need to add this to your context or props
    // For example: onResumeStream(messageId)
  };

  return (
    <div ref={containerRef} className="flex-1 w-11/20 overflow-y-auto px-4 py-4">
      <MemoryPopup />
      <RetrievedContentModal />
      <div className="flex flex-col space-y-4">
        {loadingMessages ? (
          <div className="fixed top-1/2 left-1/2 transform -translate-x-1/2 
                          -translate-y-1/2 w-fit whitespace-nowrap bg-gray-200/20 text-center 
                          p-4 rounded border-light-300 animate-pulse z-50">
            Loading...
          </div>
        ) : (
          <div className="flex justify-center">
            <div className="w-5/6 px-4">
              {groupedMessages.map((msg, index, arr) => {
                const prevMsg = arr[index - 1];

                const showThickLine =
                  msg.type === "human" &&
                  prevMsg &&
                  ["ai", "tool", "reasoning_ai"].includes(prevMsg.type);

                const isAI = msg.type === "ai";
                const isTool = msg.type === "tool";
                const isReasoningAI = msg.type === "reasoning_ai";
                const isHuman = msg.type === "human";

                return (
                  <div key={msg.id} className="flex flex-col items-start pb-1">
                    {showThickLine && (
                      <hr className="mx-auto w-[95%] border-t-2 mb-2 border-gray-300" />
                    )}

                    <span className="text-sm text-gray-400 mb-1">
                      {isHuman
                        ? "You:"
                        : isAI
                        ? "Assistant:"
                        : isTool
                        ? "Tool:"
                        : isReasoningAI
                        ? "Reasoning:"
                        : "Unknown:"}
                    </span>

                    {(isTool || isReasoningAI) ? (
                      <div
                        className={`w-full rounded transition-all ${
                          !collapsed[msg.id]
                            ? isReasoningAI
                              ? "backdrop-blur-md bg-white/5 p-2"
                              : "bg-[#1e1e1e] p-1"
                            : ""
                        }`}
                      >
                        <button
                          onClick={() => toggleCollapse(msg.id)}
                          className="mb-1 px-2 cursor-pointer text-gray-500 py-1 hover:text-gray-200 rounded text-xs"
                        >
                          {isCollapsed(msg.id) ? "Show Message" : "Hide Message"}
                        </button>

                        {!isCollapsed(msg.id) && (
                          <div dir="auto" className="p-1 text-sm">
                            <MarkdownRenderer 
                              content={String(msg.content)} 
                              messageId={msg.id}
                            />
                          </div>
                        )}
                        
                      </div>
                    ) : (
                      <div
                      dir="auto"
                        className={`px-4 text-slate-200 text-sm w-full whitespace-pre-wrap overflow-hidden relative ${
                          isAI 
                            ? "bg-black/50 p-3 pb-4 mb-5" 
                            : isHuman
                            ? " bg-black/15 p-3 pb-4 mb-1.5" // Lighter background for human messages
                            : ""

                        }`}
                      >
                        
                          
                        
                        
                        
                        <MarkdownRenderer 
                          content={String(msg.content)} 
                          messageId={msg.id}
                        />
                        
                        {/* Resume button for AI messages - positioned at bottom right */}
                        {isAI && (
                          <div className="mt-2 flex items-center justify-end gap-2">
  {/* <button
    onClick={() => handleResume(msg.id)}
    className="rounded-md bg-blue-600 px-3 py-1.5 text-xs font-medium text-white
               transition-colors hover:bg-blue-700
               focus:outline-none focus:ring-2 focus:ring-blue-500
               cursor-pointer"
  >
    Resume
  </button> */}

                        {<button
                          onClick={() => setIsRetrievedModalOpen(true)}
                          className="rounded-md bg-gray-100 px-3 py-1.5 text-xs font-medium text-gray-700
                                    transition-colors hover:bg-gray-200
                                    focus:outline-none focus:ring-2 focus:ring-gray-400
                                    dark:bg-gray-800 dark:text-gray-200 dark:hover:bg-gray-700
                                    cursor-pointer"
                        >
                              مستندات
                        </button>}
                      </div>
                        )}
                      </div>
                    )}
                  
                  </div>
                );
              })}

              {spinnerLoading && (
                <div className="flex justify-start pl-2">
                  <div className="w-5 h-5 border-4 border-blue-500 border-t-transparent
                                  rounded-full animate-spin" />
                </div>
              )}

      
             
{candidateDoctors && candidateDoctors.length > 0 ? (

        <div className="p-1 bg-gray-800/30 rounded-lg border border-gray-700 w-full">
    <h3 className="text-white font-semibold mb-3 text-sm w-full text-right" dir="auto">یک دکتر را انتخاب کنید.</h3>
    <div className="space-y-2 w-full">
      {candidateDoctors.map((doctor) => (
        <div key={doctor.id} className="flex relative flex-row-reverse items-center justify-between bg-gray-700/30 p-3 rounded w-full">
          <div className="text-right w-full">
            <div className="text-white text-sm font-medium">{doctor.name}</div>
            <hr className="border-gray-600 my-1" />
            <div className="text-gray-400 text-xs">{doctor.profession}</div>
            <div className="text-gray-400 text-xs">{doctor.hospital}</div>
          </div>
          <div className="absolute bottom-1 left-1 flex gap-1">
            
            <button 
              onClick={() => {
                console.log("Cancel button clicked");
                setDoctorChoice({
                  action: "cancel_booking"
                });
              }}
              className="bg-gray-600 hover:bg-gray-700 text-white px-4 py-1.5 
              rounded text-xs transition-colors cursor-pointer"
            >
              انصراف
            </button>
            <button 
              onClick={() => {
                console.log(`Button clicked for doctor: ${doctor.name} (ID: ${doctor.id})`);
                setDoctorChoice({
                  action: "select_doctor",
                  doctor_id: doctor.id
                });
              }}
              className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-1.5 
              rounded text-xs transition-colors cursor-pointer"
            >
              انتخاب این دکتر
            </button>
          </div>
        </div>
      ))}
    </div>
  </div>
): null}      
              <div dir="auto">
  <MarkdownRenderer 
    content={confirmation === "" ? "" : confirmation} 
    messageId="confirmation"
  />
</div>
              <div className="h-46" />
              <div ref={bottomRef} />
            </div>
         
          </div>
          
        )}
      
      </div>
      
    </div>
  );
};

export default ChatMessages;
