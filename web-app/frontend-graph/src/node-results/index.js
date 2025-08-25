import React from 'react';
import { Component } from 'react';
import { connect } from 'react-redux';

import { CollapsibleSection } from '../components/collapsible-section.js';
import { NodeTable } from './table.js';

import './index.css';

// node results section component
// details about source/target nodes
export class NodeResults extends Component {
  // display component
  render() {
    return (
      <CollapsibleSection
        label='Node Info'
        tooltipText='Details about the source and target node'
        className='node_results_content'
      >
        {this.props.sourceNode.name && (
          <>
            {/* <div className='small left'>Node</div> */}
            <NodeTable node={this.props.sourceNode} label='Node' />
          </>
        )}
        {this.props.targetNode.name && (
          <>
            <div className='small left'>Target Node</div>
            <NodeTable node={this.props.targetNode} label='Target Node' />
          </>
        )}
        {!this.props.sourceNode.name && !this.props.targetNode.name && (
          <span className='light'>select a source and target node</span>
        )}
      </CollapsibleSection>
    );
  }
}
// connect component to global state
NodeResults = connect((state) => ({
  sourceNode: state.sourceNode,
  targetNode: state.targetNode
}))(NodeResults);
