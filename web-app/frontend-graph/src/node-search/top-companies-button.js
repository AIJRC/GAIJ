import React from 'react';
import { Component } from 'react';
import { connect } from 'react-redux';
import { faBuilding } from '@fortawesome/free-solid-svg-icons';
import { IconButton } from '../utils/buttons';
import { getTopCompanies } from '../backend-queries.js';
import { setSourceTargetNode } from './actions.js';
import { setPaths } from '../path-graph/actions.js'; 
// Add this import

export class TopCompaniesButton extends Component {
  onClick = async () => {
    const graphData = await getTopCompanies();
    console.log('Graph data received:', graphData);

    if (graphData && graphData.nodes.length > 0) {
      const mainCompany = graphData.nodes[0];

      // First set the source and target nodes
      this.props.dispatch(
        setSourceTargetNode({
          sourceNode: {
            id: mainCompany.neo4j_id,
            name: mainCompany.name,
            metanode: mainCompany.metanode,
            properties: mainCompany.properties
          },
          targetNode: {
            id: graphData.edges[0].target_neo4j_id,
            name: graphData.nodes.find(n => n.neo4j_id === graphData.edges[0].target_neo4j_id).name,
            metanode: 'Company',
            properties: graphData.nodes.find(n => n.neo4j_id === graphData.edges[0].target_neo4j_id).properties
          },
          updateUrl: true
        })
      );
  
      // Create paths array with all edges
      const paths = graphData.edges.map((edge, index) => ({
        node_ids: [edge.source_neo4j_id, edge.target_neo4j_id],
        rel_ids: [index],
        checked: true,
        highlighted: false
      }));
  
      // Format nodes and relationships
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
  
      // Then update the graph data
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
        icon={faBuilding}
        text='Top 10 Companies with highest number of subsidiaries'
        onClick={this.onClick}
      />
    );
  }
}

TopCompaniesButton = connect()(TopCompaniesButton);