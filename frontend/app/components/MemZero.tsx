import React, { useState } from "react";


const MemZero: React.FC = () => {
  // const { user } = useUser();
  const [isOpen, setIsOpen] = useState(true);

  // Log current memory hashes whenever memories change
//   useEffect(() => {
//   console.log(
//     "Current memories:",
//     memories
//   );
// }, [memories]);

  return (
    <div className="text-center">
      {/* Clickable title */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center justify-between px-1 cursor-pointer w-full 
        text-gray-200 text-sm font-semibold mb-1
        focus:outline-none hover:text-gray-700 hover:bg-gray-300
        transition-colors  py-1"
      >
        <span>Memories</span>
        <span
          className={`ml-2 inline-block transform transition-transform duration-300 ${
            isOpen ? "rotate-180" : "rotate-0"
          }`}
        >
          ▼
        </span>
      </button>

      

      {/* Animated collapse/expand */}
      <div
        className={`overflow-hidden transition-all duration-200 ease-in-out ${
          isOpen ? "max-h-64 opacity-100" : "max-h-0 opacity-0"
        }`}
      >
        <hr className="border-t border-gray-300 my-1 max-w-[85%] mx-auto" />
        <div
          className="text-[12px] h-64 overflow-y-auto p-2 border border-gray-700 
          rounded-md dark-blue-scrollbar"
        >
         
        </div>
      </div>
    </div>
  );
};

export default MemZero;
