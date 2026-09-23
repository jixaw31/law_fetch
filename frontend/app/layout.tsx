import type { Metadata } from "next";
import "./globals.css";
import Navbar from "./components/Navbar";
import { MessageProvider } from './contexts/MessageContext';
import { UserProvider } from "./contexts/AuthContext";
// import { ConvProvider } from "./contexts/ConvContext";
// import { FileProvider } from "./contexts/FileContext";
import { UIProvider } from "./contexts/UIContext";
import GlassyFooter from './components/GlassyStickyBottom';
// import { MemoriesProvider } from "./contexts/MemoriesContext";

import { CareerProvider } from "./contexts/CareerContext";
export const metadata: Metadata = {
  title: "defintely not JOOW",
  description: "",
};

// <ConvProvider>
// <FileProvider>
// <MemoriesProvider></MemoriesProvider>

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`antialiased`}
      > 
      <UIProvider >
        <UserProvider>
          <Navbar />
          
                <MessageProvider>
                 
                    {children}
                  
                </MessageProvider>
              
        </UserProvider>
      <GlassyFooter />
      </UIProvider>
      </body>
    </html>
  );
}


