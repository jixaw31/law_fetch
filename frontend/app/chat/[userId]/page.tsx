"use client";

import { Suspense, useEffect } from "react";
import { useRouter } from "next/navigation";

import { useIsMounted } from "@/app/hooks/useIsMounted";

// import Sidebar from "@/app/components/LSidebar";
// import RSidebar from "@/app/components/RSidebar";

import ChatInput from "@/app/components/ChatInput";
import ProtectedRoute from "@/app/components/ProtectedRoute";
import AuthMessage from "@/app/components/AuthMessage";
import ChatMessages from "@/app/components/ChatMessages";
import Confirmation from "@/app/components/Confirmation"
// import MemZero from "@/app/components/MemZero";
// import { useUser } from "@/app/contexts/AuthContext";

const ConversationPage = () => {
  const router = useRouter();
  const isMounted = useIsMounted();
  // const {user} = useUser()

  // useEffect(() => {
  //   if (!isMounted) return; // only run on client

  //   if (!loadingConversations) {
  //     const storedId = sessionStorage.getItem("activeConversationId");
  //     const storedSection = sessionStorage.getItem("activeConversationSection") || "general";

  //     if (storedId) {
  //       router.replace(`/${storedSection}/${storedId}`);
  //     } else if (!conversations || conversations.length === 0) {
  //       router.replace("/general/new");
  //     }
  //   }
  // }, [isMounted, router]);

  // Show loader while fetching or waiting for hydration
  // || loadingConversations || !conversations it was beside !isMounted, before.
  if (!isMounted ) {
    return <div className="text-white">Loading conversations...</div>;
  }

  // Redirect effect handles empty conversations, render nothing
  // if (conversations.length === 0) return null;

  return (
    <Suspense>
      <ProtectedRoute>
        <div className="min-h-screen flex text-white">
          {/* Sidebar */}
          {/* <Sidebar /> */}
          {/* <RSidebar /> */}
          {/* Main Chat Content */}
          <div className="flex flex-col flex-1 items-center mt-10">
            {/* <div className="fixed right-[6%] top-[12%]">
              <div className="bg-slate-700 max-w-[139px] mb-4">
              </div>
              <hr className="border-t border-gray-300 mb-3.5 max-w-[85%] min-w-25 mx-auto" />
              <div className="bg-slate-700 max-w-[139px]">
                <MemZero />
              </div>
            </div> */}

            {/* Messages */}
            <ChatMessages />

            <div className="flex flex-col items-center justify-start mt-4">
              {/* other content */}
              {/* <Confirmation /> */}
            </div>

            <ChatInput />

            <AuthMessage />
          </div>
        </div>
      </ProtectedRoute>
    </Suspense>
  );
};

export default ConversationPage;
