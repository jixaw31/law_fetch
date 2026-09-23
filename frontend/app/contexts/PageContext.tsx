// 'use client';

// import {
//   createContext,
//   useContext,
//   useState,
//   useEffect,
//   ReactNode,
//   Dispatch,
//   SetStateAction
// } from 'react';
// import { usePathname } from 'next/navigation';

// interface PageContextType {
//   title: string;
//   setTitle: Dispatch<SetStateAction<string>>;
//   section: string;
//   setSection: Dispatch<SetStateAction<string>>;
// }

// const PageContext = createContext<PageContextType | null>(null);

// export const PageProvider = ({ children }: { children: ReactNode }) => {
//   const pathname = usePathname();
//   const [title, setTitle] = useState<string>('');
//   const [section, setSection] = useState<string>('');

//   useEffect(() => {
//     const titleMap: Record<string, string> = {
//       '/general/new': 'General',
//       '/dating/new': 'Dating',
//       '/prv_chat/new': 'Private Chat',
//       '/career/new': 'Career',
//     };

//     const currentTitle = titleMap[pathname];
//     const currentSection = pathname?.split('/')[1];

//     setTitle(currentTitle);
//     setSection(currentSection);
//   }, [pathname]);

//   return (
//     <PageContext.Provider value={{ title, setTitle, section, setSection }}>
//       {children}
//     </PageContext.Provider>
//   );
// };

// export const usePage = () => {
//   const context = useContext(PageContext);
//   if (!context) throw new Error('usePage must be used within a PageProvider');
//   return context;
// };
