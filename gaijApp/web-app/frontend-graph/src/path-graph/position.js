import * as d3 from 'd3';

import {
  nodeRadius,
  edgeArrowSize,
  edgeSpreadAngle,
  edgeSpreadDistance,
  edgeFontSize
} from './constants.js';

// position node based on results of simulation
// d3 simulation stores positions/velocities/etc directly in data object
export function positionNode(d, i, s) {
  const node = s[i];
  d3.select(node).attr('transform', 'translate(' + d.x + ',' + d.y + ')');
}

// position edge line between start/end nodes of edge
export function positionEdge(d, i, s) {
  let x1 = d.source.x;
  let y1 = d.source.y;
  let x2 = d.target.x;
  let y2 = d.target.y;
  let path = '';

  // get angle between source/target in radians
  const angle = Math.atan2(y2 - y1, x2 - x1);

  // get radius of source/target nodes
  const sourceRadius = nodeRadius - 0.25;
  let targetRadius = nodeRadius - 0.25;
  // increase target node radius to bring tip of arrowhead out of circle
  if (d.directed)
    targetRadius += edgeArrowSize / 4;

  if (d.coincidentOffset === 0) {
    // if no coincident edges, or middle of odd number of coincident edges,
    // just draw straight line

    // bring start/end of line to edge of circles
    x1 += Math.cos(angle) * sourceRadius;
    y1 += Math.sin(angle) * sourceRadius;
    x2 -= Math.cos(angle) * targetRadius;
    y2 -= Math.sin(angle) * targetRadius;

    // straight line path
    path = ['M', x1, y1, 'L', x2, y2].join(' ');
  } else {
    // otherwise, if coincident edge, draw a curve

    // spread out contact points with circle over spread angle
    const angleOffset = edgeSpreadAngle * d.coincidentOffset;

    // bring start/end of curve to edge of circle
    x1 += Math.cos(angle + angleOffset) * sourceRadius;
    y1 += Math.sin(angle + angleOffset) * sourceRadius;
    x2 -= Math.cos(angle - angleOffset) * targetRadius;
    y2 -= Math.sin(angle - angleOffset) * targetRadius;

    // get straight line distance between start/end of curve
    const distance = Math.sqrt(Math.pow(x2 - x1, 2) + Math.pow(y2 - y1, 2));

    // get "sagitta" distance
    const sag = Math.min(edgeSpreadDistance, distance) * d.coincidentOffset;

    // get point distance "sag" away from midpoint of line
    const qX = (x2 + x1) / 2 - (2 * sag * (y2 - y1)) / distance;
    const qY = (y2 + y1) / 2 + (2 * sag * (x2 - x1)) / distance;

    // draw curve with handle point Q
    path = ['M', x1, y1, 'Q', qX, qY, x2, y2].join(' ');
  }

  // set edge path
  const edge = s[i];
  d3.select(edge).attr('d', path);
}

// position edge label in center of edge line and rotate
export function positionEdgeLabel(d, i, s) {
  let x1 = d.source.x;
  let y1 = d.source.y;
  let x2 = d.target.x;
  let y2 = d.target.y;

  // get angle between source/target in radians
  let angle = Math.atan2(y2 - y1, x2 - x1);

  // get radius of source/target nodes
  const sourceRadius = nodeRadius - 0.25;
  let targetRadius = nodeRadius - 0.25;
  // increase target node radius to bring tip of arrowhead out of circle
  if (d.directed)
    targetRadius += edgeArrowSize / 4;

  // spread out contact points with circle over spread angle
  const angleOffset = edgeSpreadAngle * d.coincidentOffset;

  // bring start/end of curve to edge of circle
  x1 += Math.cos(angle + angleOffset) * sourceRadius;
  y1 += Math.sin(angle + angleOffset) * sourceRadius;
  x2 -= Math.cos(angle - angleOffset) * targetRadius;
  y2 -= Math.sin(angle - angleOffset) * targetRadius;

  // get straight line distance between start/end of curve
  const distance = Math.sqrt(Math.pow(x2 - x1, 2) + Math.pow(y2 - y1, 2));

  // get "sagitta" distance
  const sag = Math.min(edgeSpreadDistance, distance) * d.coincidentOffset;

  // get anchor point of text, point distance "sag" away from midpoint of line
  const textX = (x2 + x1) / 2 - (sag * (y2 - y1)) / distance;
  const textY = (y2 + y1) / 2 + (sag * (x2 - x1)) / distance;

  // get angle of text in degrees
  angle = (angle / (2 * Math.PI)) * 360;
  // rotate text to always show upright
  if (angle > 90)
    angle -= 180;
  if (angle <= -90)
    angle += 180;

  // set vertical alignment of text relative to anchor point
  let dy = -0.35 * edgeFontSize;
  // always place text on "outside" side of curve
  if (sag < 0 && d.source.x > d.target.x)
    dy = 1.1 * edgeFontSize;

  // set edge text transform
  const edgeLabel = s[i];
  d3.select(edgeLabel)
    .attr('x', 0)
    .attr('y', 0)
    .attr('dy', dy)
    .attr(
      'transform',
      'translate(' + textX + ',' + textY + ') rotate(' + angle + ') '
    );
}
