'use client';

import { useUI } from "../contexts/UIContext";

const GlassyFooter = () => {

  const { isMinimized } = useUI();
  return (
    <div
      className={`sticky py-10 z-10 mt-2 bottom-0 left-0 w-full backdrop-blur-sm shadow-inner p-4 flex flex-col items-center justify-center border-t
        bg-blue-300/20 transition-all duration-300
        ${isMinimized ? 'pl-4' : 'pl-[18%]'}`}
    >
      <p className="absolute left-1/2 transform -translate-x-1/2 text-white text-sm">Some wisdom message will be displayed here.</p>
    </div>
  );
};

export default GlassyFooter;