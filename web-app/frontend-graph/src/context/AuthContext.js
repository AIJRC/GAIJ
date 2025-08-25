import React, { createContext, useState, useEffect } from "react";

// Create authentication context
export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true); // New loading state

  // Check if the user is already logged in (e.g., from localStorage)
  useEffect(() => {
    const storedAuth = localStorage.getItem("isAuthenticated") === "true";
    setIsAuthenticated(storedAuth);
    setLoading(false); // Ensure loading completes
  }, []);

  // Mock login function
  const login = (callback) => {
    setIsAuthenticated(true);
    localStorage.setItem("isAuthenticated", "true");
    if (callback) callback();
  };

  // Mock logout function
  const logout = () => {
    setIsAuthenticated(false);
    localStorage.removeItem("isAuthenticated");
  };

  return (
    <AuthContext.Provider value={{ isAuthenticated, login, logout, loading }}>
      {!loading && children} {/* Don't render until loading completes */}
    </AuthContext.Provider>
  );
};
