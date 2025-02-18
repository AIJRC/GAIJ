import React from 'react';
import { Component } from 'react';
import { connect } from 'react-redux';
import * as d3 from 'd3';

import { cutString } from '../utils/string';

import {
  nodeRadius,
  backgroundColor,
  nodeFontSize,
  nodeCharLimit
} from './constants.js';

// graph node label text updater
export class GraphNodeLabels extends Component {
  // when component updates
  componentDidUpdate() {
    this.update();
  }

  // get node text color based on type (metanode)
  getTextColor = (type) => {
    const style = this.props.gaijStyles[type];
    if (style && style.text_color)
      return style.text_color;
    else
      return backgroundColor;
  };

  // update
  getNodeText = (node) => {
    if (!node || !node.properties) return '';
    return node.properties.full_address || node.properties.name || node.name || '';
  };

  update = () => {
    const data = this.props.graph;
    const layer = d3.select('#graph_node_label_layer');

    const nodeLabels = layer.selectAll('.graph_node_label').data(data.nodes);

    nodeLabels
      .enter()
      .append('foreignObject')
      .attr('class', 'graph_node_label')
      .append('xhtml:div')
      .attr('xmlns', 'http://www.w3.org/1999/xhtml')
      .append('xhtml:span')
      .attr('xmlns', 'http://www.w3.org/1999/xhtml');

    layer
      .selectAll('.graph_node_label')
      .attr('x', -nodeRadius)
      .attr('y', -nodeRadius)
      .attr('width', nodeRadius * 2)
      .attr('height', nodeRadius * 2)
      .style('pointer-events', 'none')
      .select('div')
      .style('display', 'flex')
      .style('justify-content', 'center')
      .style('align-items', 'center')
      .style('width', '100%')
      .style('height', '100%')
      .style('box-sizing', 'border-box')
      .style('padding', nodeRadius * 0.25 + 'px')
      .select('span')
      .style('text-align', 'center')
      .style('font-size', nodeFontSize + 'px')
      .style('font-weight', 500)
      .style('color', (d) => this.getTextColor(d.metanode))
      .style('word-break', 'break-word')
      .html((d) => cutString(this.getNodeText(d), nodeCharLimit));

    nodeLabels.exit().remove();
  };

  // display component
  render() {
    return <></>;
  }
}
// connect component to global state
GraphNodeLabels = connect((state) => ({
  graph: state.graph,
  gaijStyles: state.gaijStyles
}))(GraphNodeLabels);
