import React from "react";
import { connect } from "react-redux";
import "./Explore.css"; // Import CSS

import { NodeSearch } from "../node-search";
import { NodeResults } from "../node-results";
import { PathGraph } from "../path-graph";

const Explore = ({ sourceNode, isPathsLoading }) => {
  const shouldRenderResults = sourceNode?.id && !isPathsLoading;

  return (
    <div className="explore-container">
      <NodeSearch />
      {shouldRenderResults && <NodeResults />}
      <PathGraph />
    </div>
  );
};

// Connect to Redux state
const mapStateToProps = (state) => ({
  sourceNode: state.sourceNode,
  isPathsLoading: state.isPathsLoading,
});

export default connect(mapStateToProps)(Explore);
