// "use client";

// import { Suspense } from 'react';

// import Sidebar from '@/app/components/Sidebar';

// import ChatInput from '@/app/components/ChatInput';
// import ProtectedRoute from '@/app/components/ProtectedRoute';
// import AuthMessage from '@/app/components/AuthMessage';

// import ChatMessages from '@/app/components/ChatMessages';
// import MemZero from '@/app/components/MemZero';


// const ConversationPage = () => {
  

//   return (
//     <Suspense>
//     <ProtectedRoute>
//     <div className="min-h-screen flex text-white">
      
//       {/* rest of the dashboard */}
    
//       <Sidebar />
      
//       {/* Main Chat Content */}
//       <div className="flex flex-col flex-1 items-center mt-10">

//         {/* 🧩 Floating right-side widgets */}
//             <div className="fixed right-[6%] top-[12%] flex flex-col space-y-4">
//               <div className="bg-slate-700 max-w-[139px] mb-0">
//               </div>
//               <hr className="border-t border-gray-300 max-w-[85%] min-w-25 mx-auto my-2" />
//               <div className="bg-slate-700 max-w-[139px]">
//                 <MemZero />
//               </div>
//             </div>
        
//         {/* Messages */}
//         <ChatMessages />
//         <div className="flex flex-col items-center justify-start mt-4">
          
//           {/* other content */}
//         </div>
        
//         <ChatInput />
        

//         <AuthMessage />
        
        
//       </div>
      
//     </div>
//     </ProtectedRoute>
//     </Suspense>
//   );
// };

// export default ConversationPage;