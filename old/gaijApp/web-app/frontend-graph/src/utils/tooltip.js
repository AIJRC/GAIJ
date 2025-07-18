import React, { Component } from 'react';
import './tooltip.css';

const delay = 250;

export class Tooltip extends Component {
  constructor() {
    super();
    this.state = { show: false };
    this.timer = null;
  }

  onMouseEnter = () => {
    this.timer = window.setTimeout(() => {
      this.setState({ show: true });
    }, delay);
  };

  onMouseLeave = () => {
    window.clearTimeout(this.timer);
    this.setState({ show: false });
  };

  render() {
    if (!this.props.text)
      return this.props.children;

    return (
      <div 
        className='tooltip_container'
        onMouseEnter={this.onMouseEnter}
        onMouseLeave={this.onMouseLeave}
      >
        {this.props.children}
        {this.state.show && (
          <div className='tooltip'>
            {this.props.text}
          </div>
        )}
      </div>
    );
  }
}