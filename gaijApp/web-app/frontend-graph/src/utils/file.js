// downloads provided data as csv file
// data in format [ [A1, B1] , [A2, B2] ]
export function downloadCsv(data, filename) {
  const fileContent = data.map((cell) => cell.join(',')).join('\n');
  const blob = new Blob(['\ufeff', fileContent], {
    type: 'text/csv;charset=utf-8'
  });
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  document.body.appendChild(link);
  link.href = url;
  link.download = (filename || 'data') + '.csv';
  link.click();
  window.URL.revokeObjectURL(url);
  link.remove();
}

// downloads provided data as svg file
export function downloadSvg(data, filename) {
  const blob = new Blob([data], { type: 'image/svg+xml' });
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  document.body.appendChild(link);
  link.href = url;
  link.download = (filename || 'data') + '.svg';
  link.click();
  window.URL.revokeObjectURL(url);
  link.remove();
}
