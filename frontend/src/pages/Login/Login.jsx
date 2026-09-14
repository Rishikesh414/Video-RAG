import React, { useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "../../hooks/useAuth";
import { authAPI } from "../../services/api";
import "./Login.css";

/**
 * Login page — authenticates students and faculty members.
 * Redirects to the appropriate dashboard based on user role.
 */
function Login() {
  const location = useLocation();
  const [email, setEmail] = useState(location.state?.email || "");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(location.state?.message || "");
  const [isLoading, setIsLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSuccess("");
    setIsLoading(true);

    try {
      const response = await authAPI.login({ email, password });
      const { user, access_token } = response.data;
      login(user, access_token);

      // Redirect based on role
      navigate(user.role === "faculty" ? "/faculty" : "/student");
    } catch (err) {
      setError(err.response?.data?.detail || "Login failed. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="login" id="login-page">
      <div className="login__card">
        <div className="login__header">
          <h1 className="login__title">🎬 VideoRAG</h1>
          <p className="login__subtitle">Next-Gen Video Search & Generation</p>
        </div>

        <form className="login__form" onSubmit={handleSubmit}>
          {success && <div className="login__success">{success}</div>}
          {error && <div className="login__error">{error}</div>}

          <div className="login__field">
            <label htmlFor="email" className="login__label">Email</label>
            <input
              id="email"
              type="email"
              className="login__input"
              placeholder="your@email.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          <div className="login__field">
            <label htmlFor="password" className="login__label">Password</label>
            <input
              id="password"
              type="password"
              className="login__input"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          <button
            id="login-btn"
            type="submit"
            className="login__btn"
            disabled={isLoading}
          >
            {isLoading ? "Signing in..." : "Sign In"}
          </button>

          <div className="login__divider">
            <span>or</span>
          </div>

          <button
            id="register-btn"
            type="button"
            className="login__btn login__btn--secondary"
            onClick={() => navigate("/register")}
          >
            Register
          </button>
        </form>
      </div>
    </div>
  );
}

export default Login;
