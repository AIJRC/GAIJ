import React from 'react';
import { Component } from 'react';
import { connect } from 'react-redux';
import { faUserTie } from '@fortawesome/free-solid-svg-icons';
import { IconButton } from '../utils/buttons';
import { getSharedLeadership } from '../backend-queries.js';
import { setPaths } from '../path-graph/actions.js';

export class SharedLeadershipButton extends Component {
  onClick = async () => {
    const graphData = await getSharedLeadership();
    
    if (graphData && graphData.nodes.length > 0) {
      const paths = graphData.edges.map((edge, index) => ({
        node_ids: [edge.source_neo4j_id, edge.target_neo4j_id],
        rel_ids: [index],
        checked: true,
        highlighted: false
      }));

      const formattedNodes = {};
      const formattedRelationships = {};

      graphData.nodes.forEach(node => {
        formattedNodes[node.neo4j_id] = {
          neo4j_id: node.neo4j_id,
          name: node.name,
          metanode: node.metanode,
          properties: node.properties
        };
      });

      graphData.edges.forEach((edge, index) => {
        formattedRelationships[index] = {
          source_neo4j_id: edge.source_neo4j_id,
          target_neo4j_id: edge.target_neo4j_id,
          kind: edge.kind,
          directed: edge.directed,
          properties: edge.properties
        };
      });

      this.props.dispatch(
        setPaths({
          paths: paths,
          nodes: formattedNodes,
          relationships: formattedRelationships
        })
      );
    }
  };

  render() {
    return (
      <IconButton
        className={`square_button ${this.props.className || ''}`}
        icon={faUserTie}
        text='People leading multiple companies'
        onClick={this.onClick}
      />
    );
  }
}

SharedLeadershipButton = connect()(SharedLeadershipButton);