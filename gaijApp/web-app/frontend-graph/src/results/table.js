import React from 'react';
import { Component } from 'react';
import { connect } from 'react-redux';

import { CollapsibleSection } from '../components/collapsible-section';

// results table component
export class ConnectionResults extends Component {
  getNodeName(node) {
    if (!node) return 'Unknown';
    return node.properties?.name || node.properties?.full_address || node.name || 'Unknown';
  }

  render() {
    if (!this.props.paths || !this.props.paths.length)
      return <></>;

    return (
      <CollapsibleSection
        label='Connections'
        tooltipText='Direct connections from the selected node'
      >
        <div className='connections_table'>
          {this.props.paths.map((path, index) => (
            <div key={index} className='connection_row'>
              <div className='connection_info'>
                {this.getNodeName(this.props.nodes[path.node_ids[1]])}
              </div>
            </div>
          ))}
        </div>
      </CollapsibleSection>
    );
  }
}

// connect component to global state
ConnectionResults = connect((state) => ({
  paths: state.paths,
  nodes: state.nodes
}))(ConnectionResults);

export default ConnectionResults;