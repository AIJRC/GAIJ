import React from 'react';
import { Component } from 'react';

import { Tooltip } from '../utils/tooltip';
import './number-box.css';

// number input box component
export class NumberBox extends Component {
  // intialize component
  constructor(props) {
    super(props);

    // Ensure initial value is valid
    const initialValue = isNaN(this.props.value) ? '' : this.props.value;
    this.state = {
      value: initialValue
    };
  }

  // when component updates
  componentDidUpdate(prevProps) {
    // Only update state if the value has changed, is different from current state, and is valid
    if (this.props.value !== prevProps.value && 
        this.props.value !== this.state.value && 
        !isNaN(this.props.value)) {
      this.setState({ value: this.props.value });
    }
  }

  // when user changes field
  onChange = (event) => {
    const newValue = event.target.value;
    
    // Always update the input field for UX, even if empty
    this.setState({ value: newValue });
    
    // Only trigger callbacks if we have a valid number
    if (newValue !== '' && !isNaN(newValue)) {
      if (event.nativeEvent.data === undefined) {
        this.onArrows(newValue);
      } else {
        this.onType(newValue);
      }
    }
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
    // Ensure we're not submitting invalid values
    if (value === '' || isNaN(value)) {
      // Reset to last valid value or default
      const resetValue = !isNaN(this.props.value) ? this.props.value : '';
      this.setState({ value: resetValue });
      return;
    }
    
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
