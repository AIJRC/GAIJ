import React, { useState } from "react";
import { connect } from "react-redux";
import SelectionPanel from '../components/SelectionPanel';
import FilterPanel from '../node-search/filters';
import "./Explore.css"; // Import CSS

import { NodeSearch } from "../node-search";
import Statistics from "../node-search/statistics";
import { NodeResults } from "../node-results";
import { PathGraph } from "../path-graph";
import { SelectedInfo } from "../path-graph/selected-info.js"; // Import SelectedInfo component

const Explore = ({ sourceNode, isPathsLoading }) => {
  const shouldRenderResults = sourceNode?.id && !isPathsLoading;

  // State to track selected and hovered elements from the graph
  const [selectedElement, setSelectedElement] = useState(null);
  const [hoveredElement, setHoveredElement] = useState(null);
  // State to track sidebar visibility
  const [leftSidebarVisible, setLeftSidebarVisible] = useState(true);
  const [rightSidebarVisible, setRightSidebarVisible] = useState(true);
  const [topBarVisible, setTopBarVisible] = useState(true);

  const handleSelectionsSubmit = (selections) => {
    console.log('User selections:', selections);
  };

  const handleFiltersSubmit = (select_filters) => {
    console.log('User filters:', select_filters);
  };

  // Toggle left sidebar visibility
  const toggleLeftSidebar = () => {
    setLeftSidebarVisible(!leftSidebarVisible);
  };

  // Toggle right sidebar visibility
  const toggleRightSidebar = () => {
    setRightSidebarVisible(!rightSidebarVisible);
  };

  // Toggle top bar visibility
  const toggletopBar = () => {
    setTopBarVisible(!topBarVisible);
  };

  return (
    <div className="explore-container">
      {/* Main three-panel layout */}
      <div className="explore-layout">
        
        {/* Left Sidebar - Filtering Options */}
        <div className={`explore-left-sidebar ${leftSidebarVisible ? '' : 'hidden'}`}>
          {/*<SelectionPanel onSubmit={handleSelectionsSubmit} /> */}
          <NodeSearch onSubmit={handleSelectionsSubmit} />
        </div>

        {/* Toggle Button for Left Sidebar */}
        <button
          className="sidebar-toggle-btn left-sidebar-toggle"
          onClick={toggleLeftSidebar}
          title={leftSidebarVisible ? "Hide Filters" : "Show Filters"}
        >
          {leftSidebarVisible ? '◀' : '▶'}
        </button>

        {/* Central Pane - Graph and Search */}
        <div className="explore-search-section">
          {/*<NodeSearch />*/}
          <Statistics/>
          <div className={`explore-top-bar ${topBarVisible ? '' : 'hidden'}`}>
            <FilterPanel onSubmit={handleFiltersSubmit} />
          </div>
          <button
            className="topbar-toggle-btn"
            onClick={toggletopBar}
            title={topBarVisible ? "Hide Top Filters" : "Show Top Filters"}
          >
            {topBarVisible ? '▲' : '▼'}
          </button>



          {/* Graph Section */}
          <div className="explore-graph-section">
            <PathGraph
              onElementSelect={setSelectedElement}
              onElementHover={setHoveredElement}
            />
          </div>
        </div>
      </div>

      {/* Right Sidebar - Node Information */}
      <div className={`explore-right-sidebar ${rightSidebarVisible ? '' : 'hidden'}`}>
        {shouldRenderResults && <NodeResults />}
        <div className="graph-info-wrapper">
          <SelectedInfo
            selectedElement={selectedElement}
            hoveredElement={hoveredElement}
          />
        </div>
      </div>

      {/* Toggle Button for Right Sidebar */}
      <button
        className="sidebar-toggle-btn right-sidebar-toggle"
        onClick={toggleRightSidebar}
        title={rightSidebarVisible ? "Hide Info Panel" : "Show Info Panel"}
      >
        {rightSidebarVisible ? '▶' : '◀'}
      </button>
    </div>
  );
};

// Connect to Redux state
const mapStateToProps = (state) => ({
  sourceNode: state.sourceNode,
  isPathsLoading: state.isPathsLoading,
});

export default connect(mapStateToProps)(Explore);
