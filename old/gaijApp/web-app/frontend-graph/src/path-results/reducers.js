// import { assemblePath } from './assemble.js';
// import { textDescription } from './assemble.js';
// import { transferObjectProps } from '../utils/object';

// reducer for state.paths
export function paths(state = [], action) {
  switch (action.type) {
    case 'set_paths':
      // Ensure we have valid data structure
      if (!action.payload || !action.payload.paths) {
        return [];
      }
      return action.payload.paths || [];
    default:
      return state;
  }
}

// reducer for state.nodes
export function nodes(state = {}, action) {
  switch (action.type) {
    case 'set_paths':
      // Ensure we have valid nodes data
      if (!action.payload || !action.payload.nodes) {
        return {};
      }
      return { ...state, ...(action.payload.nodes || {}) };
    default:
      return state;
  }
}

// reducer for state.relationships
export function relationships(state = {}, action) {
  switch (action.type) {
    case 'set_paths':
      // Ensure we have valid relationships data
      if (!action.payload || !action.payload.relationships) {
        return {};
      }
      return { ...state, ...(action.payload.relationships || {}) };
    default:
      return state;
  }
}
