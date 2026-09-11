import React, { useState } from "react";
import Sidebar from "../../components/Sidebar/Sidebar";
import ChatWindow from "../../components/ChatWindow/ChatWindow";
import ClipViewer from "../../components/ClipViewer/ClipViewer";
import { queryAPI } from "../../services/api";
import "./StudentDashboard.css";

/**
 * StudentDashboard page — the main interface for students.
 *
 * Uses the hybrid VideoRAG pipeline which returns 3 outputs:
 * 1. Text answer (displayed in chat + ClipViewer)
 * 2. Video clip (displayed in ClipViewer player)
 * 3. Timestamps (displayed in ClipViewer)
 */
function StudentDashboard() {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  // 3-part response state from the hybrid pipeline
  const [currentAnswer, setCurrentAnswer] = useState(null);
  const [currentClip, setCurrentClip] = useState(null);
  const [currentTimestamp, setCurrentTimestamp] = useState(null);
  const [currentSources, setCurrentSources] = useState([]);

  const handleSendMessage = async (content) => {
    // Add user message
    const userMessage = { role: "user", content };
    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    // Reset previous results
    setCurrentAnswer(null);
    setCurrentClip(null);
    setCurrentTimestamp(null);
    setCurrentSources([]);

    try {
      const response = await queryAPI.askQuestion({ question: content });
      const { answer, video_clip, timestamp, sources } = response.data;

      // Add AI response to chat
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: answer?.text || "No answer generated.",
          sources: sources || [],
        },
      ]);

      // Update the 3-part ClipViewer display
      setCurrentAnswer(answer);
      setCurrentClip(video_clip);
      setCurrentTimestamp(timestamp);
      setCurrentSources(sources || []);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Sorry, an error occurred while processing your question. Please try again.",
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="student-dashboard" id="student-dashboard">
      <Sidebar />
      <main className="student-dashboard__main">
        <header className="student-dashboard__header">
          <h1>Student Dashboard</h1>
          <p>Ask questions about your lecture videos — get answers with video evidence</p>
        </header>
        <div className="student-dashboard__content">
          <section className="student-dashboard__chat">
            <ChatWindow
              messages={messages}
              onSendMessage={handleSendMessage}
              isLoading={isLoading}
            />
          </section>
          <section className="student-dashboard__evidence">
            <ClipViewer
              answer={currentAnswer}
              videoClip={currentClip}
              timestamp={currentTimestamp}
              sources={currentSources}
            />
          </section>
        </div>
      </main>
    </div>
  );
}

export default StudentDashboard;
