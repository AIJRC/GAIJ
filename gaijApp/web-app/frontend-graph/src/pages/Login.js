import React, { useContext, useState } from "react";
import { useLocation, useHistory } from "react-router-dom";
import { AuthContext } from "../context/AuthContext"; // Import AuthContext
import "./Login.css"; // Import the Login CSS file

const Login = () => {
  const { login } = useContext(AuthContext); // Access login function from context
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(""); // For displaying error messages

  const location = useLocation();
  const history = useHistory();

  const handleSubmit = (event) => {
    event.preventDefault();

    // Allow any non-empty credentials for testing
    if (username === "gaij" && password === "gaij") {
      login(() => {
        const { from } = location.state || { from: { pathname: "/" } };
        history.replace(from);
      });
    } else {
      setError("Invalid credentials, please try again.");
    }
  };

  return (
    <div className="login-container">
      <h1>Login</h1>
      <form onSubmit={handleSubmit} className="login-form">
        <label>Username:</label>
        <input
          type="text"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          required
        />

        <label>Password:</label>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />

        {error && <p className="error">{error}</p>}

        <button type="submit">Login</button>
      </form>
    </div>
  );
};

export default Login;
