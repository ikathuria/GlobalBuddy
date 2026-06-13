import { useEffect, useRef, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import client, { API_BASE_URL } from "../api/client.js";
import { getAuthToken } from "../auth/tokenStore.js";

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
  const [searchParams, setSearchParams] = useSearchParams();
  const seedSentRef = useRef(false);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  // Append `text` to the last assistant bubble, creating it if needed.
  const appendDelta = (text) => {
    setMessages((prev) => {
      const last = prev[prev.length - 1];
      if (last?.role === "assistant" && last.streaming) {
        return [...prev.slice(0, -1), { ...last, content: last.content + text }];
      }
      return [...prev, { role: "assistant", content: text, streaming: true }];
    });
  };

  const finishStream = () => {
    setMessages((prev) => {
      const last = prev[prev.length - 1];
      if (last?.role === "assistant" && last.streaming) {
        return [...prev.slice(0, -1), { role: "assistant", content: last.content }];
      }
      return prev;
    });
  };

  const streamReply = async (msg) => {
    const token = getAuthToken();
    const res = await fetch(`${API_BASE_URL}/v1/chat/stream`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: JSON.stringify({ message: msg, session_id: sessionId }),
    });
    if (!res.ok || !res.body) throw new Error(`stream failed: ${res.status}`);

    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";
    let sawDelta = false;

    for (;;) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });

      const events = buffer.split("\n\n");
      buffer = events.pop(); // keep any incomplete trailing event
      for (const raw of events) {
        const line = raw.split("\n").find((l) => l.startsWith("data: "));
        if (!line) continue;
        const event = JSON.parse(line.slice(6));
        if (event.type === "session") setSessionId(event.session_id);
        if (event.type === "delta" && event.text) {
          sawDelta = true;
          appendDelta(event.text);
        }
        if (event.type === "done") setSessionId(event.session_id);
      }
    }

    if (!sawDelta) throw new Error("stream produced no reply");
    finishStream();
  };

  const send = async (text) => {
    const msg = (text || input).trim();
    if (!msg || loading) return;

    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: msg }]);
    setLoading(true);

    try {
      await streamReply(msg);
    } catch {
      // Streaming unavailable — fall back to the non-streaming endpoint.
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
      }
    } finally {
      setLoading(false);
    }
  };

  // Cultural Bridge handoff: /chat?seed=<question> sends the question as the first message.
  useEffect(() => {
    const seed = searchParams.get("seed");
    if (!seed || seedSentRef.current) return;
    seedSentRef.current = true;
    setSearchParams({}, { replace: true });
    send(seed);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchParams]);

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
