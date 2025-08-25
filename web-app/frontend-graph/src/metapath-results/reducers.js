import { transferObjectProps } from '../utils/object';

// reducer for state.metapaths
export function metapaths(state = [], action) {
  switch (action.type) {
    case 'set_metapaths':
      let metapaths = action.payload.metapaths;

      // transfer checkbox states from previous to next
      if (action.payload.preserveChecks) {
        metapaths = transferObjectProps(
          state,
          action.payload.metapaths,
          ['metapath_id'],
          ['checked']
        );
      }
      return metapaths || [];

    // any time a new path is fetched from a query, fill in the returned
    // metapath data into the corresponding metapath in case it is missing
    // (not precomputed)
    case 'set_paths':
      const newMetapaths = state;

      if (!action.payload || !action.payload.pathCountInfo)
        return newMetapaths || [];

      const pathCountInfo = action.payload.pathCountInfo;

      for (const key of Object.keys(pathCountInfo)) {
        const index = newMetapaths.findIndex(
          (metapath) => metapath.metapath_abbreviation === key
        );
        newMetapaths[index] = {
          ...newMetapaths[index],
          ...pathCountInfo[key]
        };
      }
      return newMetapaths || [];

    default:
      return state;
  }
}

// reducer for state.precomputedMetapathsOnly
export function precomputedMetapathsOnly(state = true, action) {
  switch (action.type) {
    case 'toggle_precomputed_metapaths_only':
      return !state;
    case 'set_precomputed_metapaths_only':
      let precomputedMetapathsOnly = action.payload.precomputedMetapathsOnly;
      if (typeof precomputedMetapathsOnly !== 'boolean')
        precomputedMetapathsOnly = true;
      return precomputedMetapathsOnly;
    default:
      return state;
  }
}
