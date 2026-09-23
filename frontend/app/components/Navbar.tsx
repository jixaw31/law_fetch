'use client';

import { useState } from 'react';
import { usePathname, useRouter } from "next/navigation";


import SignupModal from './SignUpModal';
import SignInModal from './SignInModal';
import { useUser } from '../contexts/AuthContext';
import { useUI } from '../contexts/UIContext';
import Link from "next/link";


type User = {
  id: string;
  user_name: string;
  access_token?: string;
  
};

export default function Navbar() {

  const router = useRouter();
  const pathname = usePathname();
  
  // const {title} = usePage()
  

  const [showSignup, setShowSignup] = useState(false);
  const [showSignIn, setShowSignIn] = useState(false);
  
  const {user, setUser, setAuthMessage, setShowAuthMessage,
          authMessage, showAuthMessage, 
  } = useUser()
  const {setFadeOut, fadeOut} = useUI()
  const sections = [
    { name: "Chat", path: `/chat/${user?.id}` },
  ];
  
  const handleLogout = () => {
  localStorage.clear();       // clear all storage
  sessionStorage.clear();     // clear session storage
  setUser(null);
  

  setAuthMessage("Logged out!");
  setShowAuthMessage(true);
  setFadeOut(false);
  setTimeout(() => setFadeOut(true), 3000);
  setTimeout(() => setShowAuthMessage(false), 4000);
};

  // Use this to set user and persist in localStorage
  const saveUserToStorage = (user: User) => {
    setUser(user);
    localStorage.setItem('user', JSON.stringify(user));
  };

  // const linkClasses = (path: string) =>
  //   `px-4 h-full flex items-center justify-center transition`
  //   ;

  return (
    <nav className="sticky top-0 z-50 bg-[#1b1b1b] h-14 text-white">
      <div className="flex items-center justify-between h-full px-4">
        {/* Left (placeholder if needed) */}
        <div>
          <button
            onClick={() => router.push('/') }
            className="text-white px-3 h-13 cursor-pointer hover:bg-gray-700 transition"
          >
            Home
          </button>
        </div>
        <div />

        {/* Centered Nav Links */}
        <div className="absolute left-1/2 -translate-x-1/2 top-0 h-14 flex space-x-2">

        <div className="flex flex-row px-4">
          {sections.map(({ name, path }) => {
            const currentSegment = pathname.split("/")[1]; // "general" from "/general/new"
            const sectionSegment = path.split("/")[1];     // "general" from "/general/new"
            const isActive = currentSegment === sectionSegment;
            return (
              <Link
                key={name}
                href={path}
                className={`cursor-pointer h-full flex items-center justify-center
                  text-gray-400 transition-all duration-300 ease-in-out text-md px-2
                  ${isActive ? "text-white bg-gray-700" : "hover:bg-gray-500 hover:text-black hover:font-bold"}
                `}
              >
                {name}
              </Link>
            );
          })}
        </div>

        
          {/* <Link href={{ pathname: '/rag', query: { redirect: '/rag' } }}
           className={linkClasses('/rag')}>
            RAG
          </Link> */}
          
          {/* <Link href="/coder" className={linkClasses('/coder')}>
            CODER
          </Link> */}
        </div>

        {/* Right side: Username */}
        <div className="text-sm mr-10 h-full flex items-center p-1">
          {!user ? (
            <>
              <button
                className="h-1/2 mr-1 pr-2
                cursor-pointer text-blue-300 hover:text-gray-100 border-r border-white"
                onClick={() => {setShowSignIn(true);
                  router.push(`?redirect=/general/new`);
                  
                }}
              >
                Sign In
              </button>
              <button
                onClick={() => setShowSignup(true)}
                className="h-1/2 text-blue-300 pl-1 hover:text-gray-100 cursor-pointer"
              >
                Sign Up
              </button>
            </>
          ) : (
            <>
              <span className="mr-4">Hello, {user.user_name}</span>
              <button
                onClick={()=>{handleLogout();
                              router.push("/")
                        }}
                className="h-full text-blue-300 p-1 hover:text-gray-100 cursor-pointer"
              >
                Logout
              </button>
            </>
          )}
        </div>
      </div>

      <SignInModal
        isOpen={showSignIn}
        onClose={() => setShowSignIn(false)}
        onLogin={(loggedInUser) => {
          saveUserToStorage(loggedInUser);
          setShowSignIn(false);
        }}
      />
      <SignupModal isOpen={showSignup} onClose={() => setShowSignup(false)} />
      {showAuthMessage && (
      <div
        className={`absolute top-15 right-4 p-3 rounded ${
          !authMessage.includes("out") ? "bg-green-600 text-gray-100" : "bg-red-900 text-gray-200"
        } text-sm shadow-lg transition-opacity duration-1000 ${
          fadeOut ? "opacity-0" : "opacity-100"
        }`}
      >
        {authMessage}
      </div>
    )}
    </nav>
  );
}
