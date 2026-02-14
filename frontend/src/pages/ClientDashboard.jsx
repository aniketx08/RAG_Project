'use client';

import { useState, useEffect, useRef } from "react";
import { useAuth } from "@clerk/clerk-react";
import { askQuestion, fetchChats } from "../services/api";
import { motion, AnimatePresence } from "framer-motion";

export default function ClientDashboard() {
  const { getToken } = useAuth();
  const [question, setQuestion] = useState("");
  const [chat, setChat] = useState([]);
  const [loading, setLoading] = useState(false);
  const sessionIdRef = useRef(crypto.randomUUID());
  const chatEndRef = useRef(null);

  // Load chat history
  useEffect(() => {
    async function loadChats() {
      const token = await getToken();
      const history = await fetchChats(token);
      setChat(history);
    }
    loadChats();
  }, []);

  // Auto-scroll on new messages
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chat]);

  const handleAsk = async () => {
    if (!question.trim()) return;

    try {
      setLoading(true);
      const token = await getToken();

      // Add user message immediately
      setChat(prev => [...prev, { role: "user", content: question }]);
      setQuestion("");

      const data = await askQuestion(
        { question, session_id: sessionIdRef.current },
        token
      );

      setChat(prev => [...prev, { role: "assistant", content: data.answer }]);
    } catch (err) {
      alert("Error fetching answer");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="relative min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-amber-950 flex flex-col items-center py-12 px-4">
      <div className="fixed inset-0 z-0 flex justify-center items-start pointer-events-none">
        <img
          src="https://cdn.arturbanstatue.com/wp-content/uploads/2021/12/1-7.jpg" // Replace with your image path
          alt="Justicia Statue"
          className="w-full max-w-7xl opacity-10 object-contain filter brightness-200"
        />
      </div>
      {/* Main chat container */}
      <div className="relative z-10 w-[80vw] max-w-5xl flex flex-col bg-black/50 backdrop-blur-lg border border-amber-700 rounded-2xl shadow-2xl p-6 h-[80vh]">

        {/* Chat messages scrollable */}
        <div className="flex-1 overflow-y-auto mb-4 space-y-4 px-2">
          <AnimatePresence initial={false}>
            {chat.map((msg, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                transition={{ duration: 0.3 }}
                className={`p-3 rounded-xl break-words max-w-[92%] ${
                  msg.role === "user"
                    ? "bg-amber-600 text-black self-end"
                    : "bg-black/60 border border-amber-500 text-amber-100 self-start"
                }`}
              >
                <strong>{msg.role === "user" ? "You" : "Assistant"}:</strong>
                <p className="mt-1 whitespace-pre-wrap">{msg.content}</p>
              </motion.div>
            ))}
          </AnimatePresence>
          <div ref={chatEndRef} />
        </div>

        {/* Input area */}
        <div className="flex gap-3 items-center">
          <textarea
            rows="2"
            placeholder="Type your legal question..."
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            className="flex-1 p-3 bg-black/50 border border-amber-700 rounded-xl text-amber-100 placeholder-amber-300 focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent resize-none transition-all duration-200"
          />
          <button
            onClick={handleAsk}
            disabled={loading}
            className="bg-amber-600 text-black font-semibold px-6 py-3 rounded-xl shadow-lg hover:bg-amber-500 transition disabled:opacity-60 disabled:cursor-not-allowed"
          >
            {loading ? "Thinking..." : "Send"}
          </button>
        </div>

      </div>

      {/* Disclaimer */}
      <p className="relative z-10 text-center text-sm text-amber-200 mt-4">
        Disclaimer: This is not legal advice.
      </p>

    </div>
  );
}
