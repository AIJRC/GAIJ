import React from 'react';
import { Component } from 'react';

import { Tooltip } from '../utils/tooltip';
import './number-box.css';

// number input box component
export class NumberBox extends Component {
  // intialize component
  constructor(props) {
    super(props);

    this.state = {};
    this.state.value = this.props.value;
  }

  // when component updates
  componentDidUpdate(prevProps) {
    if (this.props.value !== prevProps.value)
      this.setState({ value: this.props.value });
  }

  // when user changes field
  onChange = (event) => {
    this.setState({ value: event.target.value });
    if (event.nativeEvent.data === undefined)
      this.onArrows(event.target.value);
    else
      this.onType(event.target.value);
  };

  // when user presses key in box
  onKeyPress = (event) => {
    if (event.key.toLowerCase() === 'enter')
      event.target.blur();
  };

  // when user un-focuses field
  onBlur = (event) => {
    this.onSubmit(event.target.value);
  };

  // when box changed via arrow buttons or arrow keys
  onArrows = (value) => {
    if (this.props.onArrows)
      this.props.onArrows(value);
  };

  // when box changed via typing or copy/paste
  onType = (value) => {
    if (this.props.onType)
      this.props.onType(value);
  };

  // when box change submitted
  onSubmit = (value) => {
    if (this.props.onSubmit)
      this.props.onSubmit(value);
  };

  // display component
  render() {
    return (
      <Tooltip text={this.props.tooltipText}>
        <input
          type='number'
          className='number_box'
          onChange={this.onChange}
          onKeyPress={this.onKeyPress}
          onBlur={this.onBlur}
          min={this.props.min}
          step={this.props.step}
          max={this.props.max}
          value={this.state.value}
        />
      </Tooltip>
    );
  }
}
