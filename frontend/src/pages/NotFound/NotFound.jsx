import React from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../../hooks/useAuth";
import "./NotFound.css";

function NotFound() {
  const { user } = useAuth();
  const defaultPath = user?.role === "faculty" ? "/faculty" : "/student";

  return (
    <div className="not-found" id="not-found-page">
      <div className="not-found__card">
        <span className="not-found__code">404</span>
        <h1 className="not-found__title">Page Not Found</h1>
        <p className="not-found__desc">
          The requested page or lecture resource does not exist in the VideoRAG system.
        </p>
        <Link to={defaultPath} className="not-found__btn">
          Return to Dashboard
        </Link>
      </div>
    </div>
  );
}

export default NotFound;
