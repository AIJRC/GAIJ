import React from 'react';
import { Component } from 'react';
import { connect } from 'react-redux';
import './node-type-selector.css';

export class NodeTypeSelector extends Component {
  render() {
    const types = ['Company', 'Person', 'Address', 'Tax Number'];
    
    return (
      <div className="node_search_form">
        <span className="small light node_search_form_label">
          {this.props.label}
        </span>
        <div className="search-input-wrapper">
          <select 
            className="node-type-select"
            onChange={(e) => this.props.onTypeSelect(e.target.value)}
            value={this.props.selectedType || ''}
          >
            <option value="">Select type...</option>
            {types.map(type => (
              <option key={type} value={type}>{type}</option>
            ))}
          </select>
        </div>
      </div>
    );
  }
}

NodeTypeSelector = connect()(NodeTypeSelector);