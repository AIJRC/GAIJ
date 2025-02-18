import { assembleGraph } from './assemble.js';
import { transferObjectProps } from '../utils/object';

// reducer for state.graph
// takes whole state as input
export function graph(state = {}, action) {
  switch (action.type) {
    case 'set_paths':
      const paths = action.payload.paths;
      const nodes = { ...state.nodes, ...(action.payload.nodes || {}) };
      const relationships = {
        ...state.relationships,
        ...(action.payload.relationships || {})
      };

      const graph = assembleGraph(paths, nodes, relationships);

      // transfer over physics simulation details from previous to next state
      transferObjectProps(
        state.graph.nodes,
        graph.nodes,
        ['neo4j_id'],
        ['x', 'y', 'fx', 'fy', 'vx', 'vy']
      );

      return graph || { nodes: [], edges: [] };

      case 'set_source_target_node':
        if (action.payload.sourceNode && action.payload.targetNode) {
          // Check if we have graph data in the action payload
          const graphData = action.payload.graphData;
          if (graphData && graphData.nodes && graphData.edges) {
            return {
              nodes: graphData.nodes.map(node => ({
                ...node,
                elementType: 'node'
              })),
              edges: graphData.edges.map(edge => ({
                ...edge,
                elementType: 'edge',
                source: edge.source_neo4j_id,
                target: edge.target_neo4j_id
              }))
            };
          }
        }
        return state.graph || { nodes: [], edges: [] };
  
      default:
        return state.graph || { nodes: [], edges: [] };
    }
  }

// reducer for state.showGrid
export function showGrid(state = false, action) {
  switch (action.type) {
    case 'toggle_show_grid':
      return !state;
    default:
      return state;
  }
}
