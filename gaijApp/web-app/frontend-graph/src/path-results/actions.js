import { fetchGraphData } from '../backend-queries.js';

// fetch paths function
export async function fetchPaths({
  sourceNodeId,
  targetNodeId,
  metapaths,
  updateUrl,
  preserveChecks
}) {
  const graphData = await fetchGraphData(sourceNodeId, targetNodeId);
  
  const paths = [];
  const nodes = {};
  const relationships = {};
  const pathCountInfo = {};

  // Transform nodes
  graphData.nodes.forEach(node => {
    nodes[node.neo4j_id] = {
      id: node.neo4j_id,
      name: node.name,
      metanode: node.metanode,
      properties: node.properties
    };
  });

  // Transform edges into paths
  graphData.edges.forEach(edge => {
    relationships[edge.kind] = {
      kind: edge.kind,
      directed: edge.directed,
      properties: edge.properties
    };

    paths.push({
      nodes: [edge.source_neo4j_id, edge.target_neo4j_id],
      edges: [edge.kind],
      metapath: edge.kind,
      score: 1
    });
  });

  return {
    paths,
    nodes,
    relationships,
    pathCountInfo,
    updateUrl,
    preserveChecks
  };
}

// set paths action
export function setPaths({ paths }) {
  return {
    type: 'set_paths',
    payload: paths
  };
}

// fetch and set paths action creator
export function fetchAndSetPaths({
  sourceNodeId,
  targetNodeId,
  metapaths,
  updateUrl,
  preserveChecks
}) {
  return async function(dispatch) {
    try {
      const graphData = await fetchGraphData(sourceNodeId, targetNodeId);
      
      // Transform Neo4j data into expected format
      const paths = [];
      const nodes = {};
      const relationships = {};

      // Add nodes
      graphData.nodes.forEach(node => {
        nodes[node.neo4j_id] = {
          id: node.neo4j_id,
          name: node.name,
          metanode: node.metanode,
          properties: node.properties
        };
      });

      // Add relationships and construct paths
      graphData.edges.forEach(edge => {
        relationships[edge.kind] = {
          kind: edge.kind,
          directed: edge.directed,
          properties: edge.properties
        };

        paths.push({
          nodes: [edge.source_neo4j_id, edge.target_neo4j_id],
          edges: [edge.kind],
          metapath: edge.kind,
          score: 1
        });
      });

      dispatch(setPaths({
        paths: paths,
        nodes: nodes,
        relationships: relationships,
        updateUrl: updateUrl,
        preserveChecks: preserveChecks
      }));
    } catch (error) {
      console.error('Error fetching paths:', error);
      dispatch(setPaths({
        paths: [],
        nodes: {},
        relationships: {},
        updateUrl: updateUrl,
        preserveChecks: preserveChecks
      }));
    }
  };
}
