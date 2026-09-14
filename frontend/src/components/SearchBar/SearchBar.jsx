import React, { useState } from "react";
import "./SearchBar.css";

/**
 * Enhanced SearchBar component.
 *
 * @param {Object} props
 * @param {Function} props.onSearch - Callback with search query string
 * @param {string} [props.placeholder] - Placeholder text
 * @param {string} [props.initialValue] - Initial query string
 * @param {Function} [props.onClear] - Callback when cleared
 */
function SearchBar({
  onSearch,
  placeholder = "Search lectures, concepts, or timestamps...",
  initialValue = "",
  onClear,
}) {
  const [query, setQuery] = useState(initialValue);

  const handleSubmit = (e) => {
    e.preventDefault();
    onSearch?.(query.trim());
  };

  const handleClear = () => {
    setQuery("");
    onClear?.();
    onSearch?.("");
  };

  return (
    <form className="search-bar" onSubmit={handleSubmit} id="search-bar">
      <span className="search-bar__icon">🔍</span>
      <input
        type="text"
        className="search-bar__input"
        placeholder={placeholder}
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        id="search-input"
      />
      {query && (
        <button
          type="button"
          className="search-bar__clear"
          onClick={handleClear}
          title="Clear search"
        >
          ✕
        </button>
      )}
      <button type="submit" className="search-bar__btn" id="search-btn">
        Search
      </button>
    </form>
  );
}

export default SearchBar;
