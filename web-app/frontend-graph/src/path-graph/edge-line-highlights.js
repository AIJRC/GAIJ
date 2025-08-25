import React from 'react';
import { Component } from 'react';
import { connect } from 'react-redux';
import * as d3 from 'd3';

import { highlightColor, edgeArrowSize } from './constants.js';

// graph edge line highlight updater
export class GraphEdgeLineHighlights extends Component {
  // when component updates
  componentDidUpdate() {
    this.update();
  }

  // update
  update = () => {
    const data = this.props.graph;
    const layer = d3.select('#graph_edge_line_highlight_layer');

    const edgeLineHighlights = layer
      .selectAll('.graph_edge_line_highlight')
      .data(data.edges.filter((d) => d.highlighted === true));

    edgeLineHighlights
      .enter()
      .append('path')
      .merge(edgeLineHighlights)
      .attr('class', 'graph_edge_line_highlight')
      .attr('fill', 'none')
      .attr('stroke', highlightColor)
      .attr('stroke-width', edgeArrowSize)
      .attr('stroke-linecap', 'square');

    edgeLineHighlights.exit().remove();
  };
  // display component
  render() {
    return <></>;
  }
}
// connect component to global state
GraphEdgeLineHighlights = connect((state) => ({
  graph: state.graph
}))(GraphEdgeLineHighlights);
