import React, { useContext } from "react";
import { Redirect, Route } from "react-router-dom";
import { AuthContext } from "../context/AuthContext"; // Import Auth Context

const ProtectedRoute = ({ component: Component, ...rest }) => {
  const { isAuthenticated, loading } = useContext(AuthContext);

  if (loading) return null; // Wait until auth check is complete

  return (
    <Route
      {...rest}
      render={(props) =>
        isAuthenticated ? (
          <Component {...props} />
        ) : (
          <Redirect
            to={{
              pathname: "/login",
              state: { from: props.location }, // Save original location for redirect after login
            }}
          />
        )
      }
    />
  );
};

export default ProtectedRoute;
