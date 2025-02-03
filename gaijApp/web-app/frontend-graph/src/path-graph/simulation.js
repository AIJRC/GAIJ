import * as d3 from 'd3';

import { positionNode, positionEdge, positionEdgeLabel } from './position.js';

import {
  nodeDistance,
  nodeRadius,
  nodeRepulsion,
  centeringForce
} from './constants.js';

// create physics simulation
export function createSimulation() {
  // create physics simulation for nodes to detangle and prettify layout
  const simulation = d3
    .forceSimulation()
    .force(
      'link',
      d3
        .forceLink()
        .distance(nodeDistance)
        .id((d) => d.neo4j_id)
    )
    .force(
      'collide',
      d3
        .forceCollide()
        .radius(nodeRadius)
        .strength(1)
    )
    .force('centerX', d3.forceX(0).strength(centeringForce / 100))
    .force('centerY', d3.forceY(0).strength(centeringForce / 100))
    .force('charge', d3.forceManyBody().strength(-nodeRepulsion));
  simulation.on('tick', onSimulationTick);
  return simulation;
}

// when simulation ticks forward
function onSimulationTick() {
  // position all elements in graph
  d3.selectAll('.graph_edge_line_highlight').each(positionEdge);
  d3.selectAll('.graph_edge_line').each(positionEdge);
  d3.selectAll('.graph_edge_label').each(positionEdgeLabel);
  d3.selectAll('.graph_node_circle_highlight').each(positionNode);
  d3.selectAll('.graph_node_circle').each(positionNode);
  d3.selectAll('.graph_node_label').each(positionNode);
}

// update simulation with new data
export function updateSimulation(simulation, nodes, edges, reheat) {
  // reimport nodes
  simulation.nodes(nodes);
  // rebuild node links
  simulation.force('link').links(edges);
  // reheat simulation
  if (reheat)
    simulation.alpha(1).restart();
  else
    simulation.restart();
}

// fix source and target nodes in nice starting positions
export function pinSourceTarget(data) {
  data.nodes.forEach((node) => {
    if (node.neo4j_id === data.source_neo4j_id) {
      node.fx = -nodeDistance * 2;
      node.fy = 0;
    }
    if (node.neo4j_id === data.target_neo4j_id) {
      node.fx = nodeDistance * 2;
      node.fy = 0;
    }
  });
}

// unpin all nodes
export function unpinAll(data, simulation) {
  data.nodes.forEach((node) => {
    node.fx = null;
    node.fy = null;
  });

  simulation.alpha(1).restart();
}

// pin all nodes
export function pinAll(data) {
  data.nodes.forEach((node) => {
    node.fx = node.x;
    node.fy = node.y;
  });
}

// reset position of nodes to center
export function resetAll(data) {
  data.nodes.forEach((node) => {
    // set position to 0,0
    // add a bit of random offset to prevent nodes from "exploding" outward
    // due to them being right on top of each other
    node.x = -nodeRadius + Math.random() * 2 * nodeRadius;
    node.y = -nodeRadius + Math.random() * 2 * nodeRadius;
  });
}
