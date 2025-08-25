import React from 'react';
import { Component } from 'react';
import { connect } from 'react-redux';
import * as d3 from 'd3';

import { nodeRadius, inkColor, edgeThickness } from './constants.js';
import { nodeStyles } from '../config/styles.js';  // Import the styles

// graph node circle updater
export class GraphNodeCircles extends Component {
  // when component updates
  componentDidUpdate() {
    this.update();
  }

  // get node fill color based on type (metanode)
  getFillColor = (type) => {
    const style = nodeStyles[type];  // Use nodeStyles directly
    if (style && style.fill_color)
      return style.fill_color;
    else
      return inkColor;
  };

  // update
  update = () => {
    const data = this.props.graph;
    const layer = d3.select('#graph_node_circle_layer');

    const nodeCircles = layer.selectAll('.graph_node_circle').data(data.nodes);

    nodeCircles
      .enter()
      .append('circle')
      .call(this.props.nodeDragHandler)
      .on('click', this.props.onNodeEdgeClick)
      .on('mouseenter', this.props.onNodeEdgeHover)
      .on('mouseleave', this.props.onNodeEdgeUnhover)
      .merge(nodeCircles)
      .attr('class', 'graph_node_circle')
      .attr('r', nodeRadius)
      .attr('fill', (d) => this.getFillColor(d.metanode))
      .attr('stroke', (d) => (d.selected || d.hovered ? inkColor : 'none'))
      .attr('stroke-width', edgeThickness)
      .style('stroke-dasharray', edgeThickness * 2 + ' ' + edgeThickness)
      .style('cursor', 'pointer');

    nodeCircles.exit().remove();
  };

  // display component
  render() {
    return <></>;
  }
}
// connect component to global state
GraphNodeCircles = connect((state) => ({
  graph: state.graph
}))(GraphNodeCircles);  // Remove gaijStyles from state mapping
