import React from 'react';
import { Component } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';

import { Tooltip } from './tooltip.js';

// Create a wrapper component for FontAwesomeIcon that uses default parameters instead of defaultProps
const Icon = ({ icon, className, ...props }) => (
  <FontAwesomeIcon 
    icon={icon} 
    className={className || ''} 
    {...props} 
  />
);

// //////////////////////////////////////////////////
// INPUT PROPS
// //////////////////////////////////////////////////

// children - jsx
// children react components to put inside the button

// onClick - function
// called when button is clicked

// onCtrlClick - function
// called when button is clicked and ctrl button is held

// onShiftClick - function
// called when button is clicked and shift button is held

// onMouseDown - function
// called when mouse is pressed down on button

// onMouseMove - function
// called when mouse moves over button

// onMouseUp - function
// called when mouse is released on button

// className - string
// the className to apply to the button

// tooltipText - string
// text to display in tooltip when button is hovered

// disabled - boolean
// the data-disabled attribute value to be applied to the button

// //////////////////////////////////////////////////
// COMPONENT
// //////////////////////////////////////////////////

const flashTime = 1000;

// button component
export class Button extends Component {
  // initialize component
  constructor() {
    super();

    this.onClick = this.onClick.bind(this);
    this.onMouseDown = this.onMouseDown.bind(this);
    this.onMouseMove = this.onMouseMove.bind(this);
    this.onMouseUp = this.onMouseUp.bind(this);
    this.onKeyDown = this.onKeyDown.bind(this);
  }

  // when user clicks button
  onClick(event) {
    if (event.ctrlKey) {
      if (this.props.onCtrlClick)
        this.props.onCtrlClick(event);
    } else if (event.shiftKey) {
      if (this.props.onShiftClick)
        this.props.onShiftClick(event);
    } else if (this.props.onClick)
      this.props.onClick(event);
  }

  // when user presses down on button
  onMouseDown(event) {
    if (event.button === 0 && this.props.onMouseDown)
      this.props.onMouseDown(event);
  }

  // when user moves mouse across button
  onMouseMove(event) {
    if (this.props.onMouseMove)
      this.props.onMouseMove(event);
  }

  // when user releases button
  onMouseUp(event) {
    if (event.button === 0 && this.props.onMouseUp)
      this.props.onMouseUp(event);
  }

  // when user presses key with button focused
  onKeyDown(event) {
    if (
      (event.key.toLowerCase() === 'enter' ||
        event.key.toLowerCase() === ' ') &&
      this.props.onKeyDown
    )
      this.props.onKeyDown(event);
  }

  // display component
  render() {
    const Button = this.props.href ? 'a' : 'button';
    return (
      <Tooltip text={this.props.tooltipText}>
        <Button
          className={'button ' + this.props.className || ''}
          href={this.props.href}
          onClick={this.onClick}
          onMouseDown={this.onMouseDown}
          onMouseMove={this.onMouseMove}
          onMouseUp={this.onMouseUp}
          onKeyDown={this.onKeyDown}
          data-disabled={this.props.disabled}
        >
          {this.props.children}
        </Button>
      </Tooltip>
    );
  }
}

// //////////////////////////////////////////////////
// INPUT PROPS
// //////////////////////////////////////////////////

// same as Button above, and...

// text - string
// text to display in the button

// icon - FontAwesomeIcon
// the font awesome icon object from '@fortawesome/free-solid-svg-icons' to
// display next to the text

// checked - boolean
// the data-checked attribute value to be applied to the button

// //////////////////////////////////////////////////
// COMPONENT
// //////////////////////////////////////////////////

// icon button component
// link colored button with text and icon to right
// icon gets the attribute data-checked to allow desired CSS styling
export class IconButton extends Component {
  // initialize component
  constructor() {
    super();

    this.state = {};
    this.state.flashing = false;

    this.flash = this.flash.bind(this);
    this.timer = null;
  }

  flash() {
    this.setState({ flashing: true });
    window.clearTimeout(this.timer);
    this.timer = window.setTimeout(
      () => this.setState({ flashing: false }),
      flashTime
    );
  }

  // display component
  render() {
    let text = this.props.text;
    let icon = this.props.icon;

    if (this.props.flashText && this.state.flashing)
      text = this.props.flashText;
    if (this.props.flashIcon && this.state.flashing)
      icon = this.props.flashIcon;

    return (
      <Button
        className={(this.props.className || '') + ' blue small'}
        tooltipText={this.props.tooltipText}
        href={this.props.href}
        onClick={() => {
          if (this.props.onClick)
            this.props.onClick();
          this.flash();
        }}
        onCtrlClick={() => {
          if (this.props.onCtrlClick)
            this.props.onCtrlClick();
          this.flash();
        }}
        onShiftClick={() => {
          if (this.props.onShiftClick)
            this.props.onShiftClick();
          this.flash();
        }}
      >
        <span>{text}</span>
        <Icon icon={icon} data-checked={this.props.checked} />
      </Button>
    );
  }
}
