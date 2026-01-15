import { useState } from "react";
import { useAuth } from "@clerk/clerk-react";

export default function AdminDashboard() {
  const { getToken } = useAuth();

  const [file, setFile] = useState(null);
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  const handleIngest = async () => {
    if (!file && !url) {
      setMessage("Please select a file or enter a URL.");
      return;
    }

    setLoading(true);
    setMessage("");

    try {
      const token = await getToken();
      const formData = new FormData();

      if (file) formData.append("file", file);
      if (url) formData.append("url", url);

      const response = await fetch("http://127.0.0.1:8000/ingest", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: formData,
      });

      if (!response.ok) {
        const text = await response.text();
        throw new Error(`Error ${response.status}: ${text}`);
      }

      const result = await response.json();
      setMessage(result.message || "Document ingested successfully!");
      setFile(null);
      setUrl("");
    } catch (err) {
      setMessage(err.message);
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
      <div className="relative bg-white/70 backdrop-blur-lg rounded-2xl shadow-xl border border-white/50 p-10 max-w-lg w-full">
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
                d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"
              />
            </svg>
          </div>
          <h2 className="text-2xl font-bold text-slate-800 tracking-tight">
            Admin Document Ingestion
          </h2>
        </div>

        {/* File upload */}
        <div className="mb-4">
          <label className="block text-sm font-medium text-slate-600 mb-2">
            Upload Document
          </label>
          <div className="relative">
            <input
              type="file"
              onChange={(e) => setFile(e.target.files[0])}
              className="w-full p-3 bg-white/50 border border-slate-200/60 rounded-xl text-slate-700 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-600 hover:file:bg-blue-100 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-transparent transition-all duration-200"
            />
          </div>
          {file && (
            <p className="mt-2 text-sm text-slate-500 flex items-center gap-1">
              <svg
                className="w-4 h-4 text-blue-500"
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
              {file.name}
            </p>
          )}
        </div>

        {/* URL input */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-slate-600 mb-2">
            Or Enter URL
          </label>
          <input
            type="text"
            placeholder="https://example.com/document.pdf"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            className="w-full p-3 bg-white/50 border border-slate-200/60 rounded-xl text-slate-700 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-transparent transition-all duration-200"
          />
        </div>

        {/* Ingest button */}
        <button
          onClick={handleIngest}
          disabled={loading}
          className="w-full bg-gradient-to-r from-blue-600 to-blue-700 text-white font-semibold py-3 px-6 rounded-xl shadow-lg shadow-blue-500/30 hover:shadow-xl hover:shadow-blue-500/40 hover:from-blue-700 hover:to-blue-800 transform hover:-translate-y-0.5 transition-all duration-200 disabled:opacity-60 disabled:cursor-not-allowed disabled:hover:transform-none disabled:hover:shadow-lg"
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
              Ingesting...
            </span>
          ) : (
            "Ingest"
          )}
        </button>

        {/* Message display */}
        {message && (
          <div
            className={`mt-4 p-4 rounded-xl border ${
              message.includes("Error") || message.includes("Please")
                ? "bg-red-50/50 border-red-200/60 text-red-600"
                : "bg-green-50/50 border-green-200/60 text-green-600"
            }`}
          >
            <p className="text-sm flex items-center gap-2">
              {message.includes("Error") || message.includes("Please") ? (
                <svg
                  className="w-5 h-5"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
              ) : (
                <svg
                  className="w-5 h-5"
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
              )}
              {message}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}