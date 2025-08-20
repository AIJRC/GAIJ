import React from 'react';
import { Component } from 'react';
import { connect } from 'react-redux';

import { InfoTable } from '../utils/InfoTable';
import { sortCustom } from '../utils';

// node results table component
// displays details about source/target node
export class NodeTable extends Component {
  // get primary rows entries
  getPrimaryRows = () => {
    const fieldLabels = {
      'name': 'Name'
    };

    const rows = ['name'].map((field) => {
      return {
        firstCol: fieldLabels[field],
        secondCol: String(this.props.node[field])
      }
    });
    return rows;
  };

  // get extra row entries
  getExtraRows = () => {
    const fieldLabels = {
      'id': 'Tax Number',
      'type': 'Type',
      'address': 'Address',
      'description': 'Description'
    };

    const rows = Object.keys(this.props.node.properties)
      .filter((field) => field !== 'source' && field !== 'url' && field !== 'name')
      .map((field) => ({
        firstCol: fieldLabels[field] || field.charAt(0).toUpperCase() + field.slice(1),
        secondCol: String(this.props.node.properties[field])
      }));

    return rows;
  };

  render() {
    let rows = this.getPrimaryRows().concat(this.getExtraRows());

    // display fields in custom order
    const order = [
      'name',
      'description'
    ];
    rows = sortCustom(rows, order, 'firstCol');

    // make row components from cols
    const bodyContents = rows.map((row, index) => [
      row.firstCol,
      this.props.tooltipDefinitions[row.firstCol],
      row.secondCol
    ]);

    return (
      <InfoTable className='node_results_table' bodyContents={bodyContents} />
    );
  }
}
// connect component to global state
NodeTable = connect((state) => ({
  tooltipDefinitions: state.tooltipDefinitions
}))(NodeTable);
