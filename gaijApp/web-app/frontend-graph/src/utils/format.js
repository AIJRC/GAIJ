import React from 'react';

export function toExponential(value) {
  if (!value || isNaN(value))
    return '-';
  if (typeof value !== 'number')
    return value;

  return parseFloat(value).toExponential(1);
}

export function toComma(value) {
  if (!value || isNaN(value))
    return '-';
  if (typeof value !== 'number')
    return value;

  return value.toLocaleString();
}

export function toGradient(value, stops) {
  // Find applicable gradient stops
  let start = stops[0];
  let end = stops[stops.length - 1];
  
  for (let i = 0; i < stops.length - 1; i++) {
    if (value >= stops[i][0] && value <= stops[i + 1][0]) {
      start = stops[i];
      end = stops[i + 1];
      break;
    }
  }

  // Calculate color
  const percent = (value - start[0]) / (end[0] - start[0]);
  return start[1] + Math.round(percent * 100) + '%';
}