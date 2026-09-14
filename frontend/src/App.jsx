import React from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import { ToastProvider } from "./context/ToastContext";
import ToastContainer from "./components/Toast/Toast";
import ProtectedRoute from "./components/ProtectedRoute/ProtectedRoute";

import Login from "./pages/Login/Login";
import Register from "./pages/Register/Register";
import StudentDashboard from "./pages/StudentDashboard/StudentDashboard";
import FacultyDashboard from "./pages/FacultyDashboard/FacultyDashboard";
import VideoLibrary from "./pages/VideoLibrary/VideoLibrary";
import History from "./pages/History/History";
import Settings from "./pages/Settings/Settings";
import NotFound from "./pages/NotFound/NotFound";
import "./App.css";

/**
 * Root application component.
 * Sets up global Auth & Toast context providers and full end-to-end routing.
 */
function App() {
  return (
    <AuthProvider>
      <ToastProvider>
        <Router>
          <div className="app">
            <ToastContainer />
            <Routes>
              {/* Public Authentication Routes */}
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />

              {/* Protected Learning & Faculty Routes */}
              <Route
                path="/student"
                element={
                  <ProtectedRoute>
                    <StudentDashboard />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/faculty"
                element={
                  <ProtectedRoute requiredRole="faculty">
                    <FacultyDashboard />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/library"
                element={
                  <ProtectedRoute>
                    <VideoLibrary />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/history"
                element={
                  <ProtectedRoute>
                    <History />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/settings"
                element={
                  <ProtectedRoute>
                    <Settings />
                  </ProtectedRoute>
                }
              />

              {/* 404 & Redirect */}
              <Route path="/404" element={<NotFound />} />
              <Route path="*" element={<Navigate to="/student" replace />} />
            </Routes>
          </div>
        </Router>
      </ToastProvider>
    </AuthProvider>
  );
}

export default App;
