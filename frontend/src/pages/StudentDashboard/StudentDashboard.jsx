import React, { useState } from "react";
import Sidebar from "../../components/Sidebar/Sidebar";
import ChatWindow from "../../components/ChatWindow/ChatWindow";
import VideoPlayer from "../../components/VideoPlayer/VideoPlayer";
import { queryAPI } from "../../services/api";
import "./StudentDashboard.css";

/**
 * StudentDashboard page — the main interface for students.
 * Contains a chat window for asking questions and a video player
 * that displays the evidence video segment.
 */
function StudentDashboard() {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [videoSrc, setVideoSrc] = useState("");
  const [videoTitle, setVideoTitle] = useState("");
  const [videoStartTime, setVideoStartTime] = useState(0);

  const handleSendMessage = async (content) => {
    // Add user message
    const userMessage = { role: "user", content };
    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const response = await queryAPI.askQuestion({ question: content });
      const { answer, sources, video_segment } = response.data;

      // Add AI response
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: answer, sources },
      ]);

      // Update video player if a segment was returned
      if (video_segment) {
        setVideoSrc(video_segment.url);
        setVideoTitle(video_segment.title);
        setVideoStartTime(video_segment.start_time || 0);
      }
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
          <p>Ask questions about your lecture videos and get evidence-based answers</p>
        </header>
        <div className="student-dashboard__content">
          <section className="student-dashboard__chat">
            <ChatWindow
              messages={messages}
              onSendMessage={handleSendMessage}
              isLoading={isLoading}
            />
          </section>
          <section className="student-dashboard__video">
            <VideoPlayer
              src={videoSrc}
              title={videoTitle}
              startTime={videoStartTime}
            />
          </section>
        </div>
      </main>
    </div>
  );
}

export default StudentDashboard;
