import React from "react";
import { connect } from "react-redux";
import SelectionPanel from '../components/SelectionPanel';
import "./Explore.css"; // Import CSS

import { NodeSearch } from "../node-search";
import { NodeResults } from "../node-results";
import { PathGraph } from "../path-graph";

const Explore = ({ sourceNode, isPathsLoading }) => {
  const shouldRenderResults = sourceNode?.id && !isPathsLoading;

   const handleSelectionsSubmit = (selections) => {
    console.log('User selections:', selections);
    // Here you can:
    // 1. Dispatch Redux actions with the selections
    // 2. Pass selections to your graph components
    // 3. Filter/process your data based on selections
  };

  return (
    <div className="explore-container">
      {/* Top Panel - Search and Results */}
      <div className="explore-top-panel">
        <NodeSearch />
        {shouldRenderResults && <NodeResults />}
      </div>

    {/* Bottom Section */}
    <div className="explore-bottom-section">
        {/* Left Panel - Selection Panel */}
        <div className="explore-left-panel">
          <SelectionPanel onSubmit={handleSelectionsSubmit} />
        </div>

        {/* Right Panel - Graph */}
        <div className="explore-right-panel">
          <PathGraph />
        </div>
      </div>
    </div>
  );
};


// Connect to Redux state
const mapStateToProps = (state) => ({
  sourceNode: state.sourceNode,
  isPathsLoading: state.isPathsLoading,
});

export default connect(mapStateToProps)(Explore);

