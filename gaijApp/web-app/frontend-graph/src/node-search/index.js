import React from 'react';
import { Component } from 'react';
import { connect } from 'react-redux';
import { SourceNode } from './source-node.js';
import { TopCompaniesButton } from './top-companies-button.js';
import { TopBoardMembersButton } from './top-board-members-button.js';
import { TopAddressesButton } from './top-addresses-button.js';
import { SharedLeadershipButton } from './shared-leadership-button.js';
import { ParentSubsidiaryLeadershipButton } from './parent-subsidiary-leadership-button.js';
import { CompaniesWithTwoSubsidiariesButton } from './get-companies-with-two-subsidiaries-button.js';

import { Statistics } from './statistics.js';
import './index.css';
import './button-group.css';

export class NodeSearch extends Component {
  render() {
    return (
      <div className='node_search'>
        <div className='node_search_content'>
          <SourceNode />
          <div className='button_group' style={{display: 'flex', justifyContent: 'center', gap: '10px'}}>
            <TopCompaniesButton className="square_button" />
            <TopBoardMembersButton className="square_button" />
            <TopAddressesButton className="square_button" />
            <SharedLeadershipButton className="square_button" />
            <ParentSubsidiaryLeadershipButton className="square_button" />
            <CompaniesWithTwoSubsidiariesButton className="square_button" />
          </div>
          <Statistics />
        </div>
      </div>
    );
  }
}

NodeSearch = connect((state) => ({
  metagraph: state.metagraph
}))(NodeSearch);
