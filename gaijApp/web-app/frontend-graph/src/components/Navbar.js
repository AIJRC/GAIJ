import React, { useState } from "react";
import { Link } from "react-router-dom";
import "./Navbar.css";

const Navbar = () => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <nav className="navbar">
      {/* Logo (left-aligned) */}
      <div className="navbar-logo"><img src="/gaij_logo.png" alt="GAIJ Logo" /></div>

      {/* Hamburger Menu Icon (Small Screens) */}
      <div className="menu-icon" onClick={() => setIsOpen(!isOpen)}>
        ☰
      </div>

      {/* Navigation Links & Login Button */}
      <div className={`navbar-links ${isOpen ? "open" : ""}`}>
        <Link to="/about" onClick={() => setIsOpen(false)}>About</Link>
        <Link to="/" onClick={() => setIsOpen(false)}>Explore</Link>
        <Link to="/extend" onClick={() => setIsOpen(false)}>Extend</Link>

        {/* Login Button (Now inside the menu) */}
        <button className="navbar-login" onClick={() => setIsOpen(false)}>Login</button>
      </div>
    </nav>
  );
};

export default Navbar;