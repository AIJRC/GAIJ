import React, { Component } from "react";
import { connect } from "react-redux";
import { BrowserRouter as Router, Route, Switch, Redirect } from "react-router-dom";
import { AuthProvider } from "../context/AuthContext"; // Import Auth Provider
import ProtectedRoute from "../components/ProtectedRoute"; // Import ProtectedRoute
import ScrollToTop from "../components/ScrollToTop"; // Import ScrollToTop

import Navbar from "../components/Navbar";
import About from "../pages/About";
import Extend from "../pages/Extend";
import Login from "../pages/Login";
import Explore from "../pages/Explore"; // Ensure this exists

import { loadStateFromUrl } from "./actions.js";
import { fetchAndSetDefinitions } from "./actions.js";
import { fetchAndSetPaths } from "../path-results/actions";
import { testConnection } from "../backend-queries";

import "./index.css";
import "../styles/global.css";

// Main App Component
class App extends Component {
  constructor(props) {
    super(props);
    this.state = {
      isPathsLoading: false,
    };
    this.loadStateFromUrl = this.loadStateFromUrl.bind(this);
    this.props.dispatch(fetchAndSetDefinitions());
  }

  loadStateFromUrl() {
    this.props.dispatch(loadStateFromUrl());
  }

  async componentDidMount() {
    await testConnection();
    this.loadStateFromUrl();
    window.addEventListener("popstate", this.loadStateFromUrl);
  }

  componentDidUpdate(prevProps) {
    if (prevProps.sourceNode.id !== this.props.sourceNode.id) {
      if (this.props.sourceNode.id && !this.state.isPathsLoading) {
        this.setState({ isPathsLoading: true }, async () => {
          try {
            await this.props.dispatch(
              fetchAndSetPaths({
                sourceNodeId: this.props.sourceNode.id,
                paths: [],
                nodes: {},
                relationships: {},
                preserveChecks: true,
              })
            );
          } finally {
            this.setState({ isPathsLoading: false });
          }
        });
      } else if (!this.props.sourceNode.id) {
        this.props.dispatch(
          fetchAndSetPaths({
            paths: [],
            nodes: {},
            relationships: {},
          })
        );
      }
    }
  }

  render() {
    return (
      <AuthProvider> {/* Ensure Auth Context wraps the app */}
        <Router>
          <ScrollToTop /> {/* This ensures scroll resets when navigating */}
          <Navbar />
            <Switch>
              {/* Set About as the Home page */}
              <Route exact path="/" component={About} /> 
              <Route path="/about" component={About} />
              <Route path="/login" component={Login} />

              {/* Protect Explore & Extend pages */}
              <ProtectedRoute path="/extend" component={Extend} />
              <ProtectedRoute path="/explore" component={Explore} />

              {/* Redirect any unknown routes to About */}
              <Redirect to="/" />
            </Switch>
        </Router>
      </AuthProvider>
    );
  }
}

// Connect component to Redux state
App = connect((state) => ({
  sourceNode: state.sourceNode,
}))(App);

export { App };
