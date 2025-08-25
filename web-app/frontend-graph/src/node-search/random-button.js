import React from 'react';
import { Component } from 'react';
import { connect } from 'react-redux';
import { faDice } from '@fortawesome/free-solid-svg-icons';
import { IconButton } from '../utils/buttons';
// random button component
export class RandomButton extends Component {
  // when user clicks button
  onClick = async () => {
    // Disable random functionality for now
    console.log('Random node selection is not available in this version');
  };

  // display component
  render() {
    return (
      <IconButton
        className='random_button'
        icon={faDice}
        text='random'
        onClick={this.onClick}
      />
    );
  }
}
// connect component to global state
RandomButton = connect()(RandomButton);
