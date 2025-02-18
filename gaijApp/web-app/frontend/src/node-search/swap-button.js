import React from 'react';
import { Component } from 'react';
import { connect } from 'react-redux';
import { faExchangeAlt } from '@fortawesome/free-solid-svg-icons';

import { IconButton } from '../utils/buttons';import { swapSourceTargetNode } from './actions.js';

// swap button component
export class SwapButton extends Component {
  // when user clicks button
  onClick = () => {
    this.props.dispatch(swapSourceTargetNode());
  };

  // display component
  render() {
    return (
      <IconButton
        className='swap_button'
        icon={faExchangeAlt}
        text='swap'
        onClick={this.onClick}
      />
    );
  }
}
// connect component to global state
SwapButton = connect()(SwapButton);