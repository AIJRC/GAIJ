import { compareElements } from './array.js';

// loop through new array of objects. for each object, find object in old
// array that matches all compare keys, and transfer specified keys from
// old object to new
export function transferObjectProps(
  oldArray,
  newArray,
  compareKeys,
  transferKeys
) {
  for (const newElement of newArray) {
    for (const oldElement of oldArray) {
      let matches = true;
      for (const compareKey of compareKeys) {
        if (!compareElements(oldElement[compareKey], newElement[compareKey])) {
          matches = false;
          break;
        }
      }
      if (matches) {
        for (const transferKey of transferKeys)
          newElement[transferKey] = oldElement[transferKey];
      }
    }
  }

  return newArray;
}

// make deep copy of object. ensures everything is clone/copy, not reference.
// works for everything except circular refs, functions, and js Dates
export function copyObject(object) {
  if (typeof object === 'object')
    return JSON.parse(JSON.stringify(object));
  else
    return object;
}

// compare objects with stringify
// works for everything except circular refs, functions, and js Dates
export function compareObjects(object1, object2) {
  // add some quick checks to short-circuit and save some time in certain cases
  if (typeof object1 !== typeof object2)
    return false;
  else if (Array.isArray(object1) && Array.isArray(object2)) {
    if (object1.length !== object2.length)
      return false;
    for (let index = 0; index < object1.length; index++) {
      if (JSON.stringify(object1[index]) !== JSON.stringify(object2[index]))
        return false;
    }
    return true;
  } else
    return JSON.stringify(object1) === JSON.stringify(object2);
    // "brute force"/thorough compare
}
