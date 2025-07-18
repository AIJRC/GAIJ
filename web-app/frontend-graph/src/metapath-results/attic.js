import React from 'react';
import { Component } from 'react';
import { connect } from 'react-redux';
import { faDownload } from '@fortawesome/free-solid-svg-icons';
import { faCheck } from '@fortawesome/free-solid-svg-icons';
import { faAngleLeft } from '@fortawesome/free-solid-svg-icons';
import { faAngleRight } from '@fortawesome/free-solid-svg-icons';

import { IconButton } from '../utils/buttons';import { download } from './download.js';
import { togglePrecomputedMetapathsOnly } from './actions.js';

// table "attic" component
// contains buttons and info above table
export class MetapathAttic extends Component {
  // display component
  render() {
    // results/selected info
    const metapathCount = this.props.metapaths.length;
    const metapathSelectedCount = this.props.metapaths.filter(
      (metapath) => metapath.checked
    ).length;

    return (
      <div className='table_attic'>
        {this.props.metapaths.length > 0 && (
          <div className='small light left'>
            {metapathCount} results, {metapathSelectedCount} selected
          </div>
        )}
        {this.props.metapaths.length > 0 && (
          <IconButton
            text='.csv'
            icon={faDownload}
            className='link_button small'
            onClick={() =>
              download(
                this.props.sourceNode,
                this.props.targetNode,
                this.props.metapaths
              )
            }
            tooltipText='Download table as .csv file'
          />
        )}
        <IconButton
          text='precomputed only'
          icon={faCheck}
          className='link_button small'
          onClick={() => this.props.dispatch(togglePrecomputedMetapathsOnly())}
          checked={this.props.precomputedMetapathsOnly}
          tooltipText='Whether to show only precomputed metapaths, or show all
            metapaths. Warning: showing all can be slow.'
        />
        {this.props.metapaths.length > 0 && (
          <IconButton
            text={this.props.showMore ? 'collapse' : 'expand'}
            icon={this.props.showMore ? faAngleLeft : faAngleRight}
            className='link_button small'
            onClick={this.props.toggleShowMore}
            tooltipText='Expand table and show more columns'
          />
        )}
      </div>
    );
  }
}
// connect component to global state
MetapathAttic = connect((state) => ({
  sourceNode: state.sourceNode,
  targetNode: state.targetNode,
  metapaths: state.metapaths,
  precomputedMetapathsOnly: state.precomputedMetapathsOnly
}))(MetapathAttic);
