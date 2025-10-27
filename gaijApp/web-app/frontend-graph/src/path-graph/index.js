import React from 'react';
import { Component } from 'react';
import ReactDOM from 'react-dom';
import { connect } from 'react-redux';

import { CollapsibleSection } from '../components/collapsible-section.js';
import { GraphAttic } from './attic.js';
import { Graph } from './graph.js';

import { minWidth, minHeight, maxWidth, maxHeight } from './constants.js';

// path graph section component
export class PathGraph extends Component {
  // initialize component
  constructor(props) {
    super(props);

    // Use a more reasonable default width instead of window.innerWidth
    const defaultWidth = 800; // A reasonable starting width for the central pane
    
    this.state = {
      width: defaultWidth,
      height: Math.ceil((defaultWidth * 3) / 4), // Maintain the 3:4 ratio
      sectionWidth: defaultWidth,
      selectedElement: null,
      hoveredElement: null,
      isInitialized: false,
      hasRendered: false,
      isProcessing: false
    };

    this.graphRef = React.createRef();
    this.containerRef = React.createRef(); // Add a ref for the container element
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
          // Call collapseContainer when new graph data arrives
          this.collapseContainer(true);
          
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
      if (this.graphRef.current && 
          !isNaN(this.state.width) && 
          !isNaN(this.state.height) && 
          this.state.width > 0 && 
          this.state.height > 0) {
        this.graphRef.current.fitView();
      }
    }

    // Notify parent component when selected or hovered element changes
    if (this.state.selectedElement !== prevState.selectedElement && this.props.onElementSelect) {
      this.props.onElementSelect(this.state.selectedElement);
    }

    if (this.state.hoveredElement !== prevState.hoveredElement && this.props.onElementHover) {
      this.props.onElementHover(this.state.hoveredElement);
    }
  }

  initializeGraph = () => {
    this.setState({
      isInitialized: true,
      hasRendered: true
    }, () => {
      // Call collapseContainer when the graph is first created
      this.collapseContainer(true);
      
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
    // Ensure width is a valid number
    if (isNaN(width) || width === null || width === undefined) {
      console.warn('Invalid width value:', width);
      return; // Don't update state with invalid values
    }
    
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
    // Ensure height is a valid number
    if (isNaN(height) || height === null || height === undefined) {
      console.warn('Invalid height value:', height);
      return; // Don't update state with invalid values
    }
    
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
    // Use setTimeout to ensure the DOM has been fully rendered
    setTimeout(() => {
      // Find the parent container element (the central pane)
      // First try using our containerRef
      let containerWidth;
      
      if (this.containerRef.current) {
        // Get the closest parent with a width
        let parent = this.containerRef.current;
        while (parent && (!parent.clientWidth || parent.clientWidth <= 0)) {
          parent = parent.parentElement;
        }
        
        if (parent) {
          containerWidth = parent.clientWidth;
        }
      }
      
      // If we couldn't find a width using the ref, try using the document body
      if (!containerWidth || isNaN(containerWidth) || containerWidth <= 0) {
        // Fallback to a percentage of the window width
        containerWidth = Math.max(document.body.clientWidth * 0.6, minWidth);
        console.log('Using fallback container width:', containerWidth);
      } else {
        console.log('Found container width:', containerWidth);
      }
      
      // Adjust width to fit within the container with some padding
      const width = Math.max(containerWidth - 40, minWidth);
      
      this.setWidth(width);
      if (proportionalHeight) {
        const height = Math.ceil((width * 3) / 4);
        this.setHeight(height);
      }
    }, 0);
  };

  // get current width of <section> element
  updateSectionWidth = () => {
    if (this.containerRef.current) {
      this.setState({ sectionWidth: this.containerRef.current.clientWidth });
    }
  };

  // Set selected element and notify parent component
  setSelectedElement = (element) => {
    this.setState({ selectedElement: element });
  };

  // Set hovered element and notify parent component
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
          expandContainer={this.expandContainer}
          collapseContainer={this.collapseContainer}
        />
        <div 
          className="graph-container-wrapper"
          ref={this.containerRef}
        >
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
        </div>
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
