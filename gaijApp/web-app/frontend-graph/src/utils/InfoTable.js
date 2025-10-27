import React from 'react';
import './InfoTable.css';

export const InfoTable = ({ className = '', bodyContents = [] }) => {
  return (
    <table className={`info_table ${className}`}>
      <tbody>
        {bodyContents.map(([label, tooltip, value], index) => (
          <tr key={index}>
            <td className='first_col'>{label}</td>
            <td className='second_col'>{value}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
};