import React from "react";
import { NavLink } from "react-router-dom";
import { useAuth } from "../../hooks/useAuth";
import "./Sidebar.css";

/**
 * Sidebar navigation component.
 * Displays nav links based on user role (student/faculty) and a logout button.
 */
function Sidebar() {
  const { user, logout } = useAuth();

  return (
    <aside className="sidebar" id="sidebar">
      <div className="sidebar__brand">
        <h2 className="sidebar__logo">🎬 VideoRAG</h2>
      </div>

      <nav className="sidebar__nav">
        {user?.role === "student" && (
          <NavLink to="/student" className="sidebar__link" id="nav-student">
            💬 Ask Questions
          </NavLink>
        )}
        {user?.role === "faculty" && (
          <NavLink to="/faculty" className="sidebar__link" id="nav-faculty">
            📤 Upload Content
          </NavLink>
        )}
      </nav>

      <div className="sidebar__footer">
        {user && (
          <div className="sidebar__user">
            <span className="sidebar__user-name">{user.name}</span>
            <span className="sidebar__user-role">{user.role}</span>
          </div>
        )}
        <button className="sidebar__logout" onClick={logout} id="logout-btn">
          Logout
        </button>
      </div>
    </aside>
  );
}

export default Sidebar;
