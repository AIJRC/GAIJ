export function cutString(str, length) {
  if (!str)
    return str;
  if (str.length <= length)
    return str;
  return str.slice(0, length - 1) + '…';
}

export function shortenUrl(url) {
  return url.replace(/^https?:\/\/(www\.)?/, '');
}