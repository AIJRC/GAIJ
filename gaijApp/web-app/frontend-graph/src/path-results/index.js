import React from 'react';
import { Component } from 'react';
import { connect } from 'react-redux';

import { CollapsibleSection } from '../components/collapsible-section.js';
import { PathAttic } from './attic.js';
import { PathTable } from './table.js';

// path results section component
export class PathResults extends Component {
  // initialize component
  constructor() {
    super();

    this.state = {};
    this.state.showMore = false;
  }

  // toggle expanded table
  toggleShowMore = (event) => {
    if (event)
      event.preventDefault();

    this.setState({ showMore: !this.state.showMore });
  };

  // display component
  render() {
    let placeholder = <></>;
    const checkedMetapaths = this.props.metapaths.filter(
      (metapath) => metapath.checked
    );

    if (!checkedMetapaths.length)
      placeholder = <span className='light'>select a metapath</span>;
    else if (this.props.paths.length === 0)
      placeholder = <span className='light'>no results to show</span>;

    return (
      <CollapsibleSection
        label='Paths'
        tooltipText='Paths of length <= 3 between the source and target node'
      >
        {this.props.paths.length > 0 && (
          <PathAttic
            showMore={this.state.showMore}
            toggleShowMore={this.toggleShowMore}
          />
        )}
        {this.props.paths.length > 0 && (
          <PathTable showMore={this.state.showMore} />
        )}
        {placeholder}
      </CollapsibleSection>
    );
  }
}
// connect component to global state
PathResults = connect((state) => ({
  metapaths: state.metapaths,
  paths: state.paths
}))(PathResults);
