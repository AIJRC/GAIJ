import React from 'react';
import { Component } from 'react';
import { connect } from 'react-redux';
import './source-node.css';

import { SearchBox } from './search-box.js';
import { NodeTypeSelector } from './node-type-selector.js';
import { setSourceTargetNode } from './actions.js';
import { setPaths } from '../path-graph/actions.js';
import { fetchNodeConnections } from '../backend-queries.js';

// source node search box component
export class SourceNode extends Component {
  constructor(props) {
    super(props);
    this.state = {
      conditions: [{
        selectedType: '',
        selectedNode: null,
        errorMessage: ''
      }],
      mode: 'OR'  // Add mode state to track current operation
    };
  }

  addCondition = () => {
    this.setState(prevState => ({
      conditions: [...prevState.conditions, {
        selectedType: '',
        selectedNode: null,
        errorMessage: ''
      }]
    }));
  };

  removeCondition = (index) => {
    if (this.state.conditions.length > 1) {
      this.setState(prevState => ({
        conditions: prevState.conditions.filter((_, i) => i !== index)
      }));
    }
  };

  onTypeSelect = (type, index) => {
    this.setState(prevState => {
      const newConditions = [...prevState.conditions];
      newConditions[index] = {
        ...newConditions[index],
        selectedType: type,
        selectedNode: null,
        errorMessage: ''  // Clear error message when type changes
      };
      return { conditions: newConditions };
    });

    // Clear the graph when changing type
    this.props.dispatch(
      setSourceTargetNode({ sourceNode: null, updateUrl: true })
    );
  };

  processConditions = async () => {
    const { conditions } = this.state;
    const validConditions = conditions.filter(c => c.selectedNode && c.selectedType);
    
    if (validConditions.length === 0) return;

    try {
      let allNodes = {};
      let allEdges = [];

      // Process connections for each condition
      for (const condition of validConditions) {
        const nodeId = condition.selectedNode.neo4j_id;
        const connections = await fetchNodeConnections(
          nodeId,
          condition.selectedType === 'Tax Number' ? 'Company' : condition.selectedType
        );

        if (connections?.nodes) {
          // Add the source node
          allNodes[nodeId] = {
            neo4j_id: nodeId,
            name: condition.selectedNode.name,
            metanode: condition.selectedNode.metanode,
            properties: condition.selectedNode.properties
          };

          // Add connected nodes
          connections.nodes.forEach(node => {
            const id = node.neo4j_id;
            if (id) {
              allNodes[id] = node;
            }
          });

          // Add edges
          if (connections.edges) {
            allEdges.push(...connections.edges);
          }
        }
      }

      // Format relationships similar to getTopCompanies
      const relationships = {};
      allEdges.forEach((edge, index) => {
        relationships[index] = {
          source_neo4j_id: edge.source_neo4j_id,
          target_neo4j_id: edge.target_neo4j_id,
          kind: edge.kind,
          directed: edge.directed,
          properties: edge.properties
        };
      });

      // Create paths array similar to top-companies-button
      const paths = allEdges.map((edge, index) => ({
        node_ids: [edge.source_neo4j_id, edge.target_neo4j_id],
        rel_ids: [index],
        checked: true,
        highlighted: false
      }));

      // Dispatch with the same format as top-companies-button
      await this.props.dispatch(
        setPaths({
          paths,
          nodes: allNodes,
          relationships,
          updateUrl: true
        })
      );
    } catch (error) {
      console.error('Error processing conditions:', error);
      this.setState(prevState => ({
        conditions: prevState.conditions.map(c => ({
          ...c,
          errorMessage: 'Error processing graph data'
        }))
      }));
    }
  };

  processConditionsAND = async () => {
    const { conditions } = this.state;
    const validConditions = conditions.filter(c => c.selectedNode && c.selectedType);
    
    if (validConditions.length < 2) return;

    try {
      let commonNodes = null;
      let allNodes = {};
      let allEdges = [];

      // Process each condition to find common nodes
      for (const condition of validConditions) {
        const nodeId = condition.selectedNode.neo4j_id;
        const connections = await fetchNodeConnections(
          nodeId,
          condition.selectedType === 'Tax Number' ? 'Company' : condition.selectedType
        );

        if (connections?.nodes) {
          // Create a set of connected node IDs
          const connectedNodeIds = new Set(
            connections.nodes
              .map(node => node.neo4j_id || node.id)
              .filter(id => id != null)
          );
          
          // Add the source node itself
          connectedNodeIds.add(nodeId);

          // If this is the first condition, use its nodes as initial set
          if (commonNodes === null) {
            commonNodes = connectedNodeIds;
          } else {
            // Intersect with previous results to find common nodes
            commonNodes = new Set(
              [...commonNodes].filter(id => connectedNodeIds.has(id))
            );
          }

          // Store all nodes and edges for later filtering
          connections.nodes.forEach(node => {
            const id = node.neo4j_id || node.id;
            if (id) {
              allNodes[id] = {
                ...node,
                id,
                neo4j_id: id,
                elementType: 'node'
              };
            }
          });

          if (connections.edges) {
            allEdges.push(...connections.edges);
          }
        }
      }

      // Add source nodes to allNodes
      validConditions.forEach(condition => {
        const nodeId = condition.selectedNode.neo4j_id;
        allNodes[nodeId] = {
          ...condition.selectedNode,
          id: nodeId,
          neo4j_id: nodeId,
          elementType: 'node'
        };
      });

      // Filter edges to only include those connecting common nodes
      const validEdges = allEdges.filter(edge => 
        edge && 
        edge.source_neo4j_id && 
        edge.target_neo4j_id && 
        commonNodes.has(edge.source_neo4j_id) && 
        commonNodes.has(edge.target_neo4j_id)
      );

      if (commonNodes.size > 0 && validEdges.length > 0) {
        const relationships = validEdges.reduce((acc, edge, index) => {
          acc[index] = {
            ...edge,
            id: index,
            source: edge.source_neo4j_id,
            target: edge.target_neo4j_id,
            elementType: 'edge'
          };
          return acc;
        }, {});

        // Create filtered allNodes object with only common nodes
        const filteredNodes = {};
        commonNodes.forEach(id => {
          if (allNodes[id]) {
            filteredNodes[id] = allNodes[id];
          }
        });

        await this.props.dispatch(
          setPaths({
            paths: [{
              node_ids: Array.from(commonNodes),
              rel_ids: Object.keys(relationships),
              checked: true
            }],
            nodes: filteredNodes,
            relationships: relationships
          })
        );
      } else {
        // Clear the graph when no common elements are found
        await this.props.dispatch(
          setPaths({
            paths: [],
            nodes: {},
            relationships: {}
          })
        );
        
        this.setState(prevState => ({
          conditions: prevState.conditions.map(c => ({
            ...c,
            errorMessage: 'No common connections found between the selected nodes'
          }))
        }));
      }

    } catch (error) {
      console.error('Error processing AND conditions:', error);
      this.setState(prevState => ({
        conditions: prevState.conditions.map(c => ({
          ...c,
          errorMessage: 'Error processing graph data'
        }))
      }));
    }
  };

  // Add mode switching methods
  setMode = async (newMode) => {
    this.setState({ mode: newMode });
    if (newMode === 'OR') {
      await this.processConditions();
    } else {
      await this.processConditionsAND();
    }
  };

  // Add refresh method
    refreshGraph = async () => {
      console.log('Refreshing graph with mode:', this.state.mode);
      console.log('Current conditions:', this.state.conditions);
      
      // Clear error messages first
      this.setState(prevState => ({
        conditions: prevState.conditions.map(c => ({
          ...c,
          errorMessage: ''
        }))
      }));
      
      try {
        if (this.state.mode === 'OR') {
          await this.processConditions();
        } else {
          await this.processConditionsAND();
        }
        
        // Force a second update after a small delay
        setTimeout(() => {
          if (this.state.mode === 'OR') {
            this.processConditions();
          } else {
            this.processConditionsAND();
          }
        }, 100);
      } catch (error) {
        console.error('Error refreshing graph:', error);
      }
    };
  
    // Add this method back
    onChange = async (value, index) => {
      console.log('onChange triggered with value:', value, 'at index:', index);
      
      // Update the selected node for this condition and clear error message
      this.setState(prevState => {
        const newConditions = [...prevState.conditions];
        newConditions[index] = {
          ...newConditions[index],
          selectedNode: value,
          errorMessage: ''  // Clear error message when node changes
        };
        return { conditions: newConditions };
      }, async () => {
        // Process conditions after state is updated
        console.log('State updated, processing conditions...');
        await this.processConditions();
      });
    };
  
    // Update the SearchBox component usage
    render() {
      const showModeButtons = this.state.conditions.length > 1;
      
      return (
        <div className="source_node_container">
          {this.state.conditions.map((condition, index) => (
            <React.Fragment key={index}>
              <div className="condition-group">
                <div className="source_node_section">
                  <div className="condition-header">
                    <div className='small left'>Source Type {index + 1}</div>
                    {index > 0 && (
                      <button 
                        className="remove-condition-button"
                        onClick={() => this.removeCondition(index)}
                      >
                        Remove
                      </button>
                    )}
                  </div>
                  <NodeTypeSelector
                    selectedType={condition.selectedType}
                    onTypeSelect={(type) => this.onTypeSelect(type, index)}
                  />
                </div>
                {condition.selectedType && (
                  <div className="source_node_section">
                    <div className='small left'>Source Node {index + 1}</div>
                    <SearchBox
                      tooltipText='The starting node of the paths'
                      node={condition.selectedNode}
                      onChange={(value) => this.onChange(value, index)}
                      nodeType={condition.selectedType}
                    />
                    {condition.errorMessage && (
                      <div className="error-message">
                        {condition.errorMessage}
                      </div>
                    )}
                  </div>
                )}
              </div>
              {/* Add mode buttons between conditions */}
              {index < this.state.conditions.length - 1 && (
                <div className="mode-buttons-container">
                  <button 
                    className={`mode-button ${this.state.mode === 'OR' ? 'active' : ''}`}
                    onClick={() => this.setMode('OR')}
                  >
                    OR
                  </button>
                  <button 
                    className={`mode-button ${this.state.mode === 'AND' ? 'active' : ''}`}
                    onClick={() => this.setMode('AND')}
                  >
                    AND
                  </button>
                </div>
              )}
            </React.Fragment>
          ))}
          <div className="button-container">
            <button 
              className="add-condition-button"
              onClick={this.addCondition}
            >
              Add Search Condition
            </button>
            <button 
              className="refresh-button"
              onClick={this.refreshGraph}
            >
              Refresh Graph
            </button>
          </div>
        </div>
      );
    }
}

SourceNode = connect((state) => ({
  node: state.sourceNode,
  otherNode: state.targetNode
}))(SourceNode);
