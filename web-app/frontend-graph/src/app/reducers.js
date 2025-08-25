// reducer for state.metagraph
export function metagraph(state = {}, action) {
  switch (action.type) {
    case 'set_definitions':
      return action.payload.metagraph || {};
    default:
      return state;
  }
}

// reducer for state.gaijStyles
export function gaijStyles(state = {}, action) {
  switch (action.type) {
    case 'set_definitions':
      return action.payload.gaijStyles || {};
    default:
      return state;
  }
}

// reducer for state.tooltipDefinitions
export function tooltipDefinitions(state = {}, action) {
  switch (action.type) {
    case 'set_definitions':
      return action.payload.tooltipDefinitions || {};
    default:
      return state;
  }
}
