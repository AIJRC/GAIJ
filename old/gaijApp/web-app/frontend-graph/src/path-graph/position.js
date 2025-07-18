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

  function positionEdgeLine(d, x1, y1, x2, y2) {
    // Special handling for self-referential edges
    if (d.source.neo4j_id === d.target.neo4j_id) {
      const radius = nodeRadius * 4;
      const angle = Math.PI / 3; // 60 degrees
      
      // Calculate control points for the arch
      const cx1 = x1 + radius * Math.cos(angle);
      const cy1 = y1 + radius * Math.sin(angle);
      const cx2 = x1 + radius * Math.cos(angle * 0.5);
      const cy2 = y1 + radius * Math.sin(angle * 0.5);
      
      // Adjust end point to accommodate arrow
      if (d.directed) {
        const endRadius = nodeRadius - 0.25 + edgeArrowSize / 4;
        x2 += Math.cos(angle * 0.1) * endRadius;
        y2 += Math.sin(angle * 0.1) * endRadius;
      }
      
      // Create an arch path using different control points
      return `M ${x1} ${y1} 
              C ${cx1} ${cy1}, 
                ${cx2} ${cy2}, 
                ${x2} ${y2}`;
    }

    // Regular edge handling
    const angle = Math.atan2(y2 - y1, x2 - x1);
    const sourceRadius = nodeRadius - 0.25;
    let targetRadius = nodeRadius - 0.25;
    
    if (d.directed) {
      targetRadius += edgeArrowSize / 4;
    }

    const angleOffset = edgeSpreadAngle * d.coincidentOffset;
    const newX1 = x1 + Math.cos(angle + angleOffset) * sourceRadius;
    const newY1 = y1 + Math.sin(angle + angleOffset) * sourceRadius;
    const newX2 = x2 - Math.cos(angle - angleOffset) * targetRadius;
    const newY2 = y2 - Math.sin(angle - angleOffset) * targetRadius;

    const distance = Math.sqrt(Math.pow(newX2 - newX1, 2) + Math.pow(newY2 - newY1, 2));
    const sag = Math.min(edgeSpreadDistance, distance) * d.coincidentOffset;
    const mx = (newX2 + newX1) / 2 - (sag * (newY2 - newY1)) / distance;
    const my = (newY2 + newY1) / 2 + (sag * (newX2 - newX1)) / distance;

    return `M ${newX1} ${newY1} Q ${mx} ${my} ${newX2} ${newY2}`;
  }

  // Use positionEdgeLine for self-referential edges
  if (d.source.neo4j_id === d.target.neo4j_id) {
    const path = positionEdgeLine(d, x1, y1, x2, y2);
    const edge = s[i];
    d3.select(edge).attr('d', path);
    return;
  }

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
  let angle, textX, textY, dy;

  if (d.source.neo4j_id === d.target.neo4j_id) {
    

    const radius = nodeRadius * 4;
    const baseAngle = Math.PI / 3;
    
    // Position label at the top of the arch
    const labelAngle = baseAngle * 0.75;
    textX = x1 + radius * Math.cos(labelAngle);
    textY = y1 + radius * Math.sin(labelAngle);
    
    // Adjust text rotation for readability
    angle = (labelAngle / (2 * Math.PI)) * 360;
    if (angle > 90) angle -= 180;
    if (angle <= -90) angle += 180;
    
    dy = -0.35 * edgeFontSize;
  } else {

  // get angle between source/target in radians
  angle = Math.atan2(y2 - y1, x2 - x1);

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
  textX = (x2 + x1) / 2 - (sag * (y2 - y1)) / distance;
  textY = (y2 + y1) / 2 + (sag * (x2 - x1)) / distance;

  // get angle of text in degrees
  angle = (angle / (2 * Math.PI)) * 360;
  // rotate text to always show upright
  if (angle > 90)
    angle -= 180;
  if (angle <= -90)
    angle += 180;

  // set vertical alignment of text relative to anchor point
  dy = -0.35 * edgeFontSize;
  // always place text on "outside" side of curve
  if (sag < 0 && d.source.x > d.target.x)
    dy = 1.1 * edgeFontSize;
  }
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
