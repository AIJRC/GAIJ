// reducer for state.sourceNode
// takes whole state as input
export function sourceNode(state = {}, action) {
  switch (action.type) {
    case 'set_source_target_node':
      if (action.payload.sourceNode !== undefined)
        return action.payload.sourceNode || {};
      else
        return state.sourceNode || {};
    case 'swap_source_target_node':
      return state.targetNode || {};
    default:
      return state.sourceNode || {};
  }
}

// reducer for state.targetNode
// takes whole state as input
export function targetNode(state = {}, action) {
  switch (action.type) {
    case 'set_source_target_node':
      if (action.payload.targetNode !== undefined)
        return action.payload.targetNode || {};
      else
        return state.targetNode || {};
    case 'swap_source_target_node':
      return state.sourceNode || {};
    default:
      return state.targetNode || {};
  }
}
