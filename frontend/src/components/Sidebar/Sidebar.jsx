import React, { useState } from "react";
import { NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../../hooks/useAuth";
import { useToast } from "../../context/ToastContext";
import "./Sidebar.css";

/**
 * Enhanced Sidebar navigation component.
 * Features responsive navigation, badge counters, role indicators, and settings.
 */
function Sidebar() {
  const { user, logout } = useAuth();
  const { showInfo } = useToast();
  const navigate = useNavigate();
  const [collapsed, setCollapsed] = useState(false);

  const handleLogout = () => {
    logout();
    showInfo("Signed out successfully.");
    navigate("/login");
  };

  return (
    <aside className={`sidebar ${collapsed ? "sidebar--collapsed" : ""}`} id="sidebar">
      {/* Brand Header */}
      <div className="sidebar__brand">
        <NavLink to={user?.role === "faculty" ? "/faculty" : "/student"} className="sidebar__brand-link">
          <span className="sidebar__logo-icon">🎬</span>
          {!collapsed && <span className="sidebar__logo-text">VideoRAG</span>}
        </NavLink>
        <button
          type="button"
          className="sidebar__toggle"
          onClick={() => setCollapsed(!collapsed)}
          title={collapsed ? "Expand sidebar" : "Collapse sidebar"}
          aria-label="Toggle sidebar"
        >
          {collapsed ? "»" : "«"}
        </button>
      </div>

      {/* Main Navigation */}
      <nav className="sidebar__nav">
        <div className="sidebar__nav-section">
          {!collapsed && <span className="sidebar__section-title">Main Workspaces</span>}

          {/* Student Q&A */}
          <NavLink
            to="/student"
            className={({ isActive }) =>
              `sidebar__link ${isActive ? "sidebar__link--active" : ""}`
            }
            id="nav-student"
            title="Ask Questions & View Video Evidence"
          >
            <span className="sidebar__icon">💬</span>
            {!collapsed && <span className="sidebar__link-text">Q&A Evidence</span>}
          </NavLink>

          {/* Course Library (Available to both students & faculty) */}
          <NavLink
            to="/library"
            className={({ isActive }) =>
              `sidebar__link ${isActive ? "sidebar__link--active" : ""}`
            }
            id="nav-library"
            title="Browse Curriculum Modules & Lectures"
          >
            <span className="sidebar__icon">📚</span>
            {!collapsed && (
              <>
                <span className="sidebar__link-text">Video Library</span>
                <span className="sidebar__badge">M1–M4</span>
              </>
            )}
          </NavLink>

          {/* Query History */}
          <NavLink
            to="/history"
            className={({ isActive }) =>
              `sidebar__link ${isActive ? "sidebar__link--active" : ""}`
            }
            id="nav-history"
            title="View Past Questions & Answers"
          >
            <span className="sidebar__icon">📜</span>
            {!collapsed && <span className="sidebar__link-text">Query History</span>}
          </NavLink>
        </div>

        {/* Faculty Admin Section */}
        {user?.role === "faculty" && (
          <div className="sidebar__nav-section">
            {!collapsed && <span className="sidebar__section-title">Faculty Admin</span>}
            <NavLink
              to="/faculty"
              className={({ isActive }) =>
                `sidebar__link ${isActive ? "sidebar__link--active" : ""}`
              }
              id="nav-faculty"
              title="Upload Lectures, PDFs & Monitor Indexing Pipeline"
            >
              <span className="sidebar__icon">📤</span>
              {!collapsed && (
                <>
                  <span className="sidebar__link-text">Upload & Pipeline</span>
                  <span className="sidebar__badge sidebar__badge--accent">Admin</span>
                </>
              )}
            </NavLink>
          </div>
        )}

        {/* System & Settings */}
        <div className="sidebar__nav-section">
          {!collapsed && <span className="sidebar__section-title">Preferences</span>}
          <NavLink
            to="/settings"
            className={({ isActive }) =>
              `sidebar__link ${isActive ? "sidebar__link--active" : ""}`
            }
            id="nav-settings"
            title="System Status, AI Models & Profile Settings"
          >
            <span className="sidebar__icon">⚙️</span>
            {!collapsed && <span className="sidebar__link-text">Settings & Info</span>}
          </NavLink>
        </div>
      </nav>

      {/* Footer / User Profile & Logout */}
      <div className="sidebar__footer">
        {user && !collapsed && (
          <div className="sidebar__user">
            <div className="sidebar__user-avatar">
              {user.name ? user.name.charAt(0).toUpperCase() : "U"}
            </div>
            <div className="sidebar__user-details">
              <span className="sidebar__user-name">{user.name}</span>
              <span className="sidebar__user-role">{user.role}</span>
            </div>
          </div>
        )}

        <button
          className="sidebar__logout"
          onClick={handleLogout}
          id="logout-btn"
          title="Log out of VideoRAG"
        >
          <span className="sidebar__logout-icon">⎋</span>
          {!collapsed && <span>Sign Out</span>}
        </button>
      </div>
    </aside>
  );
}

export default Sidebar;
