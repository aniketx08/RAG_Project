import { Link, useLocation } from "react-router-dom";
import { motion } from "framer-motion";

export default function Navbar2() {
  const location = useLocation();

  return (
    <nav className="sticky top-0 z-50 bg-slate-950/90 backdrop-blur border-b border-slate-800">
      <div className="w-full flex items-center justify-between px-8 py-6">

        {/* EXTREME LEFT: LOGO */}
        <Link to="/">
          <h1 className="text-3xl font-bold tracking-wide text-white">
            Legal<span className="text-amber-500">AI</span>
          </h1>
        </Link>

        {/* EXTREME RIGHT: LINKS + CTA */}
        <div className="flex items-center gap-10">

          <NavLink to="/" label="Home" active={location.pathname === "/"} />
          <NavLink to="/about" label="About" active={location.pathname === "/about"} />
          <NavLink to="/faq" label="FAQ" active={location.pathname === "/faq"} />
          <NavLink to="/contact" label="Contact" active={location.pathname === "/contact"} />

          {/* GLOWING LOGIN BUTTON */}
          <Link to="/login" className="relative">
            {/* Continuous white glow */}
            <motion.div
              animate={{ opacity: [0.3, 1, 0.3] }}
              transition={{ duration: 2.5, repeat: Infinity, ease: "easeInOut" }}
              className="absolute -inset-[2px] rounded-lg bg-white/70 blur-md"
            />
            <button className="relative px-6 py-2 rounded-lg bg-orange-500 border border-white text-white font-semibold hover:bg-orange-600 transition">
              Login
            </button>
          </Link>

        </div>
      </div>
    </nav>
  );
}

/* NAV LINK */
function NavLink({ to, label, active }) {
  return (
    <Link
      to={to}
      className={`relative text-lg font-medium transition
        ${active ? "text-white" : "text-slate-300 hover:text-white"}
      `}
    >
      {label}
      <span
        className={`absolute -bottom-1 left-0 h-[2px] bg-amber-500 transition-all duration-300
          ${active ? "w-full" : "w-0 hover:w-full"}
        `}
      />
    </Link>
  );
}
