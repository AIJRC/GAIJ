import React from 'react';
import { Component } from 'react';
import { connect } from 'react-redux';

import { edgeArrowSize, inkColor } from './constants.js';

// graph definitions/header component
export class GraphDefs extends Component {
  // display component
  render() {
    const sourceName = this.props.sourceNode.name || '___';
    const targetName = this.props.targetNode.name || '___';
    const sourceType = this.props.sourceNode.metanode || '___';
    const targetType = this.props.targetNode.metanode || '___';

    return (
      <>
        <title>
          {sourceName} → {targetName}
        </title>
        <desc>
          {'<!--'}
          Graph visualization of the connectivity between {sourceName} (
          {sourceType}) and {targetName} ({targetType}).
          {'\n'}
          {'\n'}
          Created at {window.decodeURI(window.location.href)}
          {'\n'}
          {'\n'}
          
          {'-->'}
        </desc>
        <defs>
          <marker
            id='graph_arrowhead'
            viewBox='0 0 100 100'
            refX='80'
            refY='50'
            orient='auto'
            markerUnits='userSpaceOnUse'
            markerWidth={edgeArrowSize}
            markerHeight={edgeArrowSize}
          >
            <path
              d='
                M 0 0
                L 100 50
                L 0 100
              '
              fill={inkColor}
            />
          </marker>
        </defs>
      </>
    );
  }
}
// connect component to global state
GraphDefs = connect((state) => ({
  sourceNode: state.sourceNode,
  targetNode: state.targetNode
}))(GraphDefs);
