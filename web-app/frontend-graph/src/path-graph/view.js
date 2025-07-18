import * as d3 from 'd3';

import { minZoom, maxZoom, nodeRadius } from './constants.js';

// create view handler
export function createViewHandler(onClick, onDblClick) {
  const svg = d3.select('#graph');
  // create handler for panning and zooming view
  const viewHandler = d3
    .zoom()
    .scaleExtent([minZoom, maxZoom])
    .on('zoom', onViewChange);
  svg.call(viewHandler);
  svg.on('click', onClick);
  svg.on('dblclick.zoom', null);
  svg.on('dblclick', onDblClick);

  return viewHandler;
}

// when view panned or zoomed by user
function onViewChange() {
  d3.select('#graph_view').attr('transform', d3.event.transform);
}

// center view around 0,0 and reset to 100% zoom
export function resetView(viewHandler, containerWidth, containerHeight) {
  // determine scale and translate to fit view
  const scale = 1;
  const translateX = containerWidth / 2;
  const translateY = containerHeight / 2;

  // perform view transform
  d3.select('#graph').call(
    viewHandler.transform,
    d3.zoomIdentity.translate(translateX, translateY).scale(scale)
  );
}

// fit view to contents of graph
export function fitView(viewHandler, containerWidth, containerHeight) {
  const contents = d3
    .select('#graph_contents')
    .node()
    .getBBox();
  const padding = nodeRadius;

  // calculate center of contents
  contents.midX = contents.x + contents.width / 2;
  contents.midY = contents.y + contents.height / 2;

  // determine scale and translate to fit view
  let scale = 1;
  if (contents.width && contents.height) {
    scale =
      1 /
      Math.max(
        contents.width / (containerWidth - padding),
        contents.height / (containerHeight - padding)
      );
  }
  const translateX = containerWidth / 2 - scale * contents.midX;
  const translateY = containerHeight / 2 - scale * contents.midY;

  // perform view transform
  d3.select('#graph').call(
    viewHandler.transform,
    d3.zoomIdentity.translate(translateX, translateY).scale(scale)
  );
}
