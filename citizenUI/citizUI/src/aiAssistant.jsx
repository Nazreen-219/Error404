// components/AIAssistant.jsx
import { useEffect, useRef, useState } from "react";

const BACKEND_BASE_URL = import.meta.env.VITE_BACKEND_URL || "http://localhost:5000";
const EDGE_AI_BASE_URL = import.meta.env.VITE_EDGE_AI_URL || "http://127.0.0.1:8000";

export default function AIAssistant() {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [listening, setListening] = useState(false);
  const [edgeListening, setEdgeListening] = useState(false);
  const [voiceEnabled, setVoiceEnabled] = useState(false);
  const recognitionRef = useRef(null);

  const voiceSupported =
    typeof window !== "undefined" &&
    (window.SpeechRecognition || window.webkitSpeechRecognition);

  useEffect(() => {
    if (!voiceSupported) return;
    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    recognition.lang = "hi-IN";
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;
    recognition.onresult = (event) => {
      const transcript = event.results?.[0]?.[0]?.transcript;
      if (transcript) {
        setInput((prev) => (prev ? `${prev} ${transcript}` : transcript));
      }
    };
    recognition.onend = () => setListening(false);
    recognition.onerror = () => setListening(false);
    recognitionRef.current = recognition;
    return () => {
      recognitionRef.current = null;
    };
  }, [voiceSupported]);

  const toggleListening = () => {
    if (!voiceSupported) return;
    if (listening) {
      recognitionRef.current?.stop();
      setListening(false);
      return;
    }
    recognitionRef.current?.start();
    setListening(true);
  };

  const sendMessage = async () => {
    if (!input.trim()) return;
    const userMessage = { sender: "user", text: input };
    setMessages([...messages, userMessage]);
    setInput("");

    // Example: call your backend API (Node.js/Flask) for AI response
    try {
      const res = await fetch(`${BACKEND_BASE_URL}/copilot`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: input }),
      });
      const data = await res.json();
      const aiMessage = { sender: "ai", text: data.answer || data.response || "AI did not respond" };
      setMessages((prev) => [...prev, aiMessage]);
      if (voiceEnabled && "speechSynthesis" in window) {
        const utterance = new SpeechSynthesisUtterance(aiMessage.text);
        utterance.lang = "hi-IN";
        window.speechSynthesis.speak(utterance);
      }
    } catch (err) {
      const errorMsg = { sender: "ai", text: "Error connecting to AI service." };
      setMessages((prev) => [...prev, errorMsg]);
    }
  };

  const captureVoiceFromEdge = async () => {
    setEdgeListening(true);
    try {
      const res = await fetch(`${EDGE_AI_BASE_URL}/voice-input`, {
        method: "POST",
      });

      const data = await res.json();
      const speechText = data.speech_text || "";

      if (speechText) {
        setInput((prev) => (prev ? `${prev} ${speechText}` : speechText));
      } else {
        setMessages((prev) => [
          ...prev,
          { sender: "ai", text: "AI STT did not return any text." },
        ]);
      }
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { sender: "ai", text: "Error connecting to edge speech-to-text service." },
      ]);
    } finally {
      setEdgeListening(false);
    }
  };

  return (
    <>
      {/* Floating AI Button */}
      <div className="fixed bottom-6 right-6 z-50 flex items-center gap-3">
        <span className="bg-orange-500 text-white text-sm px-3 py-2 rounded-full shadow-md">
          अपनी शंका पूछें
        </span>
        <button
          className="bg-orange-500 text-white p-4 rounded-full shadow-lg hover:bg-orange-600 flex items-center justify-center"
          onClick={() => setOpen(true)}
          aria-label="Open AI assistant"
        >
          <svg
            viewBox="0 0 24 24"
            className="h-6 w-6"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            aria-hidden="true"
          >
            <path d="M12 2a3 3 0 0 0-3 3v6a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3z" />
            <path d="M19 10a7 7 0 0 1-14 0" />
            <path d="M12 17v5" />
            <path d="M8 22h8" />
          </svg>
        </button>
      </div>

      {/* Chat Window */}
      {open && (
        <div className="fixed bottom-20 right-6 w-80 h-96 bg-white rounded-xl shadow-lg flex flex-col z-50">
          <div className="flex justify-between items-center bg-orange-500 text-white p-3 rounded-t-xl">
            <span>AI Assistant</span>
            <button onClick={() => setOpen(false)}>
              <span aria-hidden="true">x</span>
              <span className="sr-only">Close</span>
            </button>
          </div>
          <div className="flex-1 p-3 overflow-y-auto space-y-2">
            {messages.map((msg, idx) => (
              <div
                key={idx}
                className={`p-2 rounded-lg max-w-[80%] ${
                  msg.sender === "user" ? "bg-blue-100 ml-auto" : "bg-green-100"
                }`}
              >
                {msg.text}
              </div>
            ))}
          </div>
          <div className="p-2 border-t flex gap-2 items-center">
            <input
              className="flex-1 p-2 border rounded-lg"
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask AI..."
              onKeyDown={(e) => e.key === "Enter" && sendMessage()}
            />
            <button
              type="button"
              className={`border px-3 py-2 rounded-lg ${
                listening ? "bg-red-100 border-red-300 text-red-700" : "bg-white"
              }`}
              onClick={toggleListening}
              disabled={!voiceSupported}
              title={voiceSupported ? "Voice input" : "Voice input not supported"}
              aria-label="Voice input"
            >
              <svg
                viewBox="0 0 24 24"
                className="h-4 w-4"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                aria-hidden="true"
              >
                <path d="M12 2a3 3 0 0 0-3 3v6a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3z" />
                <path d="M19 10a7 7 0 0 1-14 0" />
                <path d="M12 17v5" />
                <path d="M8 22h8" />
              </svg>
            </button>
            <button
              type="button"
              className={`border px-3 py-2 rounded-lg text-xs ${
                edgeListening ? "bg-orange-100 border-orange-300 text-orange-700" : "bg-white"
              }`}
              onClick={captureVoiceFromEdge}
              disabled={edgeListening}
              title="Use edge speech-to-text model"
              aria-label="AI speech input"
            >
              {edgeListening ? "Listening..." : "AI STT"}
            </button>
            <button
              className="bg-orange-500 text-white px-4 rounded-lg hover:bg-orange-600"
              onClick={sendMessage}
            >
              Send
            </button>
            <button
              type="button"
              className={`border px-3 py-2 rounded-lg ${
                voiceEnabled ? "bg-green-100 border-green-300 text-green-700" : "bg-white"
              }`}
              onClick={() => setVoiceEnabled((prev) => !prev)}
              title="Toggle voice replies"
              aria-label="Toggle voice replies"
            >
              <svg
                viewBox="0 0 24 24"
                className="h-4 w-4"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                aria-hidden="true"
              >
                <path d="M11 5 6 9H3v6h3l5 4z" />
                <path d="M15 9a5 5 0 0 1 0 6" />
                <path d="M17.5 6.5a8 8 0 0 1 0 11" />
              </svg>
            </button>
          </div>
        </div>
      )}
    </>
  );
}
