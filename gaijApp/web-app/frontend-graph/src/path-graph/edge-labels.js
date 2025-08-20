import React from 'react';
import { Component } from 'react';
import { connect } from 'react-redux';
import * as d3 from 'd3';

import { edgeFontSize, inkColor } from './constants.js';

// graph edge label text updater
export class GraphEdgeLabels extends Component {
  // when component updates
  componentDidUpdate() {
    this.update();
  }

  // update
  update = () => {
    const data = this.props.graph;
    const layer = d3.select('#graph_edge_label_layer');

    const edgeLabels = layer.selectAll('.graph_edge_label').data(data.edges);

    edgeLabels
      .enter()
      .append('text')
      .on('click', this.props.onNodeEdgeClick)
      .on('mouseenter', this.props.onNodeEdgeHover)
      .on('mouseleave', this.props.onNodeEdgeUnhover)
      .merge(edgeLabels)
      .attr('class', 'graph_edge_label')
      .attr('font-size', edgeFontSize)
      .attr('font-weight', 500)
      .attr('text-anchor', 'middle')
      .attr('user-select', 'none')
      .attr('fill', inkColor)
      .style('cursor', 'pointer')
      .text((d) => d.kind);

    edgeLabels.exit().remove();
  };

  // display component
  render() {
    return <></>;
  }
}
// connect component to global state
GraphEdgeLabels = connect((state) => ({
  graph: state.graph
}))(GraphEdgeLabels);
