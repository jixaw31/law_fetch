'use client';

import {
  createContext, ReactNode, useContext, useState,
  Dispatch, SetStateAction, useCallback, useRef,
  useEffect, useMemo
} from 'react';

import { useRouter, usePathname } from "next/navigation";

import { v4 as uuidv4 } from 'uuid';

import { useUser } from './AuthContext';
// import { log } from 'console';

type WSMessagePayload = {
  // user_id?: string;
  message: string;
};



// 1️⃣ Define BackendMessage separately
export interface BackendMessage {
  id: string;
  type: "ai" | "human" | "tool";
  content?: string | null;
  completed?: boolean;
  reasoning_ai?: string;
}

// 2️⃣ Keep Message as frontend state
export interface Message {
  id: string;
  content: string | null;
  type: "ai" | "human" | "tool" | "reasoning_ai";
  completed?: boolean;
}

interface Doctor {
  id: number;
  name: string;
  profession: string;
  title: string;
  description: string;
  specialties: string[];
  experience_years: number;
  education: string;
  hospital: string;
  location: string;
  rating: number;
  reviews_count: number;
  availability: string[];
  consultation_fee: number;
  phone: string;
  email: string;
  is_accepting_patients: boolean;
  languages: string[];
  profile_image: string;
}



interface MessageContextType {
  setLoadingMessages: Dispatch<SetStateAction<boolean>>;
  setMessages: Dispatch<SetStateAction<Message[]>>;
  fetchMessages: (id: string) => Promise<void>;
  sendMessage: () => void;
  messages: Message[];
  loadingMessages: boolean;
  spinnerLoading: boolean;
  input: string;
  setInput: React.Dispatch<React.SetStateAction<string>>;
  setSideInput: React.Dispatch<React.SetStateAction<string>>;
  sideInput:string,
  wsConnected:boolean;
  retrievedContent:string;
  streamingMessageId: string | null;
  stopMessage: () => void;  // ← ADD THIS LINE
  isStreaming: boolean;     // NEW: For active token streaming state
  sideMessages: Message[];
  loadingSideMessages:boolean,
  creatingMemoryMsg: string | null;
  sendSidebarMessage: () => void;  // ← ADD THIS
  confirmation:string;
  isRetrievedModalOpen: boolean;
  candidateDoctors: Doctor[];  // ← List of doctor dictionaries
  setDoctorChoice: React.Dispatch<React.SetStateAction<{action: string; doctor_id?: number} | null>>;
  setIsRetrievedModalOpen: React.Dispatch<React.SetStateAction<boolean>>;
}


const MessageContext = createContext<MessageContextType | null>(null);

export const MessageProvider = ({ children }: { children: ReactNode }) => {
  

  const pendingMessages = useRef<WSMessagePayload[]>([]);
  const [spinnerLoading, setSpinnerLoading] = useState(false);
  const [input, setInput] = useState('');
  const [sideInput, setSideInput] = useState('');
  const [doctorChoice, setDoctorChoice] = useState<{action: string; doctor_id?: number} | null>(null);  

  const [messages, setMessages] = useState<Message[]>([]);
  const [sideMessages, setSideMessages] = useState<Message[]>([]);
  const [activeContext, setActiveContext] = useState<"main" | "sidebar">("main");

  const [loadingMessages, setLoadingMessages] = useState(false);
  const [loadingSideMessages, setLoadingSideMessages] = useState(false);

  const [wsConnected, setWsConnected] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);  // ← ADD THIS

  const [retrievedContent, setRetrievedContent] = useState("");
  const [confirmation, setConfirmation] = useState("");
  const [candidateDoctors, setCandidateDoctors] = useState([]);
  const [isRetrievedModalOpen, setIsRetrievedModalOpen] = useState(false);
  // const [creatingMemoryMsg, setCreatingMemoryMsg] = useState<string | null>(null);
  const [creatingMemoryMsg] = useState<string | null>(null)
  const skipNextFetch = useRef(false);
  // const [streamingMessageId, setStreamingMessageId] = useState<string | null>(null);
  const streamingMessageId = useMemo(() => {
  if (!spinnerLoading) return null;
  
  // Find the last incomplete AI message
  for (let i = messages.length - 1; i >= 0; i--) {
    const msg = messages[i];
    if (msg.type === "ai" && !msg.completed) {
      return msg.id;
    }
  }
  return null;
}, [spinnerLoading, messages]);


  const router = useRouter();

  const pathname = usePathname();

  const sectionFromPath = pathname.split("/")[1];

  // WebSocket ref
  const wsRef = useRef<WebSocket | null>(null);

  const {user, } = useUser()

  // const {section} = usePage()

  useEffect(() => {
  const storedSection = sessionStorage.getItem("activeConversationSection");
  if (!storedSection) return;
  if (storedSection !== sectionFromPath) {
    setMessages([]);
    setSpinnerLoading(false);
    pendingMessages.current = [];
    sessionStorage.removeItem("activeConversationId");
    sessionStorage.removeItem("activeConversationSection");
  }
}, [sectionFromPath, setMessages, setSpinnerLoading]);

  // Updated WebSocket connection useEffect
useEffect(() => {
  if (!user) return;
  
  const collectionName = user.id;
  const url = `${process.env.NEXT_PUBLIC_API_BASE_URL_WS}/chat/stream/${collectionName}`;
  console.log("Connecting WS to:", url);

  const ws = new WebSocket(url);
  wsRef.current = ws;

  ws.onopen = () => {
    console.log("WebSocket connected");
    setWsConnected(true);
    pendingMessages.current.forEach((msg) => ws.send(JSON.stringify(msg)));
    pendingMessages.current = [];
  };

  ws.onclose = () => {
    console.log("WebSocket disconnected");
    setWsConnected(false);
    setSpinnerLoading(false);
    setIsStreaming(false);
  };

  ws.onerror = (err) => {
    console.error("WebSocket error:", err);
    setSpinnerLoading(false);
  };

  ws.onmessage = (event) => {
    try {
      const msg = JSON.parse(event.data);

      switch (msg.type) {
        case "token":
          setSpinnerLoading(false);
          setIsStreaming(true);
          
          // ✅ UPDATED: Check which context is active
          if (activeContextRef.current === "sidebar") {
            setSideMessages((prev) => {
              const lastMessage = prev[prev.length - 1];
              if (lastMessage?.type === "ai" && !lastMessage.completed) {
                return [
                  ...prev.slice(0, -1),
                  { ...lastMessage, content: (lastMessage.content || "") + msg.content },
                ];
              } else {
                return [
                  ...prev,
                  { id: uuidv4(), content: msg.content, type: "ai", completed: false },
                ];
              }
            });
          } else {
            // Original main chat logic
            setMessages((prev) => {
              const lastMessage = prev[prev.length - 1];
              if (lastMessage?.type === "ai" && !lastMessage.completed) {
                return [
                  ...prev.slice(0, -1),
                  { ...lastMessage, content: (lastMessage.content || "") + msg.content },
                ];
              } else {
                return [
                  ...prev,
                  { id: uuidv4(), content: msg.content, type: "ai", completed: false },
                ];
              }
            });
          }
          break;

        case "complete":
          setIsStreaming(false);
          
          // ✅ UPDATED: Mark complete based on active context
          if (activeContextRef.current === "sidebar") {
            setSideMessages((prev) => {
              const updated = [...prev];
              for (let i = updated.length - 1; i >= 0; i--) {
                if (updated[i].type === "ai" && !updated[i].completed) {
                  updated[i] = { ...updated[i], completed: true };
                  break;
                }
              }
              
              return updated;
            });
          } else {
            setMessages((prev) => {
              const updated = [...prev];
              for (let i = updated.length - 1; i >= 0; i--) {
                if (updated[i].type === "ai" && !updated[i].completed) {
                  updated[i] = { ...updated[i], completed: true };
                  break;
                }
              }
              return updated;
            });
          }
          setSpinnerLoading(false);
          break;
        case "confirmation":
          setConfirmation(msg.confirmation_content);
          // setCandidateDoctors([])
          break;
        case "candidate_doctors":
          setCandidateDoctors(msg.candidate_doctors);
          console.log("hellleoeleleo");
          
          console.log(candidateDoctors);
          
          break;
        case "retrieved_content":
          setRetrievedContent(msg.retrieved_content);
          break;
        case "stop_ack":
          console.log("🛑 Stream stopped by user");
          setSpinnerLoading(false);
          setIsStreaming(false);
          
          // ✅ UPDATED: Handle stop based on active context
          const markIncomplete = (prev: any[]) => {
            const updated = [...prev];
            for (let i = updated.length - 1; i >= 0; i--) {
              if (updated[i].type === "ai" && !updated[i].completed) {
                updated[i] = { 
                  ...updated[i], 
                  completed: true,
                  content: (updated[i].content || "") + " [stopped by user]"
                };
                break;
              }
            }
            return updated;
          };
          
          if (activeContextRef.current === "sidebar") {
            setSideMessages(markIncomplete);
          } else {
            setMessages(markIncomplete);
          }
          break;

        case "error":
          console.error("Backend error:", msg.error);
          setSpinnerLoading(false);
          
          // ✅ UPDATED: Add error to appropriate context
          const errorMessage = {
            id: uuidv4(),
            content: `⚠️ Error: ${msg.error || "An unexpected error occurred."}`,
            type: "ai" as const,
            completed: true,
          };
          
          if (activeContextRef.current === "sidebar") {
            setSideMessages((prev) => [...prev, errorMessage]);
          } else {
            setMessages((prev) => [...prev, errorMessage]);
          }
          break;

        default:
          console.warn("Unknown message type:", msg);
      }
    } catch (err) {
      console.error("Failed to parse WS message:", err, event.data);
      setSpinnerLoading(false);
    }
  };

  return () => {
    ws.close();
  };
}, [user?.id,
  // activeContext
]); // ✅ ADDED activeContext to dependency array

const activeContextRef = useRef<"main" | "sidebar">("main");

useEffect(() => {
  activeContextRef.current = activeContext;
}, [activeContext]);


useEffect(() => {
  if (doctorChoice && wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
    wsRef.current.send(JSON.stringify(doctorChoice));
    console.log(`Sent:`, doctorChoice);
    // Optional: Reset after sending
    setDoctorChoice(null);
  }
}, [doctorChoice]);

// Updated sendMessage function
const sendMessage = async () => {
  if (!input.trim()) return;

    setActiveContext("main");  // ← Set context before sending

  // Add human message immediately
  const userMessage: Message = {
    id: uuidv4(),
    content: input,
    type: "human",
  };
  
  setSpinnerLoading(true);  // Show spinner while waiting for first response
  setIsStreaming(false);     // Not streaming yet
  setMessages(prev => [...prev, userMessage]);

  // Send via WebSocket
  const payload = {
    message: input,
    context: "main"  // ← Add context
  };

  const ws = wsRef.current;
  if (!ws || ws.readyState !== WebSocket.OPEN) {
    pendingMessages.current.push(payload);
  } else {
    ws.send(JSON.stringify(payload));
  }

  setInput("");
};
  
// Add this function right after your sendMessage function
const sendSidebarMessage = async () => {
  if (!sideInput.trim()) return;
    setActiveContext("sidebar");  // ← Set context before sending

  // Add human message to sidebar immediately
  const userMessage: Message = {
    id: uuidv4(),
    content: sideInput,
    type: "human",
  };
  
  // setSpinnerLoading(true);  // Show spinner while waiting for first response
  setIsStreaming(false);     // Not streaming yet
  setSideMessages(prev => [...prev, userMessage]);

  // Send via WebSocket with sidebar context
  const payload = {
    message: sideInput,
    context: "sidebar"  // ← Important: tell backend this is sidebar
  };

  const ws = wsRef.current;
  if (!ws || ws.readyState !== WebSocket.OPEN) {
    pendingMessages.current.push(payload);
  } else {
    ws.send(JSON.stringify(payload));
  }

  setSideInput("");
};
const stopMessage = () => {
  const ws = wsRef.current;
  if (ws && ws.readyState === WebSocket.OPEN) {
    console.log("Sending stop command...");
    ws.send(JSON.stringify({ type: "stop" }));
    // Don't set spinnerLoading to false here - wait for stop_ack from server
  } else {
    console.warn("Cannot stop: WebSocket not connected");
  }
};
// useEffect(() => {
//   // Clear messages when user changes
//   setSideMessages([]);
//   // setSpinnerLoading(false);
//   pendingMessages.current = [];
// }, [user?.id]);

// FETCH MESSAGES ====================================================================================================
const fetchMessages = useCallback(async (user_id: string) => {
  // Always fetch if collection_name exists
  
  if (!user_id) {
    console.warn("No user_id provided to fetchMessages");
    return;
  }
  
  setLoadingMessages(true);

  try {
    const res = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/messages/${user_id}`);
    
    if (!res.ok) {
      if (res.status === 404) {
        // No messages found for this collection
        setMessages([]);
        // Don't remove sessionStorage here - keep the conversation ID
        // sessionStorage.removeItem("activeConversationId"); // Remove this line
      }
      return;
    }

    const responseData = await res.json();
    
    // Extract messages array (handle both old and new formats)
    const messagesArray = responseData.messages || (Array.isArray(responseData) ? responseData : []);
    
    // Convert to your Message format
    const normalized: Message[] = messagesArray.map((msg: any, idx: number) => {
      const role = msg.role || msg.type || "human";
      const contentValue = msg.content || "";
      
      return {
        id: msg.id || `${role}_${msg.timestamp || idx}_${Date.now()}`,
        type: role === "ai" || role === "assistant" ? "ai" : "human",
        content: contentValue || "[Empty message]",
        completed: true,
      };
    });

    setMessages(normalized);
    
    // Always store/update the collection name
    if (responseData.user_id) {
      sessionStorage.setItem("activeConversationId", responseData.user_id);
    } else if (user_id) {
      sessionStorage.setItem("activeConversationId", user_id);
    }

  } catch (err) {
    console.error("Failed to fetch messages:", err);
    setMessages([]);
  } finally {
    setLoadingMessages(false);
  }
}, [setMessages, setLoadingMessages]);

// FETCH SIDE MESSAGES ======================================================================================

const fetchSideMessages = useCallback(async (user_id: string) => {
  // Always fetch if collection_name exists
  
  if (!user_id) {
    console.warn("No user_id provided to fetchMessages");
    return;
  }
  
  setLoadingSideMessages(true);

  try {
    const res = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/side-messages/${user_id}`);
    
    if (!res.ok) {
      if (res.status === 404) {
        // No messages found for this collection
        setSideMessages([]);
        // Don't remove sessionStorage here - keep the conversation ID
        // sessionStorage.removeItem("activeConversationId"); // Remove this line
      }
      return;
    }

    const responseData = await res.json();
    console.log(responseData);
    
    // Extract messages array (handle both old and new formats)
    const messagesArray = responseData.messages || (Array.isArray(responseData) ? responseData : []);
    
    // Convert to your Message format
    const normalized: Message[] = messagesArray.map((msg: any, idx: number) => {
      const role = msg.role || msg.type || "human";
      const contentValue = msg.content || "";
      
      return {
        id: msg.id || `${role}_${msg.timestamp || idx}_${Date.now()}`,
        type: role === "ai" || role === "assistant" ? "ai" : "human",
        content: contentValue || "[Empty message]",
        completed: true,
      };
    });

    setSideMessages(normalized);
    
    // Always store/update the collection name
    // if (responseData.user_id) {
    //   sessionStorage.setItem("activeConversationId", responseData.user_id);
    // } else if (user_id) {
    //   sessionStorage.setItem("activeConversationId", user_id);
    // }

  } catch (err) {
    console.error("Failed to fetch messages:", err);
    setSideMessages([]);
  } finally {
    setLoadingSideMessages(false);
  }
}, [setSideMessages, setLoadingSideMessages]);

// 4️⃣ WebSocket effect AFTER fetchMessages  =================================================================
useEffect(() => {
  if (!user) return;

  if (skipNextFetch.current) {
    skipNextFetch.current = false;
    return;
  }

  fetchMessages(user.id);
  fetchSideMessages(user.id)
}, [user?.id, fetchMessages, fetchSideMessages]);
useEffect(() => {
  if (!user?.id) return;

  const fetchConfirmation = async () => {
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE_URL}/confirmation/${user.id}`
      );

      if (!response.ok) {
        // Endpoint may not exist yet — safely ignore for now
        return;
      }

      const data = await response.json();

      if (
        data.confirmation &&
        data.confirmation !== "no confirmation exists."
      ) {
        console.log(data);
        setConfirmation(data.confirmation);
      }
    } catch (error) {
      // Backend endpoint unavailable — safely ignore for now
      console.warn("Confirmation endpoint unavailable:", error);
    }
  };

  fetchConfirmation();
}, [user?.id]);
// FETCH RETRIEVED CONTENT =====================================================
useEffect(() => {
  if (!user?.id) return;

  const fetchRetrievedContent = async () => {
    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE_URL}/fetch_retrieved/${user.id}`
      );
      if (!res.ok) return;

      const data = await res.json();
      if (data.retrieved_content) {
        setRetrievedContent(data.retrieved_content);
      }
    } catch (err) {
      console.warn("Retrieved content endpoint unavailable:", err);
    }
  };

  fetchRetrievedContent();
}, [user?.id]);
  return (
    <MessageContext.Provider
      value={{
        setMessages, setLoadingMessages,
        fetchMessages, sendMessage, loadingMessages, messages,
        spinnerLoading, input, setInput, wsConnected, creatingMemoryMsg,
        streamingMessageId, stopMessage, isStreaming, sideMessages, loadingSideMessages,
        sendSidebarMessage, sideInput, setSideInput, retrievedContent, isRetrievedModalOpen,
        setIsRetrievedModalOpen, confirmation, candidateDoctors, setDoctorChoice
      }}
    >
      {children}
    </MessageContext.Provider>
  );
};


export const useMessage = () => {
  const context = useContext(MessageContext);
  if (!context) throw new Error('useMessage must be used within a MessageProvider');
  return context;
};