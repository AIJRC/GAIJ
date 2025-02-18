import React from 'react';
import { Component } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faAngleUp } from '@fortawesome/free-solid-svg-icons';
import { faAngleDown } from '@fortawesome/free-solid-svg-icons';

import { Button } from '../utils/buttons';
import './collapsible-section.css';

// accordion (collapse/expand) section component
export class CollapsibleSection extends Component {
  // initialize component
  constructor() {
    super();

    this.state = {};
    this.state.collapsed = false;
  }

  // when component mounts
  componentDidMount() {
    if (this.loadState())
      this.setState({ collapsed: true });
  }

  // load collapsed state from local storage if exists
  loadState = () => {
    const key = this.props.label;
    return key && window.localStorage.getItem(key) === 'true';
  };

  // save collapse state to local storage
  saveState = (collapsed) => {
    const key = this.props.label;
    if (key)
      window.localStorage.setItem(key, String(String(collapsed) === 'true'));
  };

  // toggle collapse/expand
  toggle = () => {
    this.setState({ collapsed: !this.state.collapsed });
    this.saveState(!this.state.collapsed);
  };

  // display component
  render() {
    return (
      <div
        className='collapsible_section'
        data-collapsed={this.state.collapsed}
      >
        <Button
          tooltipText={this.props.tooltipText}
          className='collapsible_section_button left'
          onClick={this.toggle}
        >
          <div>{this.props.label}</div>
          <FontAwesomeIcon
            icon={this.state.collapsed ? faAngleUp : faAngleDown}
          />
        </Button>
        <div
          className={
            'collapsible_section_content ' + (this.props.className || '')
          }
        >
          {this.props.children}
        </div>
      </div>
    );
  }
}
