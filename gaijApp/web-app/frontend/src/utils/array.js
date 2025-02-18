// sort array in custom order
export function sortCustom(array, order, key) {
  return array.sort((a, b) => {
    if (key) {
      a = a[key];
      b = b[key];
    }

    a = order.indexOf(a);
    b = order.indexOf(b);

    if (a !== -1 && b !== -1)
      return a - b;
    else if (a !== -1)
      return -1;
    else if (b !== -1)
      return 1;
    else
      return b - a;
  });
}

// compare two elements as primitives (eg number === number or string ===
// string) or as arrays if both are arrays
export function compareElements(element1, element2) {
  if (Array.isArray(element1) && Array.isArray(element2))
    return compareArrays(element1, element2, true);
  else
    return element1 === element2;
}

// checks if arrays of primitives (strings, numbers, etc) are equal.
// if specified, also check if arrays are equal in reverse
export function compareArrays(array1, array2, checkReverse) {
  if (array1.length !== array2.length)
    return false;

  if (!checkReverse) {
    // check forwards
    return array1.every((element, index) => element === array2[index]);
  } else {
    // check forwards and backwards
    return (
      array1.every((element, index) => element === array2[index]) ||
      array1
        .slice()
        .reverse()
        .every((element, index) => element === array2[index])
    );
  }
}
