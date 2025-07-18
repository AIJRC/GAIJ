import { metagraph } from './app/reducers.js';
import { gaijStyles } from './app/reducers.js';
import { tooltipDefinitions } from './app/reducers.js';
import { copyObject } from './utils/object';
import { cutString } from './utils/string';

import { sourceNode } from './node-search/reducers.js';
import { targetNode } from './node-search/reducers.js';

import { metapaths } from './metapath-results/reducers.js';
import { precomputedMetapathsOnly } from './metapath-results/reducers.js';

import { paths } from './path-results/reducers.js';
import { nodes } from './path-results/reducers.js';
import { relationships } from './path-results/reducers.js';

import { graph } from './path-graph/reducers.js';
import { showGrid } from './path-graph/reducers.js';

// master combined reducer
export function Reducer(state = {}, action) {
  // make deep copy of old state into new state
  let newState = copyObject(state);
  // only shallow copy graph though, because d3 attaches internal variables
  // directly to the data structure, and the simulation will get messed up
  // if we deep copy and replace the data completely
  delete newState.graph;
  newState.graph = state.graph;

  // assemble new state from individual reducers
  newState = {
    metagraph: metagraph(newState.metagraph, action),
    gaijStyles: gaijStyles(newState.gaijStyles, action),
    tooltipDefinitions: tooltipDefinitions(newState.tooltipDefinitions, action),
    sourceNode: sourceNode(newState, action),
    targetNode: targetNode(newState, action),
    metapaths: metapaths(newState.metapaths, action),
    precomputedMetapathsOnly: precomputedMetapathsOnly(
      newState.precomputedMetapathsOnly,
      action
    ),
    paths: paths(newState, action),
    nodes: nodes(newState.nodes, action),
    relationships: relationships(newState.relationships, action),
    graph: graph(newState, action),
    showGrid: showGrid(newState.showGrid, action)
  };

  // if explicitly specified, update url to match state
  if (action.payload && action.payload.updateUrl === true)
    updateUrl(newState);

  // update document/tab title based on state
  updateTitle(newState);

  return newState;
}

// update url to reflect current state
function updateUrl(state) {
  // get checked metapaths
  const checkedMetapaths = [];
  for (const metapath of state.metapaths) {
    if (metapath.checked)
      checkedMetapaths.push(metapath.metapath_abbreviation);
  }

  // sort to keep order predictable
  checkedMetapaths.sort();

  // new url
  const newParams = new URLSearchParams();

  // set url parameters
  if (state.sourceNode.id !== undefined)
    newParams.set('source', state.sourceNode.id);
  if (state.targetNode.id !== undefined)
    newParams.set('target', state.targetNode.id);
  if (checkedMetapaths.length > 0)
    newParams.set('metapaths', checkedMetapaths.join(','));
  if (!state.precomputedMetapathsOnly)
    newParams.set('complete', '');

  // make search string
  let search = newParams.toString();
  if (search.length > 0)
    search = '?' + search;

  // if url already matches state, dont push another history entry
  if (search === window.location.search)
    return;

  // navigate to new url
  const url = window.location.origin + window.location.pathname + search;
  window.history.pushState({}, '', url);
}

// update document title to reflect state
function updateTitle(state) {
  const checkedMetapaths = state.metapaths.filter(
    (metapath) => metapath.checked
  );
  document.title =
    cutString(state.sourceNode.name || '___', 20) +
    ' ↔ ' +
    cutString(state.targetNode.name || '___', 20) +
    ' – ' +
    checkedMetapaths.length +
    ' metapaths';
}
