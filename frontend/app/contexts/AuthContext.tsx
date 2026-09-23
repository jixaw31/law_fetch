'use client';

import {
  createContext, ReactNode, useContext, useState,
  Dispatch, SetStateAction, useEffect
} from 'react';


export type User = {
  id: string;
  user_name: string;
  access_token?: string;
};

interface UserContextType {
  user: User | null;
  token: string | null;
  login: (user: User, token: string) => void;
  logout: () => void;
  setUser: Dispatch<SetStateAction<User | null>>;
  authMessage:string,
  setAuthMessage:(input: string) => void;
  showAuthMessage: boolean,
  setShowAuthMessage:Dispatch<SetStateAction<boolean>>,
  isAuthChecked: boolean,
}

const UserContext = createContext<UserContextType | null>(null);

export const UserProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [authMessage, setAuthMessage] = useState("");
  const [showAuthMessage, setShowAuthMessage] = useState(false);
  const [isAuthChecked, setIsAuthChecked] = useState(false);

  useEffect(() => {
    const storedUser = localStorage.getItem("user");
    const storedToken = localStorage.getItem("token");

    if (storedUser && storedToken) {
      setUser(JSON.parse(storedUser));
      setToken(storedToken);
    }
    setIsAuthChecked(true);
  }, []);

    const login = (user: User, token: string) => {
        setUser(user);

        setToken(token);
        localStorage.setItem('user', JSON.stringify(user));
        localStorage.setItem('token', token);
    };

    const logout = () => {
        setUser(null);
        setToken(null);
        localStorage.removeItem('user');
        localStorage.removeItem('token');
    };

    useEffect(() => {
      
      const storedUser = localStorage.getItem("user");
      const storedToken = localStorage.getItem("token");

      if (storedUser && storedToken) {
        setUser(JSON.parse(storedUser));
        setToken(storedToken);
      }
      
    }, []);

    return (
    <UserContext.Provider
      value={{
        user, token, login, logout, setUser,
        showAuthMessage, authMessage, setAuthMessage,
        setShowAuthMessage, isAuthChecked
      }}
    >
      {children}
    </UserContext.Provider>
  );
};


export const useUser = () => {
  const context = useContext(UserContext);
  if (!context) throw new Error('useUser must be used within a UserProvider');
  return context;
};
