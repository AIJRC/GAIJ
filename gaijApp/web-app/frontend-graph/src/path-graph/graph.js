import React from 'react';
import { Component } from 'react';
import { connect } from 'react-redux';
import * as d3 from 'd3';

import { GraphDefs } from './defs.js';
import { GraphEdgeLineHighlights } from './edge-line-highlights.js';
import { GraphNodeCircleHighlights } from './node-circle-highlights.js';
import { GraphEdgeLines } from './edge-lines.js';
import { GraphEdgeLabels } from './edge-labels.js';
import { GraphNodeCircles } from './node-circles.js';
import { GraphNodeLabels } from './node-labels.js';
import { GraphGrid } from './grid.js';
import { createSimulation } from './simulation.js';
import { updateSimulation } from './simulation.js';
import { pinSourceTarget } from './simulation.js';
import { unpinAll } from './simulation.js';
import { pinAll } from './simulation.js';
import { resetAll } from './simulation';
import { createViewHandler } from './view.js';
import { createNodeDragHandler } from './node-drag.js';
import { resetView } from './view.js';
import { fitView } from './view.js';
import { setPaths } from '../path-graph/actions.js';
import { fetchNodeConnections } from '../backend-queries.js';

import './graph.css';

// graph component
export class Graph extends Component {
  // initialize component
  constructor() {
    super();
    this.state = {};
    
    // Bind methods
    this.resetView = this.resetView.bind(this);
    this.unpinAll = this.unpinAll.bind(this);
    this.fitView = this.fitView.bind(this);
    this.pinAll = this.pinAll.bind(this);
    this.onViewClick = this.onViewClick.bind(this);
    this.deselectAll = this.deselectAll.bind(this);
  }

  // Convert these methods to arrow functions
  resetView = () => {
    resetView(this.state.viewHandler, this.props.width, this.props.height);
  };

  fitView = () => {
    fitView(this.state.viewHandler, this.props.width, this.props.height);
  };

  unpinAll = () => {
    unpinAll(this.props.graph, this.state.simulation);
  };

  pinAll = () => {
    pinAll(this.props.graph);
  };

  // when component mounts
  componentDidMount() {
    // initialize graph. create simulation and event handlers to be referenced
    // on graph updates
    const simulation = createSimulation();
    const viewHandler = createViewHandler(this.onViewClick, this.fitView);
    const nodeDragHandler = createNodeDragHandler(simulation);
    this.setState(
      {
        simulation: simulation,
        viewHandler: viewHandler,
        nodeDragHandler: nodeDragHandler
      },
      this.resetView
    );
  }

  // when component updates
  componentDidUpdate(prevProps) {
    console.log('Graph componentDidUpdate - Current props:', this.props.graph);
    console.log('Graph componentDidUpdate - Previous props:', prevProps.graph);
    console.log('Current paths:', this.props.paths);
    
    // If we have a new node selected from the text box
    if (this.props.graph.source_neo4j_id && 
        this.props.graph.source_neo4j_id === this.props.graph.target_neo4j_id &&
        prevProps.graph.source_neo4j_id !== this.props.graph.source_neo4j_id) {
      
      // Fetch connections for the selected node
      this.fetchAndDisplayConnections(this.props.graph.source_neo4j_id);
    }
    
    // Update simulation with new data
    if (this.props.graph.nodes.length > 100) {
      // For large graphs, update less frequently
      updateSimulation(
        this.state.simulation,
        this.props.graph.nodes,
        this.props.graph.edges,
        false // Don't reheat on every update
      );
      this.state.simulation.alpha(0.3); // Lower alpha for smoother transitions
    } else {
      // Regular update for smaller graphs
      updateSimulation(
        this.state.simulation,
        this.props.graph.nodes,
        this.props.graph.edges,
        this.props.graph.nodes.length !== prevProps.graph.nodes.length
      );
    }

    // when adding first path to graph, restart graph
    if (prevProps.graph.nodes.length === 0) {
      console.log('First path added to graph - restarting');
      console.log('Source node:', this.props.graph.source_neo4j_id);
      console.log('Target node:', this.props.graph.target_neo4j_id);
      this.resetView();
      this.unpinAll();
      resetAll(this.props.graph);
      pinSourceTarget(this.props.graph);
      this.state.simulation.alpha(1).restart();
    }
  }

  // Add new method to fetch and display connections
  fetchAndDisplayConnections = async (nodeId) => {
    const connections = await fetchNodeConnections(nodeId);
    console.log('Fetched connections for text box selection:', connections);

    if (connections && connections.nodes.length > 0) {
      const selectedNode = {
        neo4j_id: nodeId,
        elementType: 'node',
        ...this.props.graph.nodes[0]
      };

      const nodesObj = {
        [nodeId]: selectedNode,
        ...connections.nodes.reduce((acc, node) => {
          acc[node.neo4j_id] = {
            ...node,
            id: node.neo4j_id,
            elementType: 'node'
          };
          return acc;
        }, {})
      };

      const validEdges = connections.edges;

      const paths = {
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
      };

      console.log('Dispatching setPaths for text box selection:', paths);
      this.props.dispatch(setPaths(paths));
    }
  };

  // Remove the restartGraph arrow function and move its logic directly into componentDidUpdate
  // when node or edge clicked by user
  onNodeEdgeClick = async (d) => {
    console.log('Node/Edge clicked:', d);
    d3.event.stopPropagation();

    this.deselectAll();
    if (!d.selected) {
      d.selected = true;
    }

    if (d.elementType === 'node') {
      const connections = await fetchNodeConnections(d.neo4j_id, d.metanode);
      console.log('Fetched connections:', connections);

      if (connections && connections.nodes.length > 0) {
        const clickedNode = {
          ...d,
          elementType: 'node'
        };
        console.log('Clicked node with elementType:', clickedNode);

        const nodesObj = {
          [clickedNode.neo4j_id]: clickedNode,
          ...connections.nodes.reduce((acc, node) => {
            acc[node.neo4j_id] = {
              ...node,
              id: node.neo4j_id,
              elementType: 'node'
            };
            return acc;
          }, {})
        };
        console.log('Processed nodes object:', nodesObj);

        const validEdges = connections.edges;
        console.log('Valid edges:', validEdges);

        const paths = {
          paths: [{
            node_ids: [d.neo4j_id, ...validEdges.map(edge => 
              edge.source_neo4j_id === d.neo4j_id ? edge.target_neo4j_id : edge.source_neo4j_id
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
        };
        console.log('Dispatching setPaths with:', paths);
        this.props.dispatch(setPaths(paths));
      }
    }

    this.props.setSelectedElement(d);
    this.fitView();
  };

  // when node or edge hovered by user
  onNodeEdgeHover = (d) => {
    d3.event.stopPropagation();
    d.hovered = true;
    this.props.setHoveredElement(d);
  };

  // when node or edge unhovered by user
  onNodeEdgeUnhover = (d) => {
    d3.event.stopPropagation();
    d.hovered = false;
    this.props.setHoveredElement(null);
  };

  // deselect all elements
  deselectAll = () => {
    for (const node of this.props.graph.nodes)
      node.selected = undefined;
    for (const edge of this.props.graph.edges)
      edge.selected = undefined;
  };

  // on view click
  onViewClick = () => {
    this.deselectAll();
    this.props.setSelectedElement(null);
  };

  // display component
  render() {
    // calculate x position of graph container
    let left = 0;
    if (this.props.sectionWidth && this.props.width) {
      left = this.props.sectionWidth / 2 - this.props.width / 2;
      const minLeft =
        this.props.sectionWidth / 2 - document.body.clientWidth / 2 + 20;
      if (left < minLeft)
        left = minLeft;
    }

    return (
      <div id='graph_container' style={{ height: this.props.height }}>
        <svg
          xmlns='http://www.w3.org/2000/svg'
          id='graph'
          width={this.props.width}
          height={this.props.height}
          style={{ left: left }}
        >
          <GraphDefs />
          <g id='graph_view'>
            {this.props.showGrid && (
              <g id='graph_grid_layer'>
                <GraphGrid />
              </g>
            )}
            <g id='graph_contents'>
              <g id='graph_edge_line_highlight_layer'>
                <GraphEdgeLineHighlights />
              </g>
              <g id='graph_node_circle_highlight_layer'>
                <GraphNodeCircleHighlights />
              </g>
              <g id='graph_edge_line_layer'>
                <GraphEdgeLines
                  // pass props to make sure component rerenders any time they
                  // change
                  selectedElement={this.props.selectedElement}
                  hoveredElement={this.props.hoveredElement}
                  showGrid={this.props.showGrid}
                />
              </g>
              <g id='graph_edge_label_layer'>
                <GraphEdgeLabels
                  onNodeEdgeClick={this.onNodeEdgeClick}
                  onNodeEdgeHover={this.onNodeEdgeHover}
                  onNodeEdgeUnhover={this.onNodeEdgeUnhover}
                />
              </g>
              <g id='graph_node_circle_layer'>
                <GraphNodeCircles
                  nodeDragHandler={this.state.nodeDragHandler}
                  onNodeEdgeClick={this.onNodeEdgeClick}
                  onNodeEdgeHover={this.onNodeEdgeHover}
                  onNodeEdgeUnhover={this.onNodeEdgeUnhover}
                  // pass props to make sure component rerenders any time they
                  // change
                  selectedElement={this.props.selectedElement}
                  hoveredElement={this.props.hoveredElement}
                  showGrid={this.props.showGrid}
                />
              </g>
              <g id='graph_node_label_layer'>
                <GraphNodeLabels />
              </g>
            </g>
          </g>
        </svg>
      </div>
    );
  }
}
// connect component to global state
Graph = connect(
  (state) => ({
    paths: state.paths,
    graph: state.graph,
    showGrid: state.showGrid
  }),
  null,
  null,
  { forwardRef: true }
)(Graph);

