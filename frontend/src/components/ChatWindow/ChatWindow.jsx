import React, { useState, useRef, useEffect } from "react";
import "./ChatWindow.css";

/**
 * ChatWindow component — displays the conversation history and input box
 * for student queries. Renders messages from both user and AI.
 *
 * @param {Object} props
 * @param {Array} props.messages - Array of { role, content, timestamp, sources? }
 * @param {Function} props.onSendMessage - Callback when user sends a message
 * @param {boolean} props.isLoading - Whether the AI is generating a response
 */
function ChatWindow({ messages = [], onSendMessage, isLoading = false }) {
  const [input, setInput] = useState("");
  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;
    onSendMessage(input.trim());
    setInput("");
  };

  return (
    <div className="chat-window" id="chat-window">
      <div className="chat-window__messages">
        {messages.length === 0 && (
          <div className="chat-window__empty">
            <p>Ask a question about your lecture videos...</p>
          </div>
        )}
        {messages.map((msg, index) => (
          <div
            key={index}
            className={`chat-window__message chat-window__message--${msg.role}`}
          >
            <div className="chat-window__message-content">{msg.content}</div>
            {msg.sources && (
              <div className="chat-window__sources">
                <span>📎 Sources: {msg.sources.join(", ")}</span>
              </div>
            )}
          </div>
        ))}
        {isLoading && (
          <div className="chat-window__message chat-window__message--assistant">
            <div className="chat-window__typing">
              <span></span><span></span><span></span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <form className="chat-window__input-form" onSubmit={handleSubmit}>
        <input
          id="chat-input"
          type="text"
          className="chat-window__input"
          placeholder="Type your question..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={isLoading}
        />
        <button
          id="chat-send-btn"
          type="submit"
          className="chat-window__send-btn"
          disabled={!input.trim() || isLoading}
        >
          Send
        </button>
      </form>
    </div>
  );
}

export default ChatWindow;
