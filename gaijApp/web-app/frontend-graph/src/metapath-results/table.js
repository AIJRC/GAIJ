import React from 'react';
import { Component } from 'react';
import { connect } from 'react-redux';
import { faCheck } from '@fortawesome/free-solid-svg-icons';
import { faTimes } from '@fortawesome/free-solid-svg-icons';

import { IconButton } from '../utils/buttons';
import { CollapsibleSection } from '../components/collapsible-section';
import { setMetapaths } from './actions.js';
import { metapathChips } from '../components/chips.js';

// metapath results table component
export class MetapathResults extends Component {
  // when user clicks checkbox
  onChange = (newData) => {
    this.props.dispatch(
      setMetapaths({ metapaths: newData, updateUrl: true })
    );
  };

  // check/uncheck all metapaths
  setAll = (checked) => {
    const newMetapaths = [...this.props.metapaths];
    for (const metapath of newMetapaths)
      metapath.checked = checked;
    this.onChange(newMetapaths);
  };

  // display component
  render() {
    if (!this.props.metapaths.length)
      return <></>;

    return (
      <CollapsibleSection
        label='Paths'
        tooltipText='Types of paths connecting the source and target node'
      >
        <div className='table_control_button_container'>
          <IconButton
            text='select all'
            icon={faCheck}
            onClick={() => this.setAll(true)}
          />
          <IconButton
            text='deselect all'
            icon={faTimes}
            onClick={() => this.setAll(false)}
          />
        </div>
        <div className='metapath_results_table'>
          {this.props.metapaths.map((metapath, index) => (
            <div key={index} className='metapath_row'>
              <input
                type='checkbox'
                checked={metapath.checked || false}
                onChange={() => {
                  const newMetapaths = [...this.props.metapaths];
                  newMetapaths[index].checked = !newMetapaths[index].checked;
                  this.onChange(newMetapaths);
                }}
              />
              <div className='metapath_chips'>
                {metapathChips(metapath.paths)}
              </div>
            </div>
          ))}
        </div>
      </CollapsibleSection>
    );
  }
}

// connect component to global state
MetapathResults = connect((state) => ({
  metapaths: state.metapaths
}))(MetapathResults);