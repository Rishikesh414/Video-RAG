import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../../hooks/useAuth";
import { authAPI } from "../../services/api";
import "./Register.css";

/**
 * Register page — handles registration for new students and faculty members.
 */
function Register() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [role, setRole] = useState("student");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    // Client-side validations
    if (!name.trim()) {
      setError("Please enter your full name.");
      return;
    }

    if (password.length < 6) {
      setError("Password must be at least 6 characters long.");
      return;
    }

    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    setIsLoading(true);

    try {
      // 1. Register user
      await authAPI.register({
        name: name.trim(),
        email: email.trim(),
        password,
        role,
      });

      // 2. Automatically log in upon successful registration
      try {
        const loginResponse = await authAPI.login({
          email: email.trim(),
          password,
        });
        const { user, access_token } = loginResponse.data;
        login(user, access_token);
        navigate(user.role === "faculty" ? "/faculty" : "/student");
      } catch {
        // Fallback: If auto-login fails, navigate to login with success state
        navigate("/login", {
          state: {
            message: "Account created successfully! Please sign in with your credentials.",
            email: email.trim(),
          },
        });
      }
    } catch (err) {
      const detail = err.response?.data?.detail;
      setError(
        typeof detail === "string"
          ? detail
          : "Registration failed. Please check your details and try again."
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="register" id="register-page">
      <div className="register__card">
        <div className="register__header">
          <h1 className="register__title">🎬 VideoRAG</h1>
          <p className="register__subtitle">Create your account to get started</p>
        </div>

        <form className="register__form" onSubmit={handleSubmit}>
          {error && <div className="register__error">{error}</div>}

          {/* Full Name */}
          <div className="register__field">
            <label htmlFor="reg-name" className="register__label">
              Full Name
            </label>
            <input
              id="reg-name"
              type="text"
              className="register__input"
              placeholder="Dr. Jane Doe / John Smith"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
            />
          </div>

          {/* Email */}
          <div className="register__field">
            <label htmlFor="reg-email" className="register__label">
              Email Address
            </label>
            <input
              id="reg-email"
              type="email"
              className="register__input"
              placeholder="you@university.edu"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          {/* Role Selection */}
          <div className="register__field">
            <label className="register__label">Select Role</label>
            <div className="register__roles">
              <button
                type="button"
                className={`register__role-btn ${
                  role === "student" ? "register__role-btn--active" : ""
                }`}
                onClick={() => setRole("student")}
              >
                <span className="register__role-icon">🎓</span>
                <span>Student</span>
              </button>
              <button
                type="button"
                className={`register__role-btn ${
                  role === "faculty" ? "register__role-btn--active" : ""
                }`}
                onClick={() => setRole("faculty")}
              >
                <span className="register__role-icon">👨‍🏫</span>
                <span>Faculty</span>
              </button>
            </div>
          </div>

          {/* Password */}
          <div className="register__field">
            <label htmlFor="reg-password" className="register__label">
              Password
            </label>
            <input
              id="reg-password"
              type="password"
              className="register__input"
              placeholder="Minimum 6 characters"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          {/* Confirm Password */}
          <div className="register__field">
            <label htmlFor="reg-confirm-password" className="register__label">
              Confirm Password
            </label>
            <input
              id="reg-confirm-password"
              type="password"
              className="register__input"
              placeholder="Re-enter password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
            />
          </div>

          {/* Submit Button */}
          <button
            id="register-submit-btn"
            type="submit"
            className="register__btn"
            disabled={isLoading}
          >
            {isLoading ? "Creating Account..." : "Create Account"}
          </button>

          {/* Already have an account link */}
          <div className="register__footer">
            <span>Already have an account? </span>
            <Link to="/login" className="register__login-link">
              Sign In
            </Link>
          </div>
        </form>
      </div>
    </div>
  );
}

export default Register;
