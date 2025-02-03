import React from 'react';
import { Component } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faSearch, faTimes, faSpinner } from '@fortawesome/free-solid-svg-icons';

import { MetanodeChip } from '../components/chips.js';

import './text-box.css';

// text box sub-component of search box component
class TextBox extends Component {
  // initialize component
  constructor() {
    super();
    this.state = {
      focused: false,
      searchInProgress: false,
      noResults: false,
      hasConnections: false
    };
  }

  handleClear = (event) => {
    event.preventDefault();
    event.stopPropagation();
    
    if (this.props.selectedItem) {
      this.props.clearSelection();
      this.props.closeMenu();
    }
  };

  // when user types into text box
  onInput = async (event) => {
    // Persist the event since we're using it in an async operation
    event.persist();
    
    this.setState({ searchInProgress: true, noResults: false, hasConnections: false });
    
    // Store the value before the async operation
    const inputValue = event.target.value;
    
    // First trigger the parent's onChange to update the input value
    this.props.getInputProps().onChange(event);
    
    // Then trigger the search with the stored value
    const result = await this.props.onFocus(inputValue);
    
    if (inputValue === '') {
      this.props.clearSelection();
    } else if (result && result.connections && result.connections.edges && result.connections.edges.length > 0) {
      this.setState({ hasConnections: true });
    }
    
    this.setState({ searchInProgress: false });
  };

  // when user focuses text box
  onFocus = (event) => {
    this.props.onFocus(event.target.value);
    this.props.openMenu();
    this.setState({ focused: true });
  };

  // when user unfocuses text box
  onBlur = () => {
    this.setState({ focused: false });
    this.props.closeMenu();
  };

  // display component
  handleClear = () => {
    if (this.props.selectedItem) {
      this.props.clearSelection();
      this.props.onFocus(); // Trigger focus to ensure the input is ready for new text
      if (this.props.closeMenu) {
        this.props.closeMenu();
      }
    }
  };

  render() {
    let overlay = <></>;
    const showOverlay = !this.state.focused && 
      this.props.selectedItem?.metanode && 
      (this.props.nodeType === 'Tax Number' ? this.props.selectedItem?.properties?.id : this.props.selectedItem?.name) &&
      this.state.hasConnections;

    if (showOverlay) {
      overlay = (
        <div className='node_search_overlay'>
          <MetanodeChip type={this.props.selectedItem.metanode} />
          <span className='node_search_results_item_name nowrap'>
            {this.props.nodeType === 'Tax Number' ? this.props.selectedItem.properties.id : this.props.selectedItem.name}
          </span>
        </div>
      );
    }

    return (
      <>
        <input
          className='node_search_input'
          {...this.props.getInputProps({
            onChange: this.onInput,
            onFocus: this.onFocus,
            onBlur: this.onBlur,
            placeholder: this.props.nodeType === 'Tax Number' ? 
              'enter tax number (only showing nodes with connections)' : 
              'name or identifier (only showing nodes with connections)'
          })}
          ref={this.props.inputRef}
        />
        {overlay}
        <div 
          className='node_search_icon'
          onClick={this.handleClear}
          style={{ cursor: this.props.selectedItem ? 'pointer' : 'default' }}
        >
          <FontAwesomeIcon 
            icon={this.state.searchInProgress ? faSpinner : (this.props.selectedItem ? faTimes : faSearch)}
            spin={this.state.searchInProgress}
          />
        </div>
      </>
    );
  }
}

export { TextBox };