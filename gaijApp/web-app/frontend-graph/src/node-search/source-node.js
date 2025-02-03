import React from 'react';
import { Component } from 'react';
import { connect } from 'react-redux';
import './source-node.css';

import { SearchBox } from './search-box.js';
import { NodeTypeSelector } from './node-type-selector.js';
import { setSourceTargetNode } from './actions.js';
import { setPaths } from '../path-graph/actions.js';
import { fetchNodeConnections } from '../backend-queries.js';  // Add this import

// source node search box component
export class SourceNode extends Component {
  // when user makes a new node selection
  constructor(props) {
    super(props);
    this.state = {
      selectedType: '',
      errorMessage: ''  // Add this line
    };
  }

  onTypeSelect = (type) => {
    this.setState({ selectedType: type });
    // Clear the selected node when type changes
    this.props.dispatch(
      setSourceTargetNode({ sourceNode: null, updateUrl: true })
    );
  };

  onChange = async (value) => {
    console.log('Selected value:', value);

    if (!value) {
      await this.props.dispatch(
        setSourceTargetNode({ sourceNode: null, updateUrl: true })
      );
      return;
    }

    // Extract node ID with fallbacks
    const nodeId = value.neo4j_id || value.id || value.properties?.id;
    if (!nodeId) {
      console.error('Invalid node: No ID found', value);
      return;
    }

    // Ensure the node has proper ID fields
    const nodeToUse = {
      ...value,
      neo4j_id: nodeId,
      id: nodeId,
      metanode: this.state.selectedType === 'Tax Number' ? 'Company' : this.state.selectedType,
      elementType: 'node'
    };

    // Update the source node with the processed node
    await this.props.dispatch(
      setSourceTargetNode({ sourceNode: nodeToUse, updateUrl: true })
    );

    try {
      // Fetch connections
      const connections = await fetchNodeConnections(nodeId, nodeToUse.metanode);
      console.log('Source node connections:', connections);

      if (!connections || !connections.nodes || connections.nodes.length === 0) {
        console.warn('No connections found for node:', nodeId);
        this.setState({ errorMessage: 'No connections found for this node' });
        return;
      }

      // Validate edges before processing
      const validEdges = connections.edges.filter(edge => 
        edge && edge.source_neo4j_id && edge.target_neo4j_id
      );

      if (validEdges.length === 0) {
        console.warn('No valid edges found for node:', nodeId);
        this.setState({ errorMessage: 'No connections found for this node. Please try another one.' });
        return;
      }

      // Clear any previous error message
      this.setState({ errorMessage: '' });

      const nodesObj = {
        [nodeId]: {
          ...value,
          id: nodeId,
          neo4j_id: nodeId,
          elementType: 'node'
        },
        ...connections.nodes.reduce((acc, node) => {
          if (!node) return acc;
          const id = node.neo4j_id || node.id;
          if (!id) return acc;
          
          acc[id] = {
            ...node,
            id: id,
            neo4j_id: id,
            elementType: 'node'
          };
          return acc;
        }, {})
      };

      await this.props.dispatch(
        setPaths({
          paths: [{
            node_ids: [nodeId, ...validEdges.map(edge => 
              edge.source_neo4j_id === nodeId ? edge.target_neo4j_id : edge.source_neo4j_id
            )],
            rel_ids: Array.from({ length: validEdges.length }, (_, i) => i),
            checked: true
          }],
          nodes: nodesObj,
          relationships: validEdges.reduce((acc, edge, index) => {
            acc[index] = {
              ...edge,
              id: index,
              source: edge.source_neo4j_id,
              target: edge.target_neo4j_id,
              elementType: 'edge'
            };
            return acc;
          }, {})
        })
      );
    } catch (error) {
      console.error('Error fetching or processing node connections:', error);
    } finally {
      document.activeElement.blur();
    }
  };

  render() {
    return (
      <div className={`source_node_container ${!this.state.selectedType ? 'single' : ''}`}>
        <div className={`source_node_section ${!this.state.selectedType ? 'single' : ''}`}>
          <div className='small left'>Source Type</div>
          <NodeTypeSelector
            selectedType={this.state.selectedType}
            onTypeSelect={this.onTypeSelect}
          />
        </div>
        <div className="source_node_section">
          {this.state.selectedType && (
            <>
              <div className='small left'>Source Node</div>
              <SearchBox
                tooltipText='The starting node of the paths'
                node={this.props.node}
                otherNode={this.props.otherNode}
                onChange={this.onChange}
                nodeType={this.state.selectedType}
              />
              {this.state.errorMessage && (
                <div style={{ color: 'red', marginTop: '10px', fontSize: '14px' }}>
                  {this.state.errorMessage}
                </div>
              )}
            </>
          )}
        </div>
      </div>
    );
  }
}

SourceNode = connect((state) => ({
  node: state.sourceNode,
  otherNode: state.targetNode
}))(SourceNode);
