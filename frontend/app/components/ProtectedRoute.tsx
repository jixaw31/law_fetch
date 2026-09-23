'use client';

import SignInModal from '../components/SignInModal';  // adjust path as needed
import { useUser } from '../contexts/AuthContext';

type User = {
  id: string;
  user_name: string;
  access_token?: string;
  
};

export default function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { user, login, isAuthChecked } = useUser();

  // Wait for auth check to finish before rendering anything
  if (!isAuthChecked) {
    return null; // or a loader component
  }

  // Show SignInModal if no user
  if (!user) {
    return (
      <SignInModal
        isOpen
        onClose={() => {}}
        onLogin={(loggedInUser: User) => {
          // Ensure access_token exists before calling login
          if (!loggedInUser.access_token) {
            console.warn('No access token available for login');
            return;
          }

          login(
            { id: loggedInUser.id, user_name: loggedInUser.user_name },
            loggedInUser.access_token
          );
        }}
      />
    );
  }

  // User is logged in, render protected content
  return <>{children}</>;
}
