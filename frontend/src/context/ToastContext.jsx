import React, { createContext, useContext, useState, useCallback } from "react";

const ToastContext = createContext(null);

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([]);

  const removeToast = useCallback((id) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  const showToast = useCallback((message, type = "info", duration = 4000) => {
    const id = Date.now() + Math.random().toString(36).substring(2, 5);
    const newToast = { id, message, type, duration };
    setToasts((prev) => [...prev, newToast]);

    if (duration > 0) {
      setTimeout(() => {
        removeToast(id);
      }, duration);
    }
    return id;
  }, [removeToast]);

  const showSuccess = useCallback((msg, dur) => showToast(msg, "success", dur), [showToast]);
  const showError = useCallback((msg, dur) => showToast(msg, "error", dur), [showToast]);
  const showInfo = useCallback((msg, dur) => showToast(msg, "info", dur), [showToast]);
  const showWarning = useCallback((msg, dur) => showToast(msg, "warning", dur), [showToast]);

  return (
    <ToastContext.Provider
      value={{ toasts, showToast, showSuccess, showError, showInfo, showWarning, removeToast }}
    >
      {children}
    </ToastContext.Provider>
  );
}

export function useToast() {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error("useToast must be used within a ToastProvider");
  }
  return context;
}

export default ToastContext;
