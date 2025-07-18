import React from 'react';
import { Component } from 'react';
import { connect } from 'react-redux';
import * as d3 from 'd3';

import { nodeRadius, highlightColor, edgeArrowSize } from './constants.js';

// graph node circle highlight updater
export class GraphNodeCircleHighlights extends Component {
  // when component updates
  componentDidUpdate() {
    this.update();
  }

  // update
  update = () => {
    const data = this.props.graph;
    const layer = d3.select('#graph_node_circle_highlight_layer');

    const nodeCircleHighlights = layer
      .selectAll('.graph_node_circle_highlight')
      .data(data.nodes.filter((d) => d.highlighted === true));

    nodeCircleHighlights
      .enter()
      .append('circle')
      .merge(nodeCircleHighlights)
      .attr('class', 'graph_node_circle_highlight')
      .attr('r', nodeRadius)
      .attr('fill', 'none')
      .attr('stroke', highlightColor)
      .attr('stroke-width', edgeArrowSize);

    nodeCircleHighlights.exit().remove();
  };

  // display component
  render() {
    return <></>;
  }
}
// connect component to global state
GraphNodeCircleHighlights = connect((state) => ({
  graph: state.graph
}))(GraphNodeCircleHighlights);
