export const sortCustom = (items, order) => {
  return [...items].sort((a, b) => {
    const indexA = order.indexOf(a);
    const indexB = order.indexOf(b);
    return indexA - indexB;
  });
};

export const downloadSvg = (data, filename) => {
  const blob = new Blob([data], { type: 'image/svg+xml' });
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  document.body.appendChild(link);
  link.href = url;
  link.download = (filename || 'data') + '.svg';
  link.click();
  window.URL.revokeObjectURL(url);
  link.remove();
};

export const downloadCsv = (data, filename) => {
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
};

export const makeFilenameFriendly = (str) => {
  return str.replace(/[^a-z0-9]/gi, '_')
            .replace(/_{2,}/g, '_')
            .replace(/^_|_$/g, '')
            .toLowerCase();
};