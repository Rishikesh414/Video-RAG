import React, { useState } from "react";
import "./SearchBar.css";

/**
 * SearchBar component — a styled search input with submit functionality.
 *
 * @param {Object} props
 * @param {Function} props.onSearch - Callback with search query string
 * @param {string} props.placeholder - Placeholder text
 */
function SearchBar({ onSearch, placeholder = "Search videos..." }) {
  const [query, setQuery] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    if (query.trim()) {
      onSearch(query.trim());
    }
  };

  return (
    <form className="search-bar" onSubmit={handleSubmit} id="search-bar">
      <input
        type="text"
        className="search-bar__input"
        placeholder={placeholder}
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        id="search-input"
      />
      <button type="submit" className="search-bar__btn" id="search-btn">
        🔍
      </button>
    </form>
  );
}

export default SearchBar;
