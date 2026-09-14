import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import Sidebar from "../../components/Sidebar/Sidebar";
import Navbar from "../../components/Navbar/Navbar";
import SearchBar from "../../components/SearchBar/SearchBar";
import VideoPlayer from "../../components/VideoPlayer/VideoPlayer";
import { MODULES, MOCK_LECTURES } from "../../services/mockData";
import "./VideoLibrary.css";

/**
 * VideoLibrary page — allows students and faculty to browse indexed lectures
 * across modules M1–M4, inspect transcripts, visual tags, and watch videos.
 */
function VideoLibrary() {
  const [selectedModule, setSelectedModule] = useState("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [activeLecture, setActiveLecture] = useState(null);
  const navigate = useNavigate();

  const filteredLectures = MOCK_LECTURES.filter((lec) => {
    if (selectedModule !== "all" && lec.moduleId !== selectedModule) return false;
    if (
      searchQuery.trim() &&
      !lec.title.toLowerCase().includes(searchQuery.toLowerCase()) &&
      !lec.summary.toLowerCase().includes(searchQuery.toLowerCase()) &&
      !lec.visualTags.some((t) => t.toLowerCase().includes(searchQuery.toLowerCase()))
    ) {
      return false;
    }
    return true;
  });

  const handleAskAboutLecture = (lecture) => {
    navigate("/student", {
      state: {
        presetQuery: `What are the core concepts covered in ${lecture.title}?`,
      },
    });
  };

  return (
    <div className="video-library" id="video-library">
      <Sidebar />

      <div className="video-library__body">
        <Navbar
          title="Curriculum Video Library"
          subtitle="Explore indexed lectures across all 4 modules with timestamped key moments and transcripts"
          selectedModule={selectedModule}
          onSelectModule={setSelectedModule}
          modules={MODULES}
        />

        <main className="video-library__main">
          {/* Top Control Bar: Search + Module Pills */}
          <div className="video-library__controls">
            <SearchBar
              onSearch={setSearchQuery}
              placeholder="Search lectures, topics (e.g. backprop, attention, ResNet)..."
            />

            <div className="video-library__pills">
              {MODULES.map((m) => (
                <button
                  key={m.id}
                  type="button"
                  className={`video-library__pill ${
                    selectedModule === m.id ? "video-library__pill--active" : ""
                  }`}
                  onClick={() => setSelectedModule(m.id)}
                >
                  {m.code ? `[${m.code}] ` : ""}
                  {m.title}
                </button>
              ))}
            </div>
          </div>

          {/* Lecture Cards Grid */}
          <div className="video-library__grid">
            {filteredLectures.length === 0 ? (
              <div className="video-library__empty">
                <p>No lectures found matching your search.</p>
              </div>
            ) : (
              filteredLectures.map((lec) => (
                <div key={lec.id} className="video-library__card" id={`lecture-${lec.id}`}>
                  {/* Thumbnail / Video Preview */}
                  <div
                    className="video-library__thumbnail-wrapper"
                    onClick={() => setActiveLecture(lec)}
                  >
                    <img
                      src={lec.thumbnail}
                      alt={lec.title}
                      className="video-library__thumbnail"
                    />
                    <span className="video-library__duration">{lec.duration}</span>
                    <span className="video-library__module-tag">{lec.moduleCode}</span>
                    <div className="video-library__play-overlay">
                      <span className="video-library__play-icon">▶</span>
                    </div>
                  </div>

                  {/* Card Content */}
                  <div className="video-library__card-content">
                    <div className="video-library__card-meta">
                      <span>👤 {lec.instructor}</span>
                      <span>📅 {lec.uploadDate}</span>
                    </div>

                    <h3
                      className="video-library__card-title"
                      onClick={() => setActiveLecture(lec)}
                      title={lec.title}
                    >
                      {lec.title}
                    </h3>

                    <p className="video-library__card-summary">{lec.summary}</p>

                    {/* Visual Tags */}
                    <div className="video-library__tags">
                      {lec.visualTags.map((tag, i) => (
                        <span key={i} className="video-library__tag">
                          #{tag}
                        </span>
                      ))}
                    </div>

                    {/* Stats & Actions */}
                    <div className="video-library__card-footer">
                      <div className="video-library__card-stats">
                        <span>📊 {lec.transcriptionChunks} chunks</span>
                        <span>🧠 {lec.vectorCount} vectors</span>
                      </div>

                      <div className="video-library__card-buttons">
                        <button
                          type="button"
                          className="video-library__btn video-library__btn--watch"
                          onClick={() => setActiveLecture(lec)}
                        >
                          ▶ Watch Lecture
                        </button>
                        <button
                          type="button"
                          className="video-library__btn video-library__btn--ask"
                          onClick={() => handleAskAboutLecture(lec)}
                        >
                          💬 Ask AI
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </main>
      </div>

      {/* Video Modal Player */}
      {activeLecture && (
        <div className="video-library__modal" onClick={() => setActiveLecture(null)}>
          <div
            className="video-library__modal-content"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="video-library__modal-header">
              <div>
                <h3>{activeLecture.title}</h3>
                <span>Instructor: {activeLecture.instructor} | Module {activeLecture.moduleCode}</span>
              </div>
              <button
                type="button"
                className="video-library__modal-close"
                onClick={() => setActiveLecture(null)}
              >
                ✕
              </button>
            </div>

            <div className="video-library__modal-player">
              <VideoPlayer
                src={activeLecture.videoUrl}
                title={activeLecture.title}
                markers={[
                  { time: 180, label: "Core Formulation" },
                  { time: 600, label: "Visual Diagram Breakdown" },
                  { time: 1200, label: "Mathematical Proof" },
                ]}
              />
            </div>

            <div className="video-library__modal-footer">
              <p>{activeLecture.summary}</p>
              <button
                type="button"
                className="video-library__btn video-library__btn--ask"
                onClick={() => handleAskAboutLecture(activeLecture)}
              >
                💬 Ask VideoRAG Questions About This Lecture
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default VideoLibrary;
