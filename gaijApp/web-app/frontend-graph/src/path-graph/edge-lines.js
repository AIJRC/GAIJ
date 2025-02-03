import React from 'react';
import { Component } from 'react';
import { connect } from 'react-redux';
import * as d3 from 'd3';

import { inkColor, edgeThickness } from './constants.js';

// graph edge line updater
export class GraphEdgeLines extends Component {
  // when component updates
  componentDidUpdate() {
    this.update();
  }

  // update
  update = () => {
    const data = this.props.graph;
    const layer = d3.select('#graph_edge_line_layer');

    const edgeLines = layer.selectAll('.graph_edge_line').data(data.edges);

    edgeLines
      .enter()
      .append('path')
      .merge(edgeLines)
      .attr('class', 'graph_edge_line')
      .attr('marker-end', (d) => (d.directed ? 'url(#graph_arrowhead)' : ''))
      .attr('fill', 'none')
      .attr('stroke', inkColor)
      .attr('stroke-width', edgeThickness)
      .style('stroke-dasharray', (d) =>
        d.selected || d.hovered
          ? edgeThickness * 2 + ' ' + edgeThickness
          : 'none'
      );

    edgeLines.exit().remove();
  };

  // display component
  render() {
    return <></>;
  }
}
// connect component to global state
GraphEdgeLines = connect((state) => ({
  graph: state.graph
}))(GraphEdgeLines);
