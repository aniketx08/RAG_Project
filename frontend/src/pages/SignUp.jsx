import { SignUp } from "@clerk/clerk-react";

export default function Signup() {
  return (
    <div className="h-screen flex justify-center items-center">
      <SignUp
        path="/signup"
        routing="path"
        signInUrl="/login"
        unsafeMetadata={{ role: "client" }}   // 🔥 ASSIGN ROLE HERE
      />
    </div>
  );
}
