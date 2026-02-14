'use client';

import { SignIn, SignedIn, SignedOut, useUser } from "@clerk/clerk-react";
import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";

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
    <div className="relative h-screen w-screen overflow-hidden">
      {/* Stationary background image */}
      <img
        src="https://cdn.arturbanstatue.com/wp-content/uploads/2021/12/1-7.jpg"
        alt="Justicia"
        className="absolute inset-0 w-full h-full object-cover brightness-125 opacity-30 pointer-events-none"
      />

      {/* Dark gradient overlay */}
      <div className="absolute inset-0 bg-gradient-to-br from-slate-950 via-slate-900 to-amber-950 opacity-80 pointer-events-none" />

      {/* Centered form */}
      <div className="relative z-10 flex items-center justify-center h-full px-6">
        <motion.div
          initial={{ opacity: 0, y: 40, scale: 0.95 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          transition={{ duration: 0.8 }}
          className="w-full max-w-md bg-slate-900/80 backdrop-blur-md border border-slate-700 rounded-2xl shadow-2xl p-8"
        >
          <SignedOut>
            <SignIn path="/login" signUpUrl="/signup" />
          </SignedOut>

          <SignedIn>
            <p className="text-white text-center">Redirecting...</p>
          </SignedIn>
        </motion.div>
      </div>
    </div>
  );
}
