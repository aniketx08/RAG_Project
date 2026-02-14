import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { SignOutButton } from "@clerk/clerk-react";

export default function Navbar2() {
  return (
    <motion.nav
      initial={{ y: -20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.6 }}
      className="sticky top-0 z-50 bg-black/80 backdrop-blur border-b border-amber-700 shadow-md"
    >
      <div className="w-full flex items-center justify-between px-12 py-6">

        {/* LOGO */}
        <Link to="/" className="relative">
          {/* Optional subtle glow behind the logo */}
          <motion.div
            animate={{ opacity: [0.3, 1, 0.3] }}
            transition={{ duration: 2.5, repeat: Infinity, ease: "easeInOut" }}
            className="absolute -inset-[4px] rounded-lg bg-amber-500/20 blur-md"
          />
          <h1 className="relative text-4xl font-extrabold">
            <span className="text-white">Legal</span>
            <span className="text-amber-500">AI</span>
          </h1>
        </Link>

        {/* LOGOUT BUTTON */}
        <SignOutButton>
          <button className="relative px-6 py-2 rounded-lg bg-amber-600 border border-white text-black font-semibold hover:bg-amber-500 hover:shadow-lg transition shadow-amber-500/30">
            Logout
          </button>
        </SignOutButton>

      </div>
    </motion.nav>
  );
}
