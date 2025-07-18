import React, { useState, useContext } from "react";
import { Link, useHistory } from "react-router-dom";
import { AuthContext } from "../context/AuthContext"; // Import Auth Context
import "./Navbar.css";

const Navbar = () => {
  const [isOpen, setIsOpen] = useState(false);
  const { isAuthenticated, logout, loading } = useContext(AuthContext); // Remove unused `login`
  const history = useHistory();

  const handleAuth = () => {
    if (isAuthenticated) {
      logout(); // Log out user
      history.push("/"); // Redirect to home
    } else {
      history.push("/login"); // Redirect to login
    }
  };

  return (
    <nav className="navbar">
      {/* Logo (left-aligned) */}
      <div className="navbar-logo">
        <img src="/gaij_logo.png" alt="GAIJ Logo" />
      </div>

      {/* Hamburger Menu Icon (Small Screens) */}
      <div className="menu-icon" onClick={() => setIsOpen(!isOpen)}>
        ☰
      </div>

      {/* Don't render Navbar links until auth state is determined */}
      {!loading && (
        <div className={`navbar-links ${isOpen ? "open" : ""}`}>
          <Link to="/about" onClick={() => setIsOpen(false)}>About</Link>
          {isAuthenticated && <Link to="/explore" onClick={() => setIsOpen(false)}>Explore</Link>}
          {isAuthenticated && <Link to="/extend" onClick={() => setIsOpen(false)}>Extend</Link>}

          {/* Login/Logout Button */}
          <button className="navbar-login" onClick={handleAuth}>
            {isAuthenticated ? "Logout" : "Login"}
          </button>
        </div>
      )}
    </nav>
  );
};

export default Navbar;
