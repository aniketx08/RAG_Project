import { SignIn, SignedIn, SignedOut, useUser } from "@clerk/clerk-react";
import { useEffect } from "react";
import { useNavigate } from "react-router-dom";

export default function Login() {
  const { user, isLoaded } = useUser();
  const navigate = useNavigate();

  useEffect(() => {
    if (!isLoaded || !user) return;

    const role = user.unsafeMetadata?.role;

    if (role === "admin") navigate("/admin");
    else navigate("/client");
  }, [user, isLoaded, navigate]);

  return (
    <div className="h-screen flex justify-center items-center">
      <SignedOut>
        <SignIn path="/login" signUpUrl="/signup" />
      </SignedOut>

      <SignedIn>
        <p>Redirecting...</p>
      </SignedIn>
    </div>
  );
}
