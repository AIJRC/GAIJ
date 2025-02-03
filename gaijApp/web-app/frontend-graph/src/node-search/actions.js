import { searchNodes } from '../backend-queries.js';

// set source/target node
export function setSourceTargetNode({ sourceNode, targetNode, updateUrl }) {
  return async function(dispatch) {
    if (updateUrl) {
      const params = new URLSearchParams(window.location.search);
      if (sourceNode && sourceNode.id)
        params.set('source', sourceNode.id);
      else
        params.delete('source');
      if (targetNode && targetNode.id)
        params.set('target', targetNode.id);
      else
        params.delete('target');
      window.history.pushState(null, '', '?' + params.toString());
    }

    dispatch({
      type: 'set_source_target_node',
      payload: {
        sourceNode: sourceNode || {},
        targetNode: targetNode || {}
      }
    });
  };
}

// search for nodes
export function searchAndSetNodes({ searchString, otherNodeId, metanodes }) {
  return async function(dispatch) {
    const results = await searchNodes(searchString, otherNodeId, metanodes);
    dispatch({
      type: 'set_node_search_results',
      payload: results
    });
  };
}

// Add this new action creator
export function swapSourceTargetNode() {
  return async function(dispatch, getState) {
    const state = getState();
    dispatch(
      setSourceTargetNode({
        sourceNode: state.targetNode,
        targetNode: state.sourceNode,
        updateUrl: true
      })
    );
  };
}
