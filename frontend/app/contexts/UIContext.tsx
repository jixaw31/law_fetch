'use client';

import {
  createContext, ReactNode, useContext, useState,
  Dispatch, SetStateAction, useRef
} from 'react';


interface UIContextType {
  inputRef: React.RefObject<HTMLTextAreaElement>;
  
  // Left sidebar states
  setIsLeftMinimized: Dispatch<SetStateAction<boolean>>;
  isLeftMinimized: boolean;
  
  // Right sidebar states
  setIsRightMinimized: Dispatch<SetStateAction<boolean>>;
  isRightMinimized: boolean;
  
  // Fade out state (kept for backward compatibility)
  fadeOut: boolean;
  setFadeOut: Dispatch<SetStateAction<boolean>>;
}

const UIContext = createContext<UIContextType | null>(null);

export const UIProvider = ({ children }: { children: ReactNode }) => {
  
  const inputRef = useRef<HTMLTextAreaElement>(null!);
  
  // Left sidebar state
  const [isLeftMinimized, setIsLeftMinimized] = useState(true);
  
  // Right sidebar state
  const [isRightMinimized, setIsRightMinimized] = useState(true);
  
  // Fade out state
  const [fadeOut, setFadeOut] = useState(false);
  
  return (
    <UIContext.Provider
      value={{
        inputRef,
        setIsLeftMinimized,
        isLeftMinimized,
        setIsRightMinimized,
        isRightMinimized,
        fadeOut,
        setFadeOut
      }}
    >
      {children}
    </UIContext.Provider>
  );
};

export const useUI = () => {
  const context = useContext(UIContext);
  if (!context) throw new Error('useUI must be used within a UIProvider');
  return context;
};