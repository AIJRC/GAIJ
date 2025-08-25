import React from 'react';
import { Component } from 'react';
import { connect } from 'react-redux';

import { CollapsibleSection } from '../components/collapsible-section.js';

// results section component
export class Results extends Component {
  constructor() {
    super();
    this.state = {};
  }

  render() {
    let placeholder = <></>;
    if (!this.props.sourceNode.id) {
      placeholder = (
        <span className='light'>select a source node</span>
      );
    }

    return (
      <CollapsibleSection
        label='Connections'
        tooltipText='Direct connections from the selected node'
      >
        {placeholder}
      </CollapsibleSection>
    );
  }
}

Results = connect((state) => ({
  sourceNode: state.sourceNode
}))(Results);

export default Results;