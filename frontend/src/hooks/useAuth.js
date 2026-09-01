import { useAuthContext } from "../context/AuthContext";

/**
 * Custom hook for authentication actions.
 * Provides user data, login, logout, and loading state.
 */
export function useAuth() {
  const { user, loading, login, logout } = useAuthContext();

  const isAuthenticated = !!user;
  const isStudent = user?.role === "student";
  const isFaculty = user?.role === "faculty";

  return {
    user,
    loading,
    isAuthenticated,
    isStudent,
    isFaculty,
    login,
    logout,
  };
}

export default useAuth;
