import React, { useState, useEffect, useRef } from "react";

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL;

function Chat() {
const [tripParams, setTripParams] = useState({
  source: null,
  dest: null,
  days: null,
  budget: null,
  preferences: null,
});
  const [messages, setMessages] = useState([
    {
      type: "system",
      content:
        "👋 Welcome! Tell me about your trip.\n\nExample: I want to travel to Paris for 5 days with a 50000 budget",
    },
  ]);


  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const messagesEndRef = useRef(null);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const sendMessage = async () => {
  if (!input.trim()) return;

  const userMessage = { type: "user", content: input };
  setMessages((prev) => [...prev, userMessage]);

  setInput("");
  setLoading(true);

  try {
    const res = await fetch(`${API_BASE_URL}/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message: input,
        context: tripParams,   
      }),
    });

    const data = await res.json();

    // ✅ Update stored params
    if (data.parameters) {
      setTripParams((prev) => ({
        ...prev,
        ...data.parameters,
      }));
    }

    setMessages((prev) => [
      ...prev,
      {
        type: "assistant",
        content:
          data.status === "complete"
            ? `📅 Your Itinerary\n\n${data.itinerary}`
            : data.message,
      },
    ]);
  } catch (err) {
    setMessages((prev) => [
      ...prev,
      { type: "error", content: "❌ Error connecting to backend" },
    ]);
  }

  setLoading(false);
};

  return (
    <div className="chat-container full-width">
      {/* Messages */}
      <div className="messages-panel">
        {messages.map((msg, index) => (
          <div key={index} className={`message ${msg.type}`}>
            <div className="message-content">
              {msg.content.split("\n").map((line, i) => (
                <p key={i}>{line}</p>
              ))}
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="input-area">
        <div className="input-group">
          <input
            type="text"
            className="chat-input"
            placeholder="Where would you like to go?"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && sendMessage()}
          />
          <button className="send-btn" onClick={sendMessage}>
            Send
          </button>
        </div>

        {loading && (
          <div className="loading-indicator">
            <span className="spinner"></span> Processing...
          </div>
        )}
      </div>
    </div>
  );
}

export default Chat;