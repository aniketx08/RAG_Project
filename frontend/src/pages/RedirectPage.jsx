import { useUser } from "@clerk/clerk-react";
import { useEffect } from "react";
import { useNavigate } from "react-router-dom";

export default function RedirectPage() {
  const { user, isLoaded } = useUser();
  const navigate = useNavigate();

  useEffect(() => {
    if (!isLoaded || !user) return;

    const role = user.unsafeMetadata?.role;

    if (role === "admin") navigate("/admin");
    else navigate("/client");
  }, [user, isLoaded, navigate]);

  return <p>Redirecting...</p>;
}