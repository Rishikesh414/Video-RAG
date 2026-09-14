import React from "react";
import { useAuth } from "../../hooks/useAuth";
import "./Navbar.css";

/**
 * Top Navbar header displayed above dashboard and content pages.
 *
 * @param {Object} props
 * @param {string} props.title - Current page title
 * @param {string} props.subtitle - Page subtitle or context description
 * @param {string} [props.selectedModule] - Selected curriculum module ID (e.g. "all", "m1")
 * @param {Function} [props.onSelectModule] - Callback when module is switched
 * @param {Array} [props.modules] - List of modules
 */
function Navbar({
  title = "VideoRAG",
  subtitle = "Next-Gen Video Search & Generation",
  selectedModule = "all",
  onSelectModule,
  modules = [],
}) {
  const { user } = useAuth();

  return (
    <header className="navbar" id="app-navbar">
      <div className="navbar__left">
        <h1 className="navbar__title">{title}</h1>
        {subtitle && <span className="navbar__subtitle">{subtitle}</span>}
      </div>

      <div className="navbar__right">
        {/* Module Selector Pill */}
        {modules.length > 0 && onSelectModule && (
          <div className="navbar__module-picker">
            <span className="navbar__picker-label">Module:</span>
            <select
              className="navbar__select"
              value={selectedModule}
              onChange={(e) => onSelectModule(e.target.value)}
              id="navbar-module-select"
            >
              {modules.map((m) => (
                <option key={m.id} value={m.id}>
                  {m.code ? `[${m.code}] ` : ""}
                  {m.title}
                </option>
              ))}
            </select>
          </div>
        )}

        {/* System Health Status Badge */}
        <div className="navbar__status" title="Hybrid Pipeline (Whisper + Qdrant + Multimodal LLM) Online">
          <span className="navbar__status-dot"></span>
          <span className="navbar__status-text">Pipeline Ready</span>
        </div>

        {/* User Profile Pill */}
        {user && (
          <div className="navbar__profile" id="navbar-profile">
            <div className="navbar__avatar">
              {user.name ? user.name.charAt(0).toUpperCase() : "U"}
            </div>
            <div className="navbar__user-info">
              <span className="navbar__user-name">{user.name}</span>
              <span className={`navbar__user-role navbar__user-role--${user.role}`}>
                {user.role}
              </span>
            </div>
          </div>
        )}
      </div>
    </header>
  );
}

export default Navbar;
