import React from 'react';
import { Component } from 'react';
import ReactDOM from 'react-dom';
import { connect } from 'react-redux';

import { CollapsibleSection } from '../components/collapsible-section.js';
import { GraphAttic } from './attic.js';
import { Graph } from './graph.js';
import { SelectedInfo } from './selected-info.js';

import { minWidth, minHeight, maxWidth, maxHeight } from './constants.js';

// path graph section component
export class PathGraph extends Component {
  // initialize component
  constructor() {
    super();

    this.state = {
      width: window.innerWidth,
      height: 690,
      sectionWidth: window.innerWidth,
      selectedElement: null,
      hoveredElement: null,
      isInitialized: false,
      hasRendered: false,
      isProcessing: false
    };

    this.graphRef = React.createRef();
  }

  componentDidMount() {
    this.updateSectionWidth();
    window.addEventListener('resize', this.updateSectionWidth);
    
    // Graph only initializes if there are nodes
    if (this.props.graph?.nodes?.length > 0) {
      this.initializeGraph();
    }
}

componentDidUpdate(prevProps, prevState) {
    console.log('PathGraph componentDidUpdate:', {
      prevGraph: prevProps.graph,
      currentGraph: this.props.graph,
      hasNodes: this.props.graph?.nodes?.length > 0,
      isProcessing: this.state.isProcessing
    });

    if (this.state.isProcessing) {
      return;
    }

    // Graph updates when new data arrives
    if (this.props.graph !== prevProps.graph) {
      const hasNodes = this.props.graph?.nodes?.length > 0;
      
      // Remove the hasRendered condition to allow updates anytime
      if (hasNodes) {
        this.setState({ 
          isProcessing: true,
          hasRendered: true,
          isInitialized: true
        }, () => {
          if (this.graphRef.current) {
            this.graphRef.current.fitView();
          }
          this.setState({ isProcessing: false });
        });
      }
    }

    if (!this.state.isProcessing && 
        (this.state.width !== prevState.width || 
         this.state.height !== prevState.height)) {
      if (this.graphRef.current) {
        this.graphRef.current.fitView();
      }
    }
  }

  initializeGraph = () => {
    this.setState({
      isInitialized: true,
      hasRendered: true
    }, () => {
      if (this.graphRef.current) {
        setTimeout(() => {
          this.graphRef.current.fitView();
        }, 0);
      }
    });
  };

  // when component unmounts
  componentWillUnmount() {
    window.removeEventListener('resize', this.updateSectionWidth);
  }

  // set width of graph container
  setWidth = (width) => {
    if (Math.round(width) !== width)
      width = Math.round(width);
    if (width > maxWidth)
      width = maxWidth;
    if (width < minWidth)
      width = minWidth;
    this.setState({ width: width });
  };

  // set height of graph container
  setHeight = (height) => {
    if (Math.round(height) !== height)
      height = Math.round(height);
    if (height > maxHeight)
      height = maxHeight;
    if (height < minHeight)
      height = minHeight;
    this.setState({ height: height });
  };

  // expand graph container to width of window
  expandContainer = (proportionalHeight) => {
    const width = document.body.clientWidth - 20 - 20;
    this.setWidth(width);
    if (proportionalHeight)
      this.setHeight(Math.ceil((width * 3) / 4));
  };

  // collapse graph container to width of <section> element
  collapseContainer = (proportionalHeight) => {
    const width = ReactDOM.findDOMNode(this).clientWidth;
    this.setWidth(width);
    if (proportionalHeight)
      this.setHeight(Math.ceil((width * 3) / 4));
  };

  // get current width of <section> element
  updateSectionWidth = () => {
    this.setState({ sectionWidth: ReactDOM.findDOMNode(this).clientWidth });
  };

  //
  setSelectedElement = (element) => {
    this.setState({ selectedElement: element });
  };

  //
  setHoveredElement = (element) => {
    this.setState({ hoveredElement: element });
  };

  // display component
  render() {
    console.log('PathGraph render:', {
      hasNodes: this.props.graph?.nodes?.length > 0,
      isInitialized: this.state.isInitialized,
      hasRendered: this.state.hasRendered,
      isProcessing: this.state.isProcessing,
      graphProps: this.props.graph
    });

    return (
      <CollapsibleSection
        label='Graph'
        tooltipText='Graph visualization of path results'
      >
        <GraphAttic
          graphRef={this.graphRef}
          width={this.state.width}
          height={this.state.height}
          setWidth={this.setWidth}
          setHeight={this.setHeight}
          collapseContainer={this.collapseContainer}
          expandContainer={this.expandContainer}
        />
        <Graph
          ref={this.graphRef}
          width={this.state.width}
          height={this.state.height}
          sectionWidth={this.state.sectionWidth}
          setSelectedElement={this.setSelectedElement}
          setHoveredElement={this.setHoveredElement}
          selectedElement={this.state.selectedElement}
          hoveredElement={this.state.hoveredElement}
        />
        <SelectedInfo
          selectedElement={this.state.selectedElement}
          hoveredElement={this.state.hoveredElement}
        />
      </CollapsibleSection>
    );
  }
}

// Connect the component to Redux store to access graph data
// Modify the connect to include memoization
// export default connect((state) => ({
//   graph: state.graph
// }), null, null, {
//   areStatesEqual: (next, prev) => {
//     // Deep comparison of relevant properties
//     return JSON.stringify(next.graph) === JSON.stringify(prev.graph);
//   }
// })
// Single Redux connection export
export default connect(
  (state) => ({
    graph: state.graph || {}
  }),
  null,
  null,
  {
    areStatesEqual: (next, prev) => {
      const nextGraph = next.graph || {};
      const prevGraph = prev.graph || {};
      
      // Compare content instead of references
      return JSON.stringify({
        nodes: nextGraph.nodes,
        relationships: nextGraph.relationships,
        paths: nextGraph.paths
      }) === JSON.stringify({
        nodes: prevGraph.nodes,
        relationships: prevGraph.relationships,
        paths: prevGraph.paths
      });
    }
  }
)(PathGraph);
