import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import Sidebar from "../../components/Sidebar/Sidebar";
import Navbar from "../../components/Navbar/Navbar";
import { chatAPI, getStoredChats } from "../../services/api";
import { useToast } from "../../context/ToastContext";
import "./History.css";

/**
 * History page — displays past Q&A queries, retrieved video timestamps,
 * and allows re-examining the video clips in the Student Dashboard.
 */
function History() {
  const [history, setHistory] = useState([]);
  const [searchQuery, setSearchQuery] = useState("");
  const navigate = useNavigate();
  const { showSuccess, showInfo } = useToast();

  const loadHistory = async () => {
    try {
      const res = await chatAPI.getHistory();
      const items = res.data?.history || [];
      if (items.length > 0) {
        setHistory(items);
      } else {
        // Sample mock history if empty
        const local = getStoredChats();
        setHistory(
          local.length > 0
            ? local
            : [
                {
                  id: 1,
                  question: "Explain backpropagation and gradient flow through weights",
                  answer: {
                    text: "Backpropagation computes the gradient of the loss function with respect to weights using the multivariate chain rule backwards from the loss to the input.",
                    confidence: "high",
                  },
                  timestamp: {
                    formatted_start: "04:15",
                    formatted_end: "04:47",
                    video_id: "Lecture 01: Neural Network Foundations",
                  },
                  created_at: new Date(Date.now() - 3600000).toISOString(),
                },
                {
                  id: 2,
                  question: "How does ResNet solve the vanishing gradient problem?",
                  answer: {
                    text: "Residual skip connections F(x) + x allow the gradient to propagate directly back through the identity path without attenuation.",
                    confidence: "high",
                  },
                  timestamp: {
                    formatted_start: "18:30",
                    formatted_end: "18:58",
                    video_id: "Lecture 04: Convolutional Architectures",
                  },
                  created_at: new Date(Date.now() - 86400000).toISOString(),
                },
              ]
        );
      }
    } catch {
      // fallback
    }
  };

  useEffect(() => {
    loadHistory();
  }, []);

  const handleClearHistory = async () => {
    await chatAPI.deleteHistory();
    setHistory([]);
    showSuccess("Query history cleared.");
  };

  const handleReopenInDashboard = (item) => {
    navigate("/student", {
      state: {
        presetQuery: item.question,
      },
    });
  };

  const filteredHistory = history.filter((item) => {
    if (!searchQuery.trim()) return true;
    const q = searchQuery.toLowerCase();
    return (
      item.question?.toLowerCase().includes(q) ||
      item.answer?.text?.toLowerCase().includes(q) ||
      item.timestamp?.video_id?.toLowerCase().includes(q)
    );
  });

  return (
    <div className="history-page" id="history-page">
      <Sidebar />

      <div className="history-page__body">
        <Navbar
          title="Query & Q&A History"
          subtitle="Review previous multimodal queries, timestamps, and video evidence"
        />

        <main className="history-page__main">
          <div className="history-page__header-bar">
            <input
              type="text"
              placeholder="Search past questions or lecture topics..."
              className="history-page__search"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />

            {history.length > 0 && (
              <button
                type="button"
                className="history-page__clear-btn"
                onClick={handleClearHistory}
              >
                🗑 Clear History
              </button>
            )}
          </div>

          <div className="history-page__list">
            {filteredHistory.length === 0 ? (
              <div className="history-page__empty">
                <div className="history-page__empty-icon">📜</div>
                <h3>No Query History Found</h3>
                <p>
                  Questions you ask on the Student Dashboard will be saved here along with their
                  corresponding video clips and timestamps.
                </p>
                <button
                  type="button"
                  className="history-page__ask-btn"
                  onClick={() => navigate("/student")}
                >
                  Go to Student Q&A
                </button>
              </div>
            ) : (
              filteredHistory.map((item) => (
                <div key={item.id} className="history-page__card">
                  <div className="history-page__card-header">
                    <span className="history-page__card-date">
                      {item.created_at
                        ? new Date(item.created_at).toLocaleString()
                        : "Recent"}
                    </span>
                    {item.answer?.confidence && (
                      <span className="history-page__confidence-badge">
                        ● {item.answer.confidence.toUpperCase()} CONFIDENCE
                      </span>
                    )}
                  </div>

                  <h3 className="history-page__question">"{item.question}"</h3>

                  <p className="history-page__answer">{item.answer?.text}</p>

                  {item.timestamp && (
                    <div className="history-page__timestamp-bar">
                      <span>⏱ Moment: <strong>{item.timestamp.formatted_start} – {item.timestamp.formatted_end}</strong></span>
                      {item.timestamp.video_id && (
                        <span>📹 {item.timestamp.video_id}</span>
                      )}
                    </div>
                  )}

                  <div className="history-page__card-actions">
                    <button
                      type="button"
                      className="history-page__action-btn"
                      onClick={() => handleReopenInDashboard(item)}
                    >
                      ▶ Re-examine Video Evidence Clip
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        </main>
      </div>
    </div>
  );
}

export default History;
