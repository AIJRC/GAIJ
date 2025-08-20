import React from 'react';
import { Component } from 'react';
import { connect } from 'react-redux';
import { faCodeBranch } from '@fortawesome/free-solid-svg-icons';
import { IconButton } from '../utils/buttons';
import { getCompaniesWithTwoSubsidiaries } from '../backend-queries.js';
import { setPaths } from '../path-graph/actions.js';

export class CompaniesWithTwoSubsidiariesButton extends Component {
  onClick = async () => {
    const graphData = await getCompaniesWithTwoSubsidiaries();
    
    if (graphData && graphData.nodes.length > 0) {
      const paths = graphData.edges.map((edge, index) => ({
        node_ids: [edge.source_neo4j_id, edge.target_neo4j_id],
        rel_ids: [index],
        checked: true,
        highlighted: false
      }));

      this.props.dispatch(
        setPaths({
          paths: paths,
          nodes: graphData.nodes.reduce((acc, node) => {
            acc[node.neo4j_id] = node;
            return acc;
          }, {}),
          relationships: graphData.edges.reduce((acc, edge, index) => {
            acc[index] = edge;
            return acc;
          }, {})
        })
      );
    }
  };

  render() {
    return (
      <IconButton
        className={`square_button ${this.props.className || ''}`}
        icon={faCodeBranch}
        text='Companies with Two Subsidiaries'
        onClick={this.onClick}
      />
    );
  }
}

CompaniesWithTwoSubsidiariesButton = connect()(CompaniesWithTwoSubsidiariesButton);