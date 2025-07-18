import * as d3 from 'd3';

import { store } from '../index.js';

import { gridSpacing } from './constants.js';

// create node drag handler
export function createNodeDragHandler(simulation) {
  const nodeDragHandler = d3
    .drag()
    .on('drag', onNodeDrag)
    .on('start', () => onNodeDragStart(simulation));
  return nodeDragHandler;
}

// when node dragged by user
function onNodeDragStart(simulation) {
  simulation.alphaTarget(1).restart();
}

// when node dragged by user
function onNodeDrag(d) {
  let newX = d3.event.x;
  let newY = d3.event.y;

  // snap to grid
  if (store.getState().showGrid) {
    newX = Math.round(newX / (gridSpacing / 2)) * (gridSpacing / 2);
    newY = Math.round(newY / (gridSpacing / 2)) * (gridSpacing / 2);
  }

  d.fx = newX;
  d.fy = newY;
}
