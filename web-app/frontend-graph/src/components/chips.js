import React from 'react';
import { Component } from 'react';
import { connect } from 'react-redux';

import { ReactComponent as ArrowBoth } from '../images/arrow-icon-both.svg';
import { ReactComponent as ArrowForward } from '../images/arrow-icon-forward.svg';
import { ReactComponent as ArrowBackward } from '../images/arrow-icon-backward.svg';
import { Tooltip } from '../utils/tooltip';

import './chips.css';

// metanode "chip" component
// colored circle with abbreviation text in middle
// eg (G) for "gene"
export class MetanodeChip extends Component {
  // display component
  render() {
    let fillColor = '#424242';
    let textColor = '#fafafa';
    let style = {};
    if (this.props.gaijStyles)
      style = this.props.gaijStyles[this.props.type];
    if (style && style.fill_color)
      fillColor = style.fill_color;
    if (style && style.text_color)
      textColor = style.text_color;

    // Get abbreviation for node type
    let abbrev = '';
    switch (this.props.type) {
      case 'Person':
        abbrev = 'P';
        break;
      case 'Company':
        abbrev = 'C';
        break;
      case 'Address':
        abbrev = 'A';
        break;
      default:
        abbrev = '?';
    }

    return (
      <Tooltip text={this.props.type}>
        <div className='metanode_chip' style={{ color: textColor }}>
          <svg viewBox='0 0 100 100'>
            <circle cx='50' cy='50' r='49' fill={fillColor} />
            <text
              x='50'
              y='50'
              textAnchor='middle'
              dominantBaseline='central'
              fill={textColor}
              fontSize='40'
            >
              {abbrev}
            </text>
          </svg>
        </div>
      </Tooltip>
    );
  }
}
// connect component to global state
MetanodeChip = connect((state) => ({
  gaijStyles: state.gaijStyles
}))(MetanodeChip);

// metaedge "chip" component
// svg arrow with abbreviation text above
export class MetaedgeChip extends Component {
  // display component
  render() {
    // get edge direction icon
    let icon;
    switch (this.props.direction) {
      case 'backward':
        icon = <ArrowBackward />;
        break;
      case 'forward':
        icon = <ArrowForward />;
        break;
      default:
        icon = <ArrowBoth />;
        break;
    }

    let abbreviation = '';
    if (this.props.metagraph && this.props.metagraph.kind_to_abbrev)
      abbreviation = this.props.metagraph.kind_to_abbrev[this.props.type];

    return (
      <Tooltip text={this.props.type}>
        <div
          className='metaedge_chip'
          data-name={this.props.type}
          data-abbreviation={abbreviation}
        >
          {icon}
        </div>
      </Tooltip>
    );
  }
}
// connect component to global state
MetaedgeChip = connect((state) => ({
  metagraph: state.metagraph
}))(MetaedgeChip);

// get html of metapath in form of visualization chips
export function metapathChips(edges) {
  const path = edges.map((entry, index) => {
    return (
      <React.Fragment key={index}>
        <MetanodeChip type={entry[0]} />
        <MetaedgeChip type={entry[2]} direction='forward' />
        {index === edges.length - 1 && <MetanodeChip type={entry[1]} />}
      </React.Fragment>
    );
  });

  return path;
}

// get html of path in form of visualization chips
export function pathChips(path, expanded) {
  return path.map((entry, index) => {
    if (entry.element === 'node') {
      return (
        <NodeChip
          key={index}
          type={entry.type}
          name={entry.name}
          expanded={expanded}
        />
      );
    }
    if (entry.element === 'edge') {
      return (
        <MetaedgeChip
          key={index}
          type={entry.type}
          direction={entry.direction}
        />
      );
    }
    return '';
  });
}

// node "chip" component
export class NodeChip extends Component {
  // display component
  render() {
    let fillColor = '#424242';
    let textColor = '#fafafa';
    let style = {};
    if (this.props.gaijStyles)
      style = this.props.gaijStyles[this.props.type];
    if (style && style.fill_color)
      fillColor = style.fill_color;
    if (style && style.text_color)
      textColor = style.text_color;

    return (
      <Tooltip text={this.props.name}>
        <span
          className='node_chip'
          style={{ background: fillColor, color: textColor }}
          data-expanded={this.props.expanded}
        >
          {this.props.name}
        </span>
      </Tooltip>
    );
  }
}
// connect component to global state
NodeChip = connect((state) => ({
  gaijStyles: state.gaijStyles
}))(NodeChip);
