// toggle showGrid action
export function toggleShowGrid() {
  return {
    type: 'toggle_show_grid'
  };
}

// set paths action
export function setPaths(payload) {
  console.log('INSIDE SETPATHS', payload)
  return {
    type: 'set_paths',
    payload: payload
  };
}


// Relationship filters action 
export const setRelationshipFilters = (filters) => ({
  type: 'SET_RELATIONSHIP_FILTERS',
  payload: filters
});
