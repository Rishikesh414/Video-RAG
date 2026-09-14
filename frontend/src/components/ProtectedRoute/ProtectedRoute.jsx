import React from "react";
import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "../../hooks/useAuth";

/**
 * ProtectedRoute component — enforces login and optional role constraints.
 *
 * @param {Object} props
 * @param {React.ReactNode} props.children - Component to render if allowed
 * @param {string} [props.requiredRole] - "student" | "faculty"
 */
function ProtectedRoute({ children, requiredRole }) {
  const { user, loading } = useAuth();
  const location = useLocation();

  if (loading) {
    return (
      <div
        style={{
          display: "flex",
          height: "100vh",
          alignItems: "center",
          justifyContent: "center",
          backgroundColor: "#0f0f1a",
          color: "#94a3b8",
        }}
      >
        <span>Loading session...</span>
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  if (requiredRole && user.role !== requiredRole) {
    // If student tries to access faculty, redirect to student
    if (user.role === "student") {
      return <Navigate to="/student" replace />;
    }
    // If faculty tries to access student-exclusive, redirect to faculty
    return <Navigate to="/faculty" replace />;
  }

  return children;
}

export default ProtectedRoute;
