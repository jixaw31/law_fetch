
import { useEffect, useState } from "react";
import { useMessage } from "../contexts/MessageContext";


export default function MemoryPopup() {
  const [visible, setVisible] = useState(false);
  
  const {creatingMemoryMsg} = useMessage()

  useEffect(() => {
    if (!creatingMemoryMsg) return;

    setVisible(true);
    const timer = setTimeout(() => setVisible(false), 3000);

    return () => clearTimeout(timer);
  }, [creatingMemoryMsg]);

  if (!creatingMemoryMsg) return null;

  return (
    <div
      className={`fixed top-4 right-4 z-50 px-4 py-2 bg-blue-600 
        text-white rounded-lg shadow-lg transition-opacity duration-500 ${
        visible ? "opacity-100" : "opacity-0"
      }`}
    >
      {creatingMemoryMsg}
    </div>
  );
}
