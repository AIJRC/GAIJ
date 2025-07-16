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

    const toTitleCase = str =>
      str.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());

    let fields = [];

    if (element.elementType === 'node') {
      const primaryFields = ['metanode', 'neo4j_id'].map(field => ({
        firstCol: toTitleCase(field),
        secondCol: String(element[field] || '')
      }));
      fields.push({ section: 'Primary', fields: primaryFields });
    }

    if (element.metanode === 'Company' && element.properties) {

      console.log("Available property keys:", Object.keys(element.properties));
      const props = element.properties;

      const taxKeys = ['name', 'id', 'company_address', 'company_type', 'parent_company', 'leadership', 'subsidiaries'];
      const externalKeys = Object.keys(props).filter(k => k.startsWith('ext_'));
      const redFlagKeys = Object.keys(props).filter(k =>
        !taxKeys.includes(k) && !k.startsWith('ext_')
      );

      const formatProps = keys => keys
        .filter(k => k !== 'version_control' && k in props)
        .map(k => ({
          firstCol: toTitleCase(k),
          secondCol: String(props[k])
        }));

      const formatPropsRF = keys => {
        const used = new Set();
        const rows = [];

        keys.forEach(k => {
          if (used.has(k)) return;
          used.add(k);

          const value = String(props[k]);

          // Handle flag + details combo
          if (k.endsWith('_flag')) {
            const base = k.slice(0, -5); // remove "_flag"
            const detailKey = `${base}_details`;

            let label = toTitleCase(base);
            let detail = props[detailKey];

            if (detailKey in props) used.add(detailKey);

            rows.push({
              firstCol: `${label} Flag`,
              secondCol: value
            });

            if (detail) {
              rows.push({
                firstCol: `${label} Details`,
                secondCol: String(detail)
              });
            }
          } else if (!k.endsWith('_details')) {
            rows.push({
              firstCol: toTitleCase(k),
              secondCol: value
            });
          }
        });

        return rows;
      };

            
      if (taxKeys.some(k => k in props))
        fields.push({ section: 'Company Info from tax record', fields: formatProps(taxKeys) });

      if (externalKeys.length)
        fields.push({ section: 'External Info', fields: formatProps(externalKeys) });

      if (redFlagKeys.length)
        fields.push({ section: 'Red Flags', fields: formatPropsRF(redFlagKeys) });
    }

    return fields;

    // let order = [];
    // // get primary fields from top level of node/edge
    // let primaryFields = [];
    // if (element.elementType === 'node') {
    //   primaryFields = ['metanode', 'neo4j_id'];
    //   order = [
    //     'name',
    //     'metanode',
    //     'source',
    //     'url',
    //     'description',
    //     'identifier',
    //     'neo4j_id'
    //   ];
    // }
    // if (element.elementType === 'edge') {
    //   primaryFields = ['kind', 'directed', 'neo4j_id'];
    //   order = ['kind', 'neo4j_id', 'source'];
    // }

    // // get first/second column text (key/value) for each field
    // primaryFields = primaryFields.map((field) => ({
    //   firstCol: field,
    //   secondCol: String(element[field] || '')
    // }));

    // // get 'extra fields' from node/edge 'properties' field
    // let extraFields = [];
    // if (element.properties) {
    //   extraFields = Object.keys(element.properties)
    //     // Filter out the 'version_control' key
    //     .filter(field => field !== 'version_control')
    //     .map((field) => ({
    //       firstCol: field,
    //       // firstCol: field.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase()),
    //       secondCol: String(element.properties[field] || '')
    //     }));
    // }

    // // combine primary and extra fields
    // let fields = primaryFields.concat(extraFields);

    // // display fields in custom order
    // fields = sortCustom(fields, order, 'firstCol');

    // return fields;
  };

  // display component
  render() {
    const groupedFields = this.getFields();

    return (
      <div className="selected-info">
        {groupedFields.map(({ section, fields }, i) => {
          const cleanedFields = fields.filter(f => f.secondCol && f.secondCol.trim() !== '');
          if (!cleanedFields.length) return null;

          const bodyContents = fields.map(field => [
            field.firstCol,
            this.props.tooltipDefinitions[field.firstCol],
            field.secondCol
          ]);
          return (
            <div key={i} className="info-section">
              <h3>{section}</h3>
              <InfoTable bodyContents={bodyContents} />
            </div>
          );
        })}
      </div>
      // <div className="selected-info">
      //   {groupedFields.map(({ section, fields }, i) => (
      //     <div key={i} className="info-section">
      //       <h3>{section}</h3>
      //       <InfoTable fields={fields} />
      //     </div>
      //   ))}
      // </div>
    );
  }



  // render() {
  //   const fields = this.getFields();

  //   const bodyContents = fields.map((field) => [
  //     field.firstCol,
  //     this.props.tooltipDefinitions[field.firstCol],
  //     field.secondCol
  //   ]);

  //   return (
  //     <div id='graph_info_container'>
  //       {bodyContents.length > 0 && <InfoTable bodyContents={bodyContents} />}
  //       {!bodyContents.length > 0 && (
  //         <div className='center light'>
  //           Click on or hover over a node or edge
  //         </div>
  //       )}
  //     </div>
  //   );
  // }
}
// connect component to global state
SelectedInfo = connect((state) => ({
  tooltipDefinitions: state.tooltipDefinitions
}))(SelectedInfo);
