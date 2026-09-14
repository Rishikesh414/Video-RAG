import React, { useState } from "react";
import Sidebar from "../../components/Sidebar/Sidebar";
import Navbar from "../../components/Navbar/Navbar";
import ChatWindow from "../../components/ChatWindow/ChatWindow";
import ClipViewer from "../../components/ClipViewer/ClipViewer";
import { queryAPI } from "../../services/api";
import { MODULES } from "../../services/mockData";
import { useToast } from "../../context/ToastContext";
import "./StudentDashboard.css";

/**
 * StudentDashboard page — the primary multimodal learning interface for students.
 *
 * Uses the hybrid VideoRAG pipeline which returns 3 outputs:
 * 1. Grounded Text Answer
 * 2. 30-Second Video Clip
 * 3. Exact Source Timestamps
 */
function StudentDashboard() {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedModule, setSelectedModule] = useState("all");

  // 3-part response state from the hybrid pipeline
  const [currentAnswer, setCurrentAnswer] = useState(null);
  const [currentClip, setCurrentClip] = useState(null);
  const [currentTimestamp, setCurrentTimestamp] = useState(null);
  const [currentSources, setCurrentSources] = useState([]);

  const { showSuccess, showError } = useToast();

  const handleSendMessage = async (content) => {
    // Add user question to messages
    const userMessage = { role: "user", content };
    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const response = await queryAPI.askQuestion({
        question: content,
        module: selectedModule !== "all" ? selectedModule : undefined,
      });

      const { answer, video_clip, timestamp, sources } = response.data;

      // Add assistant response to messages
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: answer?.text || "No answer generated.",
          sources: sources || [],
          confidence: answer?.confidence,
        },
      ]);

      // Update 3-output ClipViewer evidence panel
      setCurrentAnswer(answer);
      setCurrentClip(video_clip);
      setCurrentTimestamp(timestamp);
      setCurrentSources(sources || []);

      showSuccess("Retrieved video evidence & generated answer!");
    } catch (error) {
      console.error(error);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content:
            "Sorry, an error occurred while connecting to the VideoRAG pipeline. Please check your backend connection.",
        },
      ]);
      showError("Failed to query VideoRAG pipeline.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleClearChat = () => {
    setMessages([]);
    setCurrentAnswer(null);
    setCurrentClip(null);
    setCurrentTimestamp(null);
    setCurrentSources([]);
    showSuccess("Conversation cleared.");
  };

  return (
    <div className="student-dashboard" id="student-dashboard">
      <Sidebar />

      <div className="student-dashboard__body">
        <Navbar
          title="Student Multimodal Learning"
          subtitle="Query course lectures — receive precise video clip evidence and verified timestamps"
          selectedModule={selectedModule}
          onSelectModule={setSelectedModule}
          modules={MODULES}
        />

        {/* Module Filter Pills */}
        <div className="student-dashboard__module-bar">
          <span className="student-dashboard__filter-label">Curriculum Focus:</span>
          <div className="student-dashboard__pills">
            {MODULES.map((m) => (
              <button
                key={m.id}
                type="button"
                className={`student-dashboard__pill ${
                  selectedModule === m.id ? "student-dashboard__pill--active" : ""
                }`}
                onClick={() => setSelectedModule(m.id)}
              >
                {m.code ? `[${m.code}] ` : ""}
                {m.title}
              </button>
            ))}
          </div>
        </div>

        <main className="student-dashboard__main">
          <div className="student-dashboard__content">
            {/* Left Column: Chat Conversation */}
            <section className="student-dashboard__chat">
              <ChatWindow
                messages={messages}
                onSendMessage={handleSendMessage}
                isLoading={isLoading}
                onClearChat={handleClearChat}
              />
            </section>

            {/* Right Column: 3-Output Video Evidence & Reasoning */}
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
    </div>
  );
}

export default StudentDashboard;
