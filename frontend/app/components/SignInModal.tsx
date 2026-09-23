"use client"

import React, { useState } from "react";

import { useRouter, 
 } from 'next/navigation';
import { useUI } from "../contexts/UIContext";
import { useUser } from "../contexts/AuthContext";

type User = {
  id: string;
  user_name: string;
  access_token?: string;
};

interface SignInModalProps {
  isOpen: boolean;
  onClose: () => void;
  onLogin?: (user: User) => void;
}

const SignInModal: React.FC<SignInModalProps> = ({ isOpen, onClose, onLogin })=>{

  const router = useRouter();
  const [userName, setUserName] = useState("");
  const [password, setPassword] = useState("");
  const [errorMessage, setErrorMessage] = useState("");

  const {setFadeOut, fadeOut} = useUI()
  const {login, setAuthMessage, setShowAuthMessage,
    showAuthMessage, authMessage
  } = useUser()

  const handleSubmit = async (e: React.FormEvent) => {
  e.preventDefault();

  // ✅ Clear previous user data
  localStorage.clear();
  sessionStorage.clear();

  const payload = { user_name: userName, password };

  try {
    const res = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/auth/sign-in`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      const err = await res.json();
      setErrorMessage(err.detail || "Sign in failed");
      setFadeOut(false);
      setTimeout(() => setFadeOut(true), 2500);
      setTimeout(() => setErrorMessage(""), 3000);
      return;
    }

    const data = await res.json();

    // Save user + token
    login({ id: data.id, user_name: data.user_name }, data.access_token);

    // Show success message
    setAuthMessage("Signed in successfully!");
    setShowAuthMessage(true);
    setFadeOut(false);
    setTimeout(() => setFadeOut(true), 2500);
    setTimeout(() => setShowAuthMessage(false), 3000);

    // Store for this user
    localStorage.setItem("token", data.access_token);
    localStorage.setItem("user_name", data.user_name);

    if (onLogin) onLogin(data);
    onClose();

    // 🔥 ADD THIS LINE:
    router.push(`/chat/${data.id}`);

  } catch (error: unknown) {
    console.error("Sign in error:", error);
    setErrorMessage("Network or server error. Please try again.");
    setFadeOut(false);
    setTimeout(() => setFadeOut(true), 2500);
    setTimeout(() => setErrorMessage(""), 3000);
  }

  setErrorMessage("");
};


  const handleCancel = () => {
    if (onClose) onClose();
  };

  if (!isOpen) return null;
  
  return (
    
    
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60">
      {showAuthMessage && (
      <div
        className={`absolute top-20 mr-10 right-4 p-3 rounded ${
          !authMessage.includes("out") ? "bg-green-600 text-gray-100" : "bg-red-900 text-gray-200"
        } text-sm shadow-lg transition-opacity duration-1000 ${
          fadeOut ? "opacity-0" : "opacity-100"
        }`}
      >
        {authMessage}
      </div>
    )}
      <div className="bg-gray-900 text-white rounded-lg p-6 w-full max-w-md shadow-xl">
        <h2 className="text-xl font-semibold mb-4">Sign In</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <input
            type="text"
            placeholder="Username"
            value={userName}
            onChange={(e) => {
              setUserName(e.target.value);
              setErrorMessage("");
            }}
            required
            className="w-full bg-gray-800 border border-gray-700 text-white px-3 py-2 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => {
              setPassword(e.target.value);
              setErrorMessage("");
            }}
            required
            className="w-full bg-gray-800 border border-gray-700 text-white px-3 py-2 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          {errorMessage && (
            <div
              className={`text-sm text-gray-200 bg-red-900 bg-opacity-30 border border-red-500 rounded p-2 transition-opacity duration-1000 ${
                fadeOut ? "opacity-0" : "opacity-100"
              }`}
            >
              {errorMessage}
            </div>
          )}
          <div className="flex justify-end gap-2 ">
            <button
              type="button"
              onClick={()=>{handleCancel();
                            router.push("/")
              }}
              className="px-4 py-2 cursor-pointer bg-gray-700 text-white rounded hover:bg-gray-600"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="cursor-pointer px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-500"
            >
              Sign In
            </button>
          </div>
        </form>
      </div>
    </div>
   
  );
}


export default SignInModal;