import React, { useState, useRef, useEffect } from "react";
import { SAMPLE_QUESTIONS } from "../../services/mockData";
import { useToast } from "../../context/ToastContext";
import "./ChatWindow.css";

/**
 * Enhanced ChatWindow component.
 *
 * @param {Object} props
 * @param {Array} props.messages - Array of { role, content, timestamp, sources?, confidence? }
 * @param {Function} props.onSendMessage - Callback when user submits a question
 * @param {boolean} props.isLoading - Generation state
 * @param {Function} [props.onClearChat] - Callback to clear messages
 */
function ChatWindow({
  messages = [],
  onSendMessage,
  isLoading = false,
  onClearChat,
}) {
  const [input, setInput] = useState("");
  const messagesEndRef = useRef(null);
  const { showSuccess } = useToast();

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;
    onSendMessage(input.trim());
    setInput("");
  };

  const handleSuggestionClick = (question) => {
    if (isLoading) return;
    onSendMessage(question);
  };

  const copyMessage = (text) => {
    navigator.clipboard.writeText(text);
    showSuccess("Message copied to clipboard!");
  };

  return (
    <div className="chat-window" id="chat-window">
      {/* Chat Header Bar */}
      <div className="chat-window__header">
        <div className="chat-window__header-info">
          <span className="chat-window__header-title">Multimodal Q&A</span>
          <span className="chat-window__header-desc">Ask questions across all indexed lectures</span>
        </div>

        {messages.length > 0 && onClearChat && (
          <button
            type="button"
            className="chat-window__clear-btn"
            onClick={onClearChat}
            title="Clear current conversation"
          >
            🗑 Clear
          </button>
        )}
      </div>

      {/* Messages Scroll Area */}
      <div className="chat-window__messages">
        {messages.length === 0 && (
          <div className="chat-window__empty">
            <div className="chat-window__empty-icon">💬</div>
            <h3>What would you like to learn from your lectures?</h3>
            <p>
              Ask any conceptual or timestamp-specific question. VideoRAG will retrieve the exact
              video evidence and deliver a grounded multimodal response.
            </p>

            {/* Quick Suggestion Chips */}
            <div className="chat-window__suggestions">
              <span className="chat-window__suggestions-title">Try asking:</span>
              <div className="chat-window__chips-grid">
                {SAMPLE_QUESTIONS.map((q, idx) => (
                  <button
                    key={idx}
                    type="button"
                    className="chat-window__chip"
                    onClick={() => handleSuggestionClick(q)}
                  >
                    "{q}"
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

        {messages.map((msg, index) => (
          <div
            key={index}
            className={`chat-window__message chat-window__message--${msg.role}`}
          >
            <div className="chat-window__message-header">
              <span className="chat-window__sender-name">
                {msg.role === "user" ? "You" : "🤖 VideoRAG Assistant"}
              </span>
              <div className="chat-window__message-actions">
                {msg.role === "assistant" && (
                  <button
                    type="button"
                    className="chat-window__msg-action"
                    onClick={() => copyMessage(msg.content)}
                    title="Copy response"
                  >
                    📋
                  </button>
                )}
              </div>
            </div>

            <div className="chat-window__message-content">
              {msg.content}
            </div>

            {msg.sources && msg.sources.length > 0 && (
              <div className="chat-window__sources">
                <span className="chat-window__sources-label">📎 Evidence Sources:</span>
                {msg.sources.map((src, i) => (
                  <span key={i} className="chat-window__source-pill">
                    {src}
                  </span>
                ))}
              </div>
            )}
          </div>
        ))}

        {isLoading && (
          <div className="chat-window__message chat-window__message--assistant">
            <div className="chat-window__sender-name">🤖 VideoRAG Assistant</div>
            <div className="chat-window__loading-state">
              <div className="chat-window__typing">
                <span></span>
                <span></span>
                <span></span>
              </div>
              <span className="chat-window__loading-text">
                Retrieving vector chunks & extracting video clip evidence...
              </span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Form */}
      <form className="chat-window__input-form" onSubmit={handleSubmit}>
        <input
          id="chat-input"
          type="text"
          className="chat-window__input"
          placeholder="Ask a question about lecture concepts or timestamps... (Press Enter)"
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
          {isLoading ? "Searching..." : "Ask VideoRAG 🚀"}
        </button>
      </form>
    </div>
  );
}

export default ChatWindow;
