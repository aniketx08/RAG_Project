import { useState } from "react";
import { useAuth } from "@clerk/clerk-react";
import { askQuestion } from "../services/api";

export default function ClientDashboard() {
  const { getToken } = useAuth();

  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [sources, setSources] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleAsk = async () => {
    try {
      setLoading(true);
      const token = await getToken();

      const data = await askQuestion(question, token);

      setAnswer(data.answer);
      setSources(data.sources || []);
    } catch (err) {
      alert("Error fetching answer");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 flex items-center justify-center p-6 relative overflow-hidden">
      {/* Background decorative elements */}
      <div className="absolute top-20 left-20 w-72 h-72 bg-blue-200 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-pulse" />
      <div className="absolute bottom-20 right-20 w-72 h-72 bg-slate-200 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-pulse" />

      {/* Main card */}
      <div className="relative bg-white/70 backdrop-blur-lg rounded-2xl shadow-xl border border-white/50 p-10 max-w-2xl w-full">
        {/* Header */}
        <div className="flex items-center gap-3 mb-6">
          <div className="w-12 h-12 bg-gradient-to-br from-blue-600 to-blue-800 rounded-xl flex items-center justify-center shadow-lg">
            <svg
              className="w-6 h-6 text-white"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
          </div>
          <h2 className="text-2xl font-bold text-slate-800 tracking-tight">
            Ask a Legal Question
          </h2>
        </div>

        {/* Question textarea */}
        <textarea
          rows="4"
          placeholder="Enter your legal question..."
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          className="w-full p-4 bg-white/50 border border-slate-200/60 rounded-xl text-slate-700 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-transparent resize-none transition-all duration-200"
        />

        {/* Ask button */}
        <button
          onClick={handleAsk}
          disabled={loading}
          className="mt-4 w-full bg-gradient-to-r from-blue-600 to-blue-700 text-white font-semibold py-3 px-6 rounded-xl shadow-lg shadow-blue-500/30 hover:shadow-xl hover:shadow-blue-500/40 hover:from-blue-700 hover:to-blue-800 transform hover:-translate-y-0.5 transition-all duration-200 disabled:opacity-60 disabled:cursor-not-allowed disabled:hover:transform-none disabled:hover:shadow-lg"
        >
          {loading ? (
            <span className="flex items-center justify-center gap-2">
              <svg
                className="animate-spin h-5 w-5 text-white"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                />
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                />
              </svg>
              Thinking...
            </span>
          ) : (
            "Ask"
          )}
        </button>

        {/* Answer section */}
        {answer && (
          <div className="mt-6 p-6 bg-white/50 rounded-xl border border-slate-200/60">
            <h3 className="text-lg font-semibold text-slate-800 mb-3 flex items-center gap-2">
              <svg
                className="w-5 h-5 text-blue-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              Answer
            </h3>
            <p className="text-slate-600 leading-relaxed">{answer}</p>

            {sources.length > 0 && (
              <>
                <h4 className="text-md font-semibold text-slate-800 mt-5 mb-2 flex items-center gap-2">
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
                      d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"
                    />
                  </svg>
                  Sources
                </h4>
                <ul className="space-y-1">
                  {sources.map((src, idx) => (
                    <li
                      key={idx}
                      className="text-slate-500 text-sm flex items-start gap-2"
                    >
                      <span className="text-blue-500 mt-1">•</span>
                      {src}
                    </li>
                  ))}
                </ul>
              </>
            )}
          </div>
        )}

        {/* Disclaimer */}
        <p className="mt-6 text-center text-xs text-slate-400">
          Disclaimer: This is not legal advice.
        </p>
      </div>
    </div>
  );
}