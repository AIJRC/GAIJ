// truncate string to character limit, insert ellipsis  if necessary
export function cutString(string, n) {
  if (typeof string !== 'string')
    return '-';
  if (string.length <= n)
    return string;
  else
    return string.substring(0, n - 3) + '...';
}

// remove unnecessary preceding "www." and etc from url
export function shortenUrl(url) {
  const regexes = ['^http://', '^https://', '^www.'];
  for (const regex of regexes)
    url = url.replace(new RegExp(regex), '');

  return url;
}

// make OS-friendly filename
export function makeFilenameFriendly(string) {
  if (typeof string !== 'string')
    return '-';
  // remove leading and trailing whitespace
  string = string.trim();
  // replace special characters with dashes
  string = string.replace(/[^0-9A-Za-z]/gi, '-');
  // shorten if too long
  string = string.substring(0, 15);
  return string;
}
