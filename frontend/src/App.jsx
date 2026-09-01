import React from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import Login from "./pages/Login/Login";
import StudentDashboard from "./pages/StudentDashboard/StudentDashboard";
import FacultyDashboard from "./pages/FacultyDashboard/FacultyDashboard";
import "./App.css";

/**
 * Root application component.
 * Sets up routing for Login, Student Dashboard, and Faculty Dashboard.
 */
function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="app">
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/student" element={<StudentDashboard />} />
            <Route path="/faculty" element={<FacultyDashboard />} />
            <Route path="*" element={<Navigate to="/login" replace />} />
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;
