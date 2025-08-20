// construct graph object with relevant properties for each node/edge
export function assembleGraph(paths = [], nodes = {}, relationships = {}) {
  // empty graph object
  const graph = {
    source_neo4j_id: null,
    target_neo4j_id: null,
    nodes: [],
    edges: []
  };

  // if paths not valid, exit
  if (!paths || !paths.length)
    return graph;

  // get source/target nodes from first path
  graph.source_neo4j_id = paths[0].node_ids[0];
  graph.target_neo4j_id = paths[0].node_ids[paths[0].node_ids.length - 1];

  // loop through all paths
  for (const path of paths) {
    // if not checked, don't include in graph
    if (!path.checked)
      continue;

    // loop through nodes in path
    for (const nodeId of path.node_ids) {
      const node = nodes[nodeId];
      const existingNode = graph.nodes.find(
        (existingNode) => existingNode.neo4j_id === node.neo4j_id
      );
      if (!existingNode) {
        // if node hasn't been added to graph yet, add it
        graph.nodes.push({
          // copy all properties of node from state.node
          ...node,
          // add highlight property
          highlighted: path.highlighted,
          // mark as node
          elementType: 'node'
        });
      } else if (path.highlighted)
        // if node already in graph, still update highlight status
        existingNode.highlighted = true;
    }

    // loop through edges in path
    for (const relId of path.rel_ids) {
      const edge = relationships[relId];
      const existingEdge = graph.edges.find(
        (existingEdge) =>
          existingEdge.source_neo4j_id === edge.source_neo4j_id &&
          existingEdge.target_neo4j_id === edge.target_neo4j_id &&
          existingEdge.kind === edge.kind &&
          existingEdge.directed === edge.directed
      );
      if (!existingEdge) {
        // if edge hasn't been added to graph yet, add it
        graph.edges.push({
          // copy all properties of edge
          ...edge,
          // set duplicate properties "source" and "target" because d3
          // needs them (with those names) to create links between nodes
          source: edge.source_neo4j_id,
          target: edge.target_neo4j_id,
          // add highlight property
          highlighted: path.highlighted,
          // mark as edge
          elementType: 'edge'
        });
      } else if (path.highlighted)
        // if edge already in graph, still update highlight status
        existingEdge.highlighted = true;
    }
  }

  // loop through all edges in graph to find coincident edges
  // (multiple edges connecting the same two nodes)
  // sort all edges in graph into bins of same source/target nodes
  const edgeBins = [];
  for (const edgeA of graph.edges) {
    let matched = false;
    // find bin with edges that have same source/target nodes
    // (order-insensitve)
    for (const edgeBin of edgeBins) {
      const match = edgeBin.find(
        (edgeB) =>
          (edgeA.source_neo4j_id === edgeB.source_neo4j_id &&
            edgeA.target_neo4j_id === edgeB.target_neo4j_id) ||
          (edgeA.source_neo4j_id === edgeB.target_neo4j_id &&
            edgeA.target_neo4j_id === edgeB.source_neo4j_id)
      );
      // if matching bin found, add edge to it
      if (match) {
        edgeBin.push(edgeA);
        matched = true;
        break;
      }
    }
    // if didn't find matching bin, create new one and add edge to it
    if (!matched)
      edgeBins.push([edgeA]);
  }

  // loop through edge bins
  for (const edgeBin of edgeBins) {
    // for each edge in bin, assign coincident "offset", a value between
    // -1 and 1 used for drawing, where 0 is straight line, negative is curve
    // on one side, and positive is curve on other side
    const firstSource = edgeBin[0].source_neo4j_id;
    for (let index = 0; index < edgeBin.length; index++) {
      // default offset to 0
      let offset = 0;
      if (edgeBin.length > 1)
        offset = -0.5 + index / (edgeBin.length - 1);
      // if edge source/target order in reverse order as rest of bin,
      // invert offset
      if (edgeBin[index].source_neo4j_id !== firstSource)
        offset *= -1;
      edgeBin[index].coincidentOffset = offset;
    }
  }

  // put source and target node at end of list to ensure highest z-index
  const sourceNodeIndex = graph.nodes.findIndex(
    (node) => node.neo4j_id === graph.source_neo4j_id
  );
  if (sourceNodeIndex !== -1)
    graph.nodes.push(graph.nodes.splice(sourceNodeIndex, 1)[0]);
  const targetNodeIndex = graph.nodes.findIndex(
    (node) => node.neo4j_id === graph.target_neo4j_id
  );
  if (targetNodeIndex !== -1)
    graph.nodes.push(graph.nodes.splice(targetNodeIndex, 1)[0]);

  return graph;
}
