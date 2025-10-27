import React, { Component } from "react";
import { connect } from "react-redux";
import { withRouter } from "react-router-dom";
import { neo4jDriver } from "../config"; // Import the **persistent** driver
import "./statistics.css";

class Statistics extends Component {
  state = {
    stats: null,
    loading: true,
    error: null,
  };

  componentDidMount() {
    this.fetchStatistics();
  }

  componentDidUpdate(prevProps) {
    // Re-fetch statistics when navigating to Explore
    if (prevProps.location.pathname !== this.props.location.pathname) {
      this.fetchStatistics();
    }
  }

  fetchStatistics = async () => {
    this.setState({ loading: true, error: null }); // Reset UI state

    // Open a new Neo4j session **without closing the driver**
    const session = neo4jDriver.session();

    try {
      console.log("Fetching statistics from Neo4j...");
      const result = await session.run(`
        MATCH (n)
        WITH labels(n) as labels, count(n) as count
        RETURN labels, count
        UNION ALL
        MATCH ()-[r]->()
        RETURN ['Relationships'] as labels, count(r) as count
      `);

      console.log("Raw Neo4j Query Result:", result.records);

      const stats = {};
      result.records.forEach((record) => {
        const labels = record.get("labels");
        let label = labels[0];

        switch (label) {
          case "Company":
            label = "Companies";
            break;
          case "Person":
            label = "People";
            break;
          case "Address":
            label = "Addresses";
            break;
          default:
            label = label + "";
        }

        const count = record.get("count").toNumber();
        stats[label] = count;
      });

      console.log("Processed Statistics:", stats);
      this.setState({ stats, loading: false });
    } catch (error) {
      console.error("Error fetching statistics:", error);
      this.setState({ loading: false, error: "Failed to load statistics" });
    } finally {
      session.close(); // Close session (but NOT the driver)
    }
  };

  render() {
    const { stats, loading, error } = this.state;

    if (loading) {
      return <div className="statistics">Loading statistics...</div>;
    }

    if (error) {
      return <div className="statistics error">{error}</div>;
    }

    if (!stats || Object.keys(stats).length === 0) {
      return <div className="statistics error">No data available.</div>;
    }

    return (
      <div className="statistics">
        <h3>Database Statistics</h3>
        <div className="stats-grid">
          {Object.entries(stats).map(([type, count]) => (
            <div key={type} className="stat-item">
              <div className="stat-count">{count.toLocaleString()}</div>
              <div className="stat-label">{type}</div>
            </div>
          ))}
        </div>
      </div>
    );
  }
}

// Use withRouter to detect navigation changes
export default withRouter(connect()(Statistics));
