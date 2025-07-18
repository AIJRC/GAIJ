import { fetchGraphData } from '../backend-queries.js';

// set metapaths
export function setMetapaths({ metapaths, updateUrl }) {
  return async function(dispatch) {
    if (updateUrl) {
      const params = new URLSearchParams(window.location.search);
      const checkedMetapaths = metapaths
        .filter((metapath) => metapath.checked)
        .map((metapath) => metapath.metapath_abbreviation)
        .join(',');
      if (checkedMetapaths)
        params.set('metapaths', checkedMetapaths);
      else
        params.delete('metapaths');
      window.history.pushState(null, '', '?' + params.toString());
    }

    dispatch({
      type: 'set_metapaths',
      payload: metapaths
    });
  };
}

// set precomputed metapaths only
export function setPrecomputedMetapathsOnly({
  precomputedMetapathsOnly,
  updateUrl
}) {
  return async function(dispatch) {
    if (updateUrl) {
      const params = new URLSearchParams(window.location.search);
      if (!precomputedMetapathsOnly)
        params.set('complete', '');
      else
        params.delete('complete');
      window.history.pushState(null, '', '?' + params.toString());
    }

    dispatch({
      type: 'set_precomputed_metapaths_only',
      payload: precomputedMetapathsOnly
    });
  };
}

// Add this new action creator
export function togglePrecomputedMetapathsOnly() {
  return function(dispatch, getState) {
    const state = getState();
    dispatch(
      setPrecomputedMetapathsOnly({
        precomputedMetapathsOnly: !state.precomputedMetapathsOnly,
        updateUrl: true
      })
    );
  };
}

// fetch and set paths between nodes
export function fetchAndSetMetapaths({ sourceNodeId, targetNodeId, updateUrl }) {
  return async function(dispatch) {
    try {
      const graphData = await fetchGraphData(sourceNodeId, targetNodeId);
      
      // Transform graph data into metapaths format
      const metapaths = [{
        metapath: 'default',
        checked: true,
        paths: graphData.edges.map(edge => ({
          type: edge.kind,
          source: edge.source_neo4j_id,
          target: edge.target_neo4j_id
        }))
      }];

      dispatch(setMetapaths({ metapaths, updateUrl }));
    } catch (error) {
      console.error('Error fetching paths:', error);
      dispatch(setMetapaths({ metapaths: [], updateUrl }));
    }
  };
}