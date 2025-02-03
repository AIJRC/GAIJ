// construct path object with relevant properties for each node/edge entry
export function assemblePath(path = {}, nodes = {}, edges = {}) {
  if (!path.node_ids || !path.rel_ids)
    return [];

  const pathNodes = [];
  for (const nodeId of path.node_ids) {
    const node = nodes[nodeId];
    if (!node)
      continue;

    pathNodes.push({
      element: 'node',
      type: node.metanode,
      name: node.properties.name
    });
  }

  const pathEdges = [];
  for (let index = 0; index < path.rel_ids.length; index++) {
    const edge = edges[path.rel_ids[index]];
    const prevNode = nodes[path.node_ids[index]];
    if (!edge || !prevNode)
      continue;

    let direction = '';
    if (edge.directed) {
      if (edge.source_neo4j_id === prevNode.neo4j_id)
        direction = 'forward';
      else
        direction = 'backward';
    }

    pathEdges.push({
      element: 'edge',
      type: edge.kind,
      direction: direction
    });
  }

  const assembledPath = [];
  for (const node of pathNodes) {
    assembledPath.push(node);
    if (pathEdges.length > 0)
      assembledPath.push(pathEdges.shift());
  }

  return assembledPath;
}

// produce text path description from assembled path
export function textDescription(path) {
  const description = [];
  for (const entry of path) {
    if (entry.element === 'node')
      description.push(entry.name);
    else if (entry.element === 'edge') {
      let arrow = '–';
      if (entry.direction === 'forward')
        arrow = '→';
      else if (entry.direction === 'backward')
        arrow = '←';
      description.push(arrow);
      description.push(entry.type);
      description.push(arrow);
    }
  }
  return description.join(' ');
}
