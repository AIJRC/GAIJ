import { getConnectivitySearchDefinitions, lookupNode } from '../backend-queries.js';
import { setSourceTargetNode } from '../node-search/actions.js';
import { setPrecomputedMetapathsOnly } from '../metapath-results/actions.js';
import { fetchAndSetMetapaths } from '../metapath-results/actions.js';

// fetch and set definitions
export function fetchAndSetDefinitions() {
  return async function(dispatch) {
    const definitions = getConnectivitySearchDefinitions();
    dispatch({
      type: 'set_tooltip_definitions',
      payload: definitions
    });
  };
}

// load state from url parameters
export function loadStateFromUrl() {
  return async function(dispatch) {
    const params = new URLSearchParams(window.location.search);
    const sourceId = params.get('source');
    const targetId = params.get('target');
    const complete = params.get('complete') === '' ? true : false;

    if (sourceId || targetId) {
      const sourceNode = sourceId ? await lookupNode(sourceId) : {};
      const targetNode = targetId ? await lookupNode(targetId) : {};
      
      // Set source and target nodes
      dispatch(setSourceTargetNode({
        sourceNode: sourceNode,
        targetNode: targetNode,
        updateUrl: false
      }));

      // Set precomputed metapaths option
      dispatch(
        setPrecomputedMetapathsOnly({
          precomputedMetapathsOnly: !complete,
          updateUrl: false
        })
      );

      // Fetch and set metapaths if both nodes are selected
      if (sourceId && targetId) {
        dispatch(
          fetchAndSetMetapaths({
            sourceNodeId: sourceId,
            targetNodeId: targetId,
            updateUrl: false
          })
        );
      }
    }
  };
}