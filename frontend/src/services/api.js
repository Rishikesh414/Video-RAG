import axios from "axios";

/**
 * Axios instance pre-configured with the backend API base URL.
 * All API calls should use this instance.
 */
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1",
  headers: {
    "Content-Type": "application/json",
  },
});

// --- Request interceptor: attach auth token ---
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("access_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// --- Response interceptor: handle 401 ---
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("access_token");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

// =====================
// Auth API
// =====================
export const authAPI = {
  login: (credentials) => api.post("/auth/login", credentials),
  register: (userData) => api.post("/auth/register", userData),
};

// =====================
// Upload API (Faculty)
// =====================
export const uploadAPI = {
  uploadVideo: (formData) =>
    api.post("/upload/video", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    }),
  uploadPDF: (formData) =>
    api.post("/upload/pdf", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    }),
  listUploads: () => api.get("/upload/list"),
};

// =====================
// Query API (Student)
// =====================
export const queryAPI = {
  askQuestion: (payload) => api.post("/query/ask", payload),
  getVideoSegment: (segmentId) => api.get(`/query/segment/${segmentId}`),
};

// =====================
// Chat API
// =====================
export const chatAPI = {
  getHistory: () => api.get("/chat/history"),
  deleteHistory: () => api.delete("/chat/history"),
};

export default api;
