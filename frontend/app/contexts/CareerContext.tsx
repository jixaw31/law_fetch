// 'use client';

// import {
//   createContext, ReactNode, useContext, useState,
//   Dispatch, SetStateAction
// } from 'react';


// export type MatchedUser = {
//   user_name: string;
//   similarity: number;
//   phone_number?: string | null;
//   city?: string | null;
//   country?: string | null;
// };

// interface CareerContextType {
//   matches: MatchedUser[];
//   fetchMatches: (userId: string) => Promise<void>;
//   setMatches: Dispatch<SetStateAction<MatchedUser[]>>;
//   isLoading: boolean;
//   error: string | null;
// }

// const CareerContext = createContext<CareerContextType | null>(null);

// export const CareerProvider = ({ children }: { children: ReactNode }) => {
//   const [matches, setMatches] = useState<MatchedUser[]>([]);
//   const [isLoading, setIsLoading] = useState(false);
//   const [error, setError] = useState<string | null>(null);

//   const fetchMatches = async (userId: string) => {
//     setIsLoading(true);
//     setError(null);

//     try {
//       const res = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/match_profiles/career/${userId}`, {
//         cache: 'no-store',
//       });

//       if (!res.ok) throw new Error(`Failed to fetch matches: ${res.status}`);

//       const data = await res.json();

//       // Map backend data to only the fields we care about
//       const mapped: MatchedUser[] = data.map((user: MatchedUser) => ({
//         user_name: user.user_name,
//         similarity: user.similarity,
//         phone_number: user.phone_number ?? null,
//         city: user.city ?? null,
//         country: user.country ?? null,
//       }));

//       // Optional: sort by similarity descending
//       mapped.sort((a, b) => b.similarity - a.similarity);

//       setMatches(mapped);
//     } catch (err: unknown) {
//       if (err instanceof Error) {
//         setError(err.message || "Something went wrong");
//       } else {
//         setError("Something went wrong");
//       }
//     } finally {
//       setIsLoading(false);
//     }
//   };

//   return (
//     <CareerContext.Provider value={{ matches, fetchMatches, setMatches, isLoading, error }}>
//       {children}
//     </CareerContext.Provider>
//   );
// };

// export const useCareerMatchesContext = () => {
//   const context = useContext(CareerContext);
//   if (!context) throw new Error('useCareerMatchesContext must be used within a CareerProvider');
//   return context;
// };
