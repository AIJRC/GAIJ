import React from 'react';
import { Component } from 'react';
import { connect } from 'react-redux';

import { InfoTable } from '../utils/InfoTable';

import { sortCustom } from '../utils';


import './selected-info.css';

// selected info component
// shows table of info about selected node or edge in graph
export class SelectedInfo extends Component {
  // get fields of info from selected node/edge
  getFields = () => {
    const element = this.props.hoveredElement || this.props.selectedElement;

    if (!element)
      return [];

    let order = [];
    // get primary fields from top level of node/edge
    let primaryFields = [];
    if (element.elementType === 'node') {
      primaryFields = ['metanode', 'neo4j_id'];
      order = [
        'name',
        'metanode',
        'source',
        'url',
        'description',
        'identifier',
        'neo4j_id'
      ];
    }
    if (element.elementType === 'edge') {
      primaryFields = ['kind', 'directed', 'neo4j_id'];
      order = ['kind', 'neo4j_id', 'source'];
    }

    // get first/second column text (key/value) for each field
    primaryFields = primaryFields.map((field) => ({
      firstCol: field,
      secondCol: String(element[field] || '')
    }));

    // get 'extra fields' from node/edge 'properties' field
    let extraFields = [];
    if (element.properties) {
      extraFields = Object.keys(element.properties)
        // Filter out the 'version_control' key
        .filter(field => field !== 'version_control')
        .map((field) => ({
          firstCol: field,
          secondCol: String(element.properties[field] || '')
        }));
    }

    // combine primary and extra fields
    let fields = primaryFields.concat(extraFields);

    // display fields in custom order
    fields = sortCustom(fields, order, 'firstCol');

    return fields;
  };

  // display component
  render() {
    const fields = this.getFields();

    const bodyContents = fields.map((field) => [
      field.firstCol,
      this.props.tooltipDefinitions[field.firstCol],
      field.secondCol
    ]);

    return (
      <div id='graph_info_container'>
        {bodyContents.length > 0 && <InfoTable bodyContents={bodyContents} />}
        {!bodyContents.length > 0 && (
          <div className='center light'>
            Click on or hover over a node or edge
          </div>
        )}
      </div>
    );
  }
}
// connect component to global state
SelectedInfo = connect((state) => ({
  tooltipDefinitions: state.tooltipDefinitions
}))(SelectedInfo);
