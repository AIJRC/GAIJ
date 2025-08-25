import React from 'react';
import { Component } from 'react';

import { Button } from '../utils/buttons';
import { MetanodeChip } from '../components/chips.js';

import './filter-button.css';

// filter button component
export class FilterButton extends Component {
  // initialize component
  constructor() {
    super();

    this.state = {};
    this.state.filters = [];
    this.state.tempActive = null;
  }

  // when component mounts
  componentDidMount() {
    window.addEventListener('mouseup', this.onMouseUp);
  }

  // when component unmounts
  componentWillUnmount() {
    window.removeEventListener('mouseup', this.onMouseUp);
  }

  // when user presses mouse down on button
  onMouseDown = () => {
    this.props.beginDrag(!this.props.active);
    this.props.addToDragList(this.props.name);
    this.setState({ tempActive: !this.props.active });
  };

  // when user moves mouse across button
  onMouseMove = () => {
    if (typeof this.props.drag === 'boolean') {
      this.props.addToDragList(this.props.name);
      this.setState({ tempActive: this.props.drag });
    }
  };

  // when user releases mouse anywhere
  onMouseUp = () => {
    this.setState({ tempActive: null });
  };

  // when user presses key on button
  onKeyDown = () => {
    this.props.toggle(this.props.name);
  }

  // display component
  render() {
    let active;
    if (typeof this.state.tempActive === 'boolean')
      active = this.state.tempActive;
    else
      active = this.props.active;

    return (
      <Button
        className='node_search_filter_button'
        disabled={!active}
        tooltipText={this.props.tooltipText + ' Ctrl+click to solo.'}
        onCtrlClick={() => this.props.solo(this.props.name)}
        onMouseDown={this.onMouseDown}
        onMouseMove={this.onMouseMove}
        onKeyDown={this.onKeyDown}
      >
        <MetanodeChip type={this.props.name} />
        {this.props.name}
      </Button>
    );
  }
}
