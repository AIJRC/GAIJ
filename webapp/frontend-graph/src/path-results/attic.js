import React from 'react';
import { Component } from 'react';
import { connect } from 'react-redux';
import { faDownload } from '@fortawesome/free-solid-svg-icons';
import { faAngleLeft } from '@fortawesome/free-solid-svg-icons';
import { faAngleRight } from '@fortawesome/free-solid-svg-icons';

import { IconButton } from '../utils/buttons';import { download } from './download.js';

// table "attic" component
// contains buttons and info above table
export class PathAttic extends Component {
  // display component
  render() {
    const pathCount = this.props.paths.length;
    const pathSelectedCount = this.props.paths.filter((path) => path.checked)
      .length;
    const pathHighlightedCount = this.props.paths.filter(
      (path) => path.highlighted
    ).length;

    return (
      <div className='table_attic'>
        <div className='small light left'>
          {pathCount} results, {pathSelectedCount} selected,{' '}
          {pathHighlightedCount} highlighted
        </div>
        <IconButton
          text='.csv'
          icon={faDownload}
          className='link_button small'
          onClick={() =>
            download(
              this.props.sourceNode,
              this.props.targetNode,
              this.props.paths
            )
          }
          tooltipText='Download table as .csv file'
        />
        <IconButton
          text={this.props.showMore ? 'collapse' : 'expand'}
          icon={this.props.showMore ? faAngleLeft : faAngleRight}
          className='link_button small'
          onClick={this.props.toggleShowMore}
          tooltipText='Expand table'
        />
      </div>
    );
  }
}
// connect component to global state
PathAttic = connect((state) => ({
  sourceNode: state.sourceNode,
  targetNode: state.targetNode,
  paths: state.paths
}))(PathAttic);
