'use client';

import React from 'react';
import { useUser } from '../contexts/AuthContext';
import { useUI } from '../contexts/UIContext';



const AuthMessage: React.FC = () => {
  
  const {showAuthMessage, authMessage} = useUser()
  
  const {fadeOut} = useUI()

  if (!showAuthMessage) return null;

  const bgColor = authMessage.includes("out") ? "bg-gray-400" : "bg-green-600";

  return (
    <div
      className={`absolute top-20 mr-10 right-4 p-3 rounded ${bgColor} text-white text-sm shadow-lg transition-opacity duration-1000 ${
        fadeOut ? 'opacity-0' : 'opacity-100'
      }`}
    >
      {authMessage}
    </div>
  );
};


export default AuthMessage;
