import { makeFilenameFriendly, sortCustom, downloadCsv } from '../utils';

// download path table
export function download(sourceNode, targetNode, paths) {
  if (!paths.length || !sourceNode.name || !targetNode.name)
    return;

  const tableData = makeTable(paths);
  const filename = [
    'paths',
    makeFilenameFriendly(sourceNode.name),
    makeFilenameFriendly(targetNode.name)
  ].join('_');

  downloadCsv(tableData, filename);
}

// make table array out of object
function makeTable(paths) {
  let headers = [];
  for (const field of Object.keys(paths[0])) {
    if (
      typeof paths[0][field] === 'number' ||
      typeof paths[0][field] === 'string'
    )
      headers.push(field);
  }

  // sort headers in custom order
  const order = ['description', 'metapath', 'score', 'percent_of_DWPC'];
  headers = sortCustom(headers, order);

  const table = [];
  table.push(headers);
  for (const result of paths) {
    const row = [];
    for (const header of headers)
      row.push(result[header]);
    table.push(row);
  }

  return table;
}
