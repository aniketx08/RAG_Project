import { Navigate } from "react-router-dom";
import { useUser } from "@clerk/clerk-react";

export default function ProtectedRoute({ children, role }) {
  const { user, isLoaded } = useUser();

  if (!isLoaded) return <p>Loading...</p>;
  if (!user) return <Navigate to="/login" />;

  const userRole = user.unsafeMetadata?.role;

  if (role && userRole !== role) {
    return <Navigate to="/unauthorized" />;
  }

  return children;
}
