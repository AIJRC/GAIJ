import React, { Component } from 'react';
import { connect } from 'react-redux';
import { neo4jConfig } from '../config';
import neo4j from 'neo4j-driver';
import './statistics.css';

const driver = neo4j.driver(
  neo4jConfig.url,
  neo4j.auth.basic(neo4jConfig.username, neo4jConfig.password)
);

export class Statistics extends Component {
  state = {
    stats: null,
    loading: true
  };

  componentDidMount() {
    this.fetchStatistics();
  }

  fetchStatistics = async () => {
    const session = driver.session();
    try {
      const result = await session.run(`
        MATCH (n)
        WITH labels(n) as labels, count(n) as count
        RETURN labels, count
        UNION ALL
        MATCH ()-[r]->()
        RETURN ['Relationships'] as labels, count(r) as count
      `);

      const stats = {};
      result.records.forEach(record => {
        const labels = record.get('labels');
        let label = labels[0];
        
        // Pluralize the labels
        switch(label) {
          case 'Company':
            label = 'Companies';
            break;
          case 'Person':
            label = 'People';
            break;
          case 'Address':
            label = 'Addresses';
            break;
          default:
            label = label + '';
        }
        
        const count = record.get('count').toNumber();
        stats[label] = count;
      });

      this.setState({ stats, loading: false });
    } catch (error) {
      console.error('Error fetching statistics:', error);
      this.setState({ loading: false });
    } finally {
      session.close();
    }
  };

  componentWillUnmount() {
    // Close the driver when component unmounts
    driver.close();
  }

  render() {
    const { stats, loading } = this.state;

    if (loading) {
      return <div className="statistics">Loading statistics...</div>;
    }

    return (
      <div className="statistics">
        <h3>Database Statistics</h3>
        <div className="stats-grid">
          {stats && Object.entries(stats).map(([type, count]) => (
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

Statistics = connect()(Statistics);