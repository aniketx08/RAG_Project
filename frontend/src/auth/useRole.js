import { useUser } from "@clerk/clerk-react";

export const useRole = () => {
  const { user, isLoaded } = useUser();

  if (!isLoaded || !user) {
    return null; // Clerk not loaded yet or no user logged in
  }

  return user.publicMetadata.role || null;
};
