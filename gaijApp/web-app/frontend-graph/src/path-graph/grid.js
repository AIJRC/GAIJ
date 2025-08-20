import React from 'react';
import { Component } from 'react';

import {
  nodeRadius,
  edgeThickness,
  inkColor,
  gridSpacing,
  gridMultiple
} from './constants.js';

// how many grid cells to extend in each cardinal direction from origin
const boundary = 50;

// graph grid component
export class GraphGrid extends Component {
  // display component
  render() {
    const lines = [];

    for (let index = -boundary; index <= boundary; index++) {
      const xy = index * gridSpacing;
      const major = index % gridMultiple === 0;
      lines.push(
        <line
          key={index * 2}
          x1={-boundary * gridSpacing}
          y1={xy}
          x2={boundary * gridSpacing}
          y2={xy}
          stroke={inkColor}
          strokeWidth={major ? edgeThickness / 3 : edgeThickness / 10}
        />
      );
      lines.push(
        <line
          key={index * 2 + 1}
          x1={xy}
          y1={-boundary * gridSpacing}
          x2={xy}
          y2={boundary * gridSpacing}
          stroke={inkColor}
          strokeWidth={major ? edgeThickness / 3 : edgeThickness / 10}
        />
      );
    }

    return (
      <>
        {lines}
        <line
          x1={-nodeRadius / 2}
          y1='0'
          x2={nodeRadius / 2}
          y2='0'
          stroke={inkColor}
          strokeWidth={edgeThickness}
        />
        <line
          x1='0'
          y1={-nodeRadius / 2}
          x2='0'
          y2={nodeRadius / 2}
          stroke={inkColor}
          strokeWidth={edgeThickness}
        />
      </>
    );
  }
}
