import React from 'react';
import { Component } from 'react';
import { connect } from 'react-redux';

import { CollapsibleSection } from '../components/collapsible-section.js';
import { MetapathAttic } from './attic.js';
import { MetapathResults as MetapathTable } from './table.js';

// path results section component
export class MetapathResultsSection extends Component {
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
    if (!this.props.sourceNode.id || !this.props.targetNode.id) {
      placeholder = (
        <span className='light'>select a source and target node</span>
      );
    } else if (this.props.metapaths.length === 0)
      placeholder = <span className='light'>no results to show</span>;

    return (
      <CollapsibleSection
        label='Metapaths'
        tooltipText='Metapaths of length <= 3 between the source and target
        node'
      >
        <MetapathAttic
          showMore={this.state.showMore}
          toggleShowMore={this.toggleShowMore}
        />
        {this.props.metapaths.length > 0 && (
          <MetapathTable showMore={this.state.showMore} />
        )}
        {placeholder}
      </CollapsibleSection>
    );
  }
}

// connect component to global state
MetapathResultsSection = connect((state) => ({
  sourceNode: state.sourceNode,
  targetNode: state.targetNode,
  metapaths: state.metapaths
}))(MetapathResultsSection);

export { MetapathResultsSection as MetapathResults };
