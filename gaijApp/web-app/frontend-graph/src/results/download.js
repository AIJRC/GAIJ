import { makeFilenameFriendly, sortCustom, downloadCsv } from '../utils';

// download metapath table
export function download(sourceNode, targetNode, metapaths) {
  if (!metapaths.length || !sourceNode.name || !targetNode.name)
    return;

  const tableData = makeTable(metapaths);
  const filename = [
    'metapaths',
    makeFilenameFriendly(sourceNode.name),
    makeFilenameFriendly(targetNode.name)
  ].join('_');

  downloadCsv(tableData, filename);
}

// make table array out of object
function makeTable(metapaths) {
  let headers = [];
  for (const field of Object.keys(metapaths[0])) {
    if (
      typeof metapaths[0][field] === 'number' ||
      typeof metapaths[0][field] === 'string'
    )
      headers.push(field);
  }

  // remove undesired fields
  headers = headers.filter((header) => header !== 'cypher_query');

  // sort headers in custom order
  const order = [
    'id',
    'metapath_name',
    'metapath_abbreviation',
    'path_count',
    'adjusted_p_value',
    'p_value',
    'dwpc',
    'dgp_source_degree',
    'dgp_target_degree',
    'dgp_n_dwpcs',
    'dgp_n_nonzero_dwpcs',
    'dgp_nonzero_mean',
    'dgp_nonzero_sd'
  ];
  headers = sortCustom(headers, order);

  const table = [];
  table.push(headers);
  for (const result of metapaths) {
    const row = [];
    for (const header of headers)
      row.push(result[header]);
    table.push(row);
  }

  return table;
}
