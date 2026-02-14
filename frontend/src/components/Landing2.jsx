import { motion, useMotionValue, useMotionTemplate } from "framer-motion";
import { Link } from "react-router-dom";

export default function Landing2() {
  return (
    <div className="bg-gradient-to-br from-slate-950 via-slate-900 to-amber-950 text-white min-h-screen text-[17px] md:text-[18px] relative">

      {/* Fixed Justicia Background */}
      <div className="fixed inset-0 z-0 flex justify-center items-start pointer-events-none">
        <img
          src="https://cdn.arturbanstatue.com/wp-content/uploads/2021/12/1-7.jpg" // Replace with your image path
          alt="Justicia Statue"
          className="w-full max-w-7xl opacity-10 object-contain filter brightness-200"
        />
      </div>

      {/* HERO SECTION */}
      <section className="relative px-8 md:px-20 pt-40 pb-36 grid md:grid-cols-2 gap-16 items-center z-10">
        {/* HERO TEXT */}
        <motion.div
          initial={{ opacity: 0, y: 70 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.9 }}
          className="relative z-10"
        >
          <h2 className="text-6xl md:text-7xl font-extrabold leading-tight mb-8">
            Legal Advice.
            <br />
            <span className="text-amber-500">Simplified by AI.</span>
          </h2>

          <p className="text-slate-300 text-xl mb-10 max-w-xl">
            Legal AI provides instant, reliable legal guidance to everyday
            people — powered by artificial intelligence and built for clarity,
            speed, and trust.
          </p>
        </motion.div>

        {/* HERO VISUAL */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.8 }}
          className="relative z-10"
        >
          <div className="absolute inset-0 blur-3xl bg-amber-600/30 rounded-full" />
          <div className="relative bg-slate-900 border border-slate-800 rounded-2xl p-8 shadow-2xl">
            <p className="text-sm text-slate-400 mb-3">Legal AI Assistant</p>

            <div className="space-y-3">
              <div className="bg-slate-800 rounded-lg p-4 text-sm">
                What are my tenant rights?
              </div>

              <TypingBubble />
            </div>
          </div>
        </motion.div>
      </section>

      {/* FEATURES */}
      <section className="px-8 md:px-20 pb-36 relative z-10">
        <motion.h3
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          viewport={{ once: true }}
          className="text-4xl md:text-5xl font-extrabold mb-20 text-center"
        >
          Why Choose <span className="text-amber-500">Legal AI</span>
        </motion.h3>

        <div className="grid md:grid-cols-3 gap-12">
          {features.map((feature, index) => (
            <FeatureCard key={index} feature={feature} index={index} />
          ))}
        </div>
      </section>

      {/* CTA */}
      <section className="px-8 md:px-20 pb-28 text-center relative z-10">
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          whileInView={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.6 }}
          viewport={{ once: true }}
          className="bg-gradient-to-r from-amber-600 to-amber-500 rounded-2xl p-16 shadow-xl"
        >
          <h3 className="text-4xl md:text-5xl font-bold mb-6">
            Get Legal Clarity Today
          </h3>
          <p className="text-xl mb-10 text-amber-100">
            Ask questions, understand your rights, and make informed decisions —
            instantly.
          </p>
          <Link to="/login">
            <button className="px-12 py-5 bg-black/30 rounded-lg hover:bg-black/40 transition font-medium">
              Start Using Legal AI
            </button>
          </Link>
        </motion.div>
      </section>

      <footer className="border-t border-slate-800 py-10 text-center text-slate-500 text-sm relative z-10">
        © {new Date().getFullYear()} Legal AI. All rights reserved.
      </footer>
    </div>
  );
}

function TypingBubble() {
  return (
    <motion.div
      initial={{ width: 0 }}
      animate={{ width: "100%" }}
      transition={{ duration: 2.2, ease: "linear" }}
      className="overflow-hidden whitespace-nowrap bg-amber-600/20 border border-amber-500 rounded-lg p-4 text-sm"
    >
      Here’s a clear overview of your tenant rights under the law...
    </motion.div>
  );
}

/* FEATURE CARD: SCROLL IN + HOVER SHINE ONLY */
function FeatureCard({ feature, index }) {
  const mouseX = useMotionValue(0);
  const mouseY = useMotionValue(0);

  function handleMouseMove(e) {
    const rect = e.currentTarget.getBoundingClientRect();
    mouseX.set(e.clientX - rect.left);
    mouseY.set(e.clientY - rect.top);
  }

  return (
    <motion.div
      onMouseMove={handleMouseMove}
      initial={{ opacity: 0, y: 60 }}
      whileInView={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, delay: index * 0.12 }}
      viewport={{ once: true }}
      whileHover={{ scale: 1.03 }}
      className="relative bg-slate-900 border border-slate-800 rounded-2xl p-10 overflow-hidden group"
    >
      {/* HOVER SHINE */}
      <motion.div
        className="pointer-events-none absolute inset-0 opacity-0 group-hover:opacity-100 transition"
        style={{
          background: useMotionTemplate`
            radial-gradient(
              300px circle at ${mouseX}px ${mouseY}px,
              rgba(245,158,11,0.18),
              transparent 60%
            )
          `,
        }}
      />

      <div className="relative z-10">
        <div className="text-amber-500 text-4xl mb-5">{feature.icon}</div>
        <h4 className="text-2xl font-semibold mb-3">{feature.title}</h4>
        <p className="text-slate-400 text-lg leading-relaxed">
          {feature.description}
        </p>
      </div>
    </motion.div>
  );
}

const features = [
  {
    icon: "⚡",
    title: "Instant Answers",
    description:
      "Get legal guidance in seconds without scheduling appointments.",
  },
  {
    icon: "🛡️",
    title: "Trusted & Secure",
    description: "Privacy-focused design with secure AI-driven responses.",
  },
  {
    icon: "📚",
    title: "Plain Language",
    description: "No legal jargon — explanations anyone can understand.",
  },
];
