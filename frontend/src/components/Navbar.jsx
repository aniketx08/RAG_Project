import React from "react";
import { useRole } from "../auth/useRole";
import { SignOutButton } from "@clerk/clerk-react";

const Navbar = () => {
  const role = useRole();

  return (
    <nav className="p-4 bg-white/70 backdrop-blur-lg border-b border-white/50 shadow-sm flex justify-between items-center">
      {/* Logo */}
      <div className="flex items-center gap-2">
        <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-blue-800 rounded-lg flex items-center justify-center shadow-md">
          <svg
            className="w-4 h-4 text-white"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
            />
          </svg>
        </div>
        <h1 className="font-bold text-xl text-slate-800 tracking-tight">
          Legal AI
        </h1>
      </div>

      {/* Right side */}
      <div className="flex items-center gap-4">
        {role ? (
          <span className="text-slate-600 text-sm flex items-center gap-2">
            <svg
              className="w-4 h-4 text-blue-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
              />
            </svg>
            Logged in as: <span className="font-medium text-slate-800">{role}</span>
          </span>
        ) : (
          <span className="text-slate-500 text-sm">Not logged in</span>
        )}
        <SignOutButton>
          <button className="px-4 py-2 bg-gradient-to-r from-red-500 to-red-600 text-white text-sm font-semibold rounded-xl shadow-md shadow-red-500/20 hover:shadow-lg hover:shadow-red-500/30 hover:from-red-600 hover:to-red-700 transform hover:-translate-y-0.5 transition-all duration-200">
            Logout
          </button>
        </SignOutButton>
      </div>
    </nav>
  );
};

export default Navbar;