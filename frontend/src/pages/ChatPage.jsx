import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import client from "../api/client.js";

const QUICK_CHIPS = [
  "How do I apply for an SSN?",
  "What bank should I open as an F-1 student?",
  "When does my health insurance start?",
  "How do I read a US lease?",
  "What is SEVIS check-in?",
  "How does the US credit score system work?",
];

function ChatBubble({ role, content }) {
  return (
    <div className={`gb-chat-bubble gb-chat-bubble--${role}`}>
      <span className="gb-chat-bubble-text">{content}</span>
    </div>
  );
}

export default function ChatPage() {
  const [messages, setMessages] = useState([
    { role: "assistant", content: "Hi! I'm your Globalदोस्त AI assistant. Ask me anything about US student life — banking, SSN, housing, healthcare, visa paperwork, or just navigating a new city." },
  ]);
  const [input, setInput] = useState("");
  const [sessionId, setSessionId] = useState(null);
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const send = async (text) => {
    const msg = (text || input).trim();
    if (!msg || loading) return;

    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: msg }]);
    setLoading(true);

    try {
      const res = await client.post("/v1/chat/message", {
        message: msg,
        session_id: sessionId,
      });
      setSessionId(res.data.session_id);
      setMessages((prev) => [...prev, { role: "assistant", content: res.data.reply }]);
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "Sorry, I couldn't reach the AI service right now. Please try again in a moment." },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKey = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      send();
    }
  };

  return (
    <div className="gb-app">
      <nav className="gb-nav" aria-label="Primary">
        <Link to="/" className="gb-brand" style={{ textDecoration: "none" }}>
          <span className="gb-mark" aria-hidden="true" />
          <span className="gb-brand-name">{"Globalदोस्त"}</span>
        </Link>
        <div className="gb-nav-right">
          <Link to="/dashboard" className="gb-btn gb-btn-ghost">Dashboard</Link>
        </div>
      </nav>

      <div className="gb-chat-layout">
        {/* Header */}
        <header className="gb-chat-header">
          <h1 className="gb-chat-title">AI Assistant</h1>
          <p className="gb-chat-subtitle">Ask anything about US student life</p>
        </header>

        {/* Quick chip suggestions (shown only before first user message) */}
        {messages.length === 1 && (
          <div className="gb-chat-chips">
            {QUICK_CHIPS.map((chip) => (
              <button
                key={chip}
                type="button"
                className="gb-chat-chip"
                onClick={() => send(chip)}
              >
                {chip}
              </button>
            ))}
          </div>
        )}

        {/* Message thread */}
        <div className="gb-chat-thread" role="log" aria-live="polite" aria-label="Chat messages">
          {messages.map((m, i) => (
            <ChatBubble key={i} role={m.role} content={m.content} />
          ))}
          {loading && (
            <div className="gb-chat-bubble gb-chat-bubble--assistant gb-chat-bubble--typing">
              <span className="gb-typing-dot" />
              <span className="gb-typing-dot" />
              <span className="gb-typing-dot" />
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        {/* Input */}
        <div className="gb-chat-input-row">
          <textarea
            className="gb-chat-input"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKey}
            placeholder="Ask anything about US student life…"
            rows={1}
            aria-label="Chat input"
            disabled={loading}
          />
          <button
            type="button"
            className="gb-btn gb-btn-primary gb-chat-send"
            onClick={() => send()}
            disabled={loading || !input.trim()}
            aria-label="Send message"
          >
            Send
          </button>
        </div>

        <p className="gb-chat-disclaimer">
          Not legal advice. Verify immigration and legal questions with your ISS office or an attorney.
        </p>
      </div>
    </div>
  );
}
