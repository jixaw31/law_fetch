'use client';

import { useState } from "react";
import { useUser } from "../contexts/AuthContext";

type User = {
  id: string;
  user_name: string;
  access_token?: string;
};

interface Props {
  isOpen: boolean;
  onClose: () => void;
  onSignup?: (user: User) => void; // Optional callback
}

export default function SignupModal({ isOpen, onClose, onSignup }: Props) {
  const [userName, setUserName] = useState("");
  const [password, setPassword] = useState("");
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false); // ✅ Loading state

  
  const { login } = useUser();

  const controller = new AbortController(); // Create an AbortController
  const signal = controller.signal;

  const handleSubmit = async (e: React.FormEvent) => {
  e.preventDefault();
  setLoading(true);

  const payload = { user_name: userName, password, email: email || undefined };

  try {
    const res = await fetch(
      `${process.env.NEXT_PUBLIC_API_BASE_URL}/auth/create-user`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
        signal, // pass the signal to fetch
      }
    );

    if (!res.ok) {
      const err: { detail?: string } = await res.json();
      alert(err.detail || "Signup failed");
      return;
    }

    // Auto-login
    const loginRes = await fetch(
      `${process.env.NEXT_PUBLIC_API_BASE_URL}/auth/sign-in`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_name: userName, password }),
        signal,
      }
    );

    if (!loginRes.ok) {
      alert("Auto-login failed");
      return;
    }

    type LoginResponse = {
      id: string;
      user_name: string;
      access_token: string;
    };

    const loginData: LoginResponse = await loginRes.json();

    login(
      { id: loginData.id, user_name: loginData.user_name },
      loginData.access_token
    );

    localStorage.setItem("token", loginData.access_token);
    localStorage.setItem("user_name", loginData.user_name);

    onSignup?.(loginData);
    onClose();
  } catch (err: unknown) {
    if (err instanceof Error) {
      if (err.name === "AbortError") {
        console.log("Signup request was cancelled");
      } else {
        console.error("Signup error:", err);
        alert(err.message || "Signup failed. Try again.");
      }
    } else {
      console.error("Signup error:", err);
      alert("Signup failed. Try again.");
    }
  } finally {
    setLoading(false);
  }
};


  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60">
      <div className="bg-gray-900 text-white rounded-lg p-6 w-full max-w-md shadow-xl">
        <h2 className="text-xl font-semibold mb-4">Create Account</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <input
            type="text"
            placeholder="Username"
            value={userName}
            onChange={(e) => setUserName(e.target.value)}
            required
            className="w-full bg-gray-800 border border-gray-700 text-white px-3 py-2 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            className="w-full bg-gray-800 border border-gray-700 text-white px-3 py-2 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <input
            type="email"
            placeholder="Email (optional)"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full bg-gray-800 border border-gray-700 text-white px-3 py-2 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <div className="flex justify-between items-center">
            {/* Left side: note or loading state */}
            <div className="flex items-center gap-2 min-w-[250px]">
              {loading ? (
                <>
                  <span className="text-white text-sm">Creating profile...</span>
                  <span className="loader border-2 border-white border-t-transparent rounded-full w-5 h-5 animate-spin"></span>
                </>
              ) : (
                <span className="text-white text-sm">
                  You will be signed in automatically.
                </span>
              )}
            </div>

            {/* Buttons on the right */}
            <div className="flex gap-2"> {/* extra gap and prevent wrapping */}
              <button
                type="button"
                onClick={() => {
                  setLoading(false); // Stop loading if user cancels
                  onClose();
                }}
                className="px-2 py-1 bg-gray-700 text-white cursor-pointer rounded hover:bg-gray-600"
              >
                Close
              </button>

              <button
                type="submit"
                disabled={loading}
                className={`px-2 py-1 bg-blue-600 text-white cursor-pointer rounded hover:bg-blue-500 ${
                  loading ? "opacity-50 cursor-not-allowed" : ""
                }`}
              >
                Sign Up
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
}
