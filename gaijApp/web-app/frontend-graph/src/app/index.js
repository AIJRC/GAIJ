import React from 'react';
import { Component } from 'react';
import { connect } from 'react-redux';

import { NodeSearch } from '../node-search';
import { NodeResults } from '../node-results';
// import { Results } from '../results';
import { PathGraph } from '../path-graph';
import { loadStateFromUrl } from './actions.js';
import { fetchAndSetDefinitions } from './actions.js';
import { fetchAndSetPaths } from '../path-results/actions';
import { testConnection } from '../backend-queries';

import './index.css';
import '../styles/global.css';

// Note about class arrow functions vs normal functions:
//
// Arrow functions automatically bind "this", but do not get added to the class
// prototype, and thus get duplicated for every instance of the class. For
// convenience, syntax aesthetics, and mitigation of human errors (forgetting
// to bind "this"), arrow functions are used in classes, with two exceptions:
// 1) react life-cycle methods (componentDidUpdate, render, etc) and 2) in
// cases where there will be many instances of the class (say, > 10), like the
// reusable "widgets" in /components.

// main app component
class App extends Component {
  // initialize component
  constructor(props) {
    super(props);
    this.state = {
      isPathsLoading: false
    };
    this.loadStateFromUrl = this.loadStateFromUrl.bind(this);
    this.props.dispatch(fetchAndSetDefinitions());
  }

  // load source/target nodes, checked metapaths, etc from url
  loadStateFromUrl() {
    this.props.dispatch(loadStateFromUrl());
  }

  async componentDidMount() {
    await testConnection();
    this.loadStateFromUrl();
    window.addEventListener('popstate', this.loadStateFromUrl);
  }

  // when component updates
  componentDidUpdate(prevProps) {
    if (prevProps.sourceNode.id !== this.props.sourceNode.id) {
      if (this.props.sourceNode.id && !this.state.isPathsLoading) {
        this.setState({ isPathsLoading: true }, async () => {
          try {
            await this.props.dispatch(
              fetchAndSetPaths({
                sourceNodeId: this.props.sourceNode.id,
                paths: [],
                nodes: {},
                relationships: {},
                preserveChecks: true
              })
            );
          } finally {
            this.setState({ isPathsLoading: false });
          }
        });
      } else if (!this.props.sourceNode.id) {
        this.props.dispatch(
          fetchAndSetPaths({
            paths: [],
            nodes: {},
            relationships: {}
          })
        );
      }
    }
  }

  render() {
    const { sourceNode } = this.props;
    const shouldRenderGraph = sourceNode?.id && !this.state.isPathsLoading;

    return (
      <>
        <NodeSearch />
        {shouldRenderGraph && <NodeResults />}
        {shouldRenderGraph && <PathGraph />}
      </>
    );
  }
}
// connect component to global state
App = connect((state) => ({
  sourceNode: state.sourceNode
}))(App);
export { App };
