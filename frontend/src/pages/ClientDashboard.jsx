import { useState, useEffect, useRef } from "react";
import { useAuth } from "@clerk/clerk-react";
import {
  askQuestion,
  fetchChats,
  createConversation,
  getMessages,
  getConversations,
} from "../services/api";
import { motion, AnimatePresence } from "framer-motion";
import SpeechRecognition, {
  useSpeechRecognition,
} from "react-speech-recognition";
export default function ClientDashboard() {
  const { getToken } = useAuth();
  const [question, setQuestion] = useState("");
  const [chat, setChat] = useState([]);
  const [loading, setLoading] = useState(false);
  const sessionIdRef = useRef(crypto.randomUUID());
  const chatEndRef = useRef(null);
  const [recording, setRecording] = useState(false);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const [language, setLanguage] = useState("auto");

  const [conversations, setConversations] = useState([]);
  const [activeConversation, setActiveConversation] = useState(null);

  const {
    transcript,
    listening,
    resetTranscript,
    browserSupportsSpeechRecognition,
  } = useSpeechRecognition();

  const isSendDisabled = loading || listening || !question.trim();

  useEffect(() => {
    if (!transcript) return;

    const processTranscript = async () => {
      if (language === "en-US") {
        setQuestion(transcript);
      } else {
        try {
          const res = await fetch("http://127.0.0.1:8000/translate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              text: transcript,
              source_lang: language,
            }),
          });

          const data = await res.json();
          setQuestion(data.translated_text);
        } catch (err) {
          console.error(err);
          alert("Translation failed");
        }
      }
    };

    processTranscript();
  }, [transcript]);

  const startListening = () => {
    resetTranscript();
    SpeechRecognition.startListening({
      continuous: true,
      language: language,
    });
  };

  const stopListening = () => {
    SpeechRecognition.stopListening();
  };

  //--------------------------------------------------------------------------------

  const transcribeAudio = async (blob) => {
    try {
      const formData = new FormData();
      formData.append("file", blob, "audio.webm");
      formData.append("language", language);

      const response = await fetch("http://127.0.0.1:8000/transcribe", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      setQuestion((prev) => prev + " " + data.text);
    } catch (error) {
      console.error(error);
      alert("Transcription failed");
    }
  };

  const startRecording = async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const mediaRecorder = new MediaRecorder(stream);

    audioChunksRef.current = [];

    mediaRecorder.ondataavailable = (event) => {
      audioChunksRef.current.push(event.data);
    };

    mediaRecorder.onstop = async () => {
      const blob = new Blob(audioChunksRef.current, { type: "audio/webm" });
      await transcribeAudio(blob);
    };

    mediaRecorder.start();
    mediaRecorderRef.current = mediaRecorder;
    setRecording(true);
  };

  const stopRecording = () => {
    mediaRecorderRef.current.stop();
    setRecording(false);
  };

  const handleNewChat = async () => {
    const token = await getToken();

    const data = await createConversation(token);

    setActiveConversation(data.conversation_id);
    setChat([]);
  };

  const loadConversation = async (id) => {
    const token = await getToken();

    const msgs = await getMessages(id, token);

    setActiveConversation(id);
    setChat(msgs);
  };

  useEffect(() => {
    const loadConversations = async () => {
      const token = await getToken();
      const data = await getConversations(token);

      setConversations(Array.isArray(data) ? data : []);
    };

    loadConversations();
  }, []);

  // Load chat history
  useEffect(() => {
    async function loadConversations() {
      const token = await getToken();
      const data = await getConversations(token);
      setConversations(data);
    }

    loadConversations();
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

      let convoId = activeConversation;

      // Create chat automatically if none exists
      if (!convoId) {
        const convo = await createConversation(token);
        convoId = convo.conversation_id;
        setActiveConversation(convoId);
      }

      setChat((prev) => [...prev, { role: "user", content: question }]);
      setQuestion("");

      const data = await askQuestion(
        {
          question,
          conversation_id: convoId,
        },
        token,
      );

      setChat((prev) => [...prev, { role: "assistant", content: data.answer }]);
    } catch (err) {
      console.error(err);
      alert("Error fetching answer");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="relative min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-amber-950 flex">
      {/* Sidebar */}
      <div className="w-72 bg-black/60 backdrop-blur-lg border-r border-amber-700 flex flex-col p-4">
        <button
          onClick={handleNewChat}
          className="w-full bg-amber-600 text-black font-semibold py-2 rounded-xl mb-4 hover:bg-amber-500 transition"
        >
          + New Chat
        </button>

        <div className="flex-1 overflow-y-auto space-y-2">
          {conversations.map((c) => (
            <div
              key={c.id}
              onClick={() => loadConversation(c.id)}
              className={`p-3 rounded-xl cursor-pointer border transition
        ${
          activeConversation === c.id
            ? "bg-amber-600 text-black border-amber-500"
            : "bg-black/50 text-amber-100 border-amber-800 hover:bg-amber-900"
        }`}
            >
              {c.title}
            </div>
          ))}
        </div>
      </div>

      {/* Chat window */}
      <div className="flex-1 flex flex-col items-center py-12 px-4">
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
            {/* <select
  value={language}
  onChange={(e) => setLanguage(e.target.value)}
  className="px-3 py-2 bg-black/50 border border-amber-700 rounded-xl text-amber-100 focus:outline-none"
>
  <option value="auto">Auto</option>
  <option value="hi">Hindi</option>
  <option value="mr">Marathi</option>
</select> */}

            <select
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
              className="px-3 py-2 bg-black/50 border border-amber-700 rounded-xl text-amber-100 focus:outline-none"
            >
              <option value="en-US">English</option>
              <option value="hi-IN">Hindi</option>
              <option value="mr-IN">Marathi</option>
            </select>

            <textarea
              rows="2"
              placeholder="Type your legal question..."
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              className="flex-1 p-3 bg-black/50 border border-amber-700 rounded-xl text-amber-100 placeholder-amber-300 focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent resize-none transition-all duration-200"
            />

            {/* <button
    onClick={recording ? stopRecording : startRecording}
    className={`px-4 py-3 rounded-xl font-semibold transition ${
      recording
        ? "bg-red-600 text-white"
        : "bg-amber-700 text-black"
    }`}
  >
    {recording ? "Stop" : "🎤"}
  </button> */}

            <button
              onClick={listening ? stopListening : startListening}
              className={`px-4 py-2 rounded-lg ${
                listening ? "bg-red-600" : "bg-amber-600 text-black"
              }`}
            >
              {listening ? "Stop" : "🎤"}
            </button>

            <button
              onClick={handleAsk}
              disabled={isSendDisabled}
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
    </div>
  );
}
