// Component to render individual tile with dynamic styling based on its value

import React from 'react';

interface TileProps {
  value: number;
  size?: number;
  style?: React.CSSProperties;
}

const Tile: React.FC<TileProps> = ({ value, size = 80, style = {} }) => {
  // Get tile color based on value
  const getTileStyle = (value: number) => {
    if (value === 0) {
      return {
        backgroundColor: 'rgba(238, 228, 218, 0.35)',
        color: 'transparent',
        border: 'none',
      };
    }

    // Color scheme for different tile values
    const colorMap: { [key: number]: { bg: string; text: string; fontSize: string } } = {
      2: { bg: '#eee4da', text: '#776e65', fontSize: 'text-2xl' },
      4: { bg: '#ede0c8', text: '#776e65', fontSize: 'text-2xl' },
      8: { bg: '#f2b179', text: '#f9f6f2', fontSize: 'text-2xl' },
      16: { bg: '#f59563', text: '#f9f6f2', fontSize: 'text-2xl' },
      32: { bg: '#f67c5f', text: '#f9f6f2', fontSize: 'text-2xl' },
      64: { bg: '#f65e3b', text: '#f9f6f2', fontSize: 'text-2xl' },
      128: { bg: '#edcf72', text: '#f9f6f2', fontSize: 'text-xl' },
      256: { bg: '#edcc61', text: '#f9f6f2', fontSize: 'text-xl' },
      512: { bg: '#edc850', text: '#f9f6f2', fontSize: 'text-xl' },
      1024: { bg: '#edc53f', text: '#f9f6f2', fontSize: 'text-lg' },
      2048: { bg: '#edc22e', text: '#f9f6f2', fontSize: 'text-lg' },
    };

    // For values higher than 2048, use a golden color
    const config = colorMap[value] || { 
      bg: '#3c3a32', 
      text: '#f9f6f2', 
      fontSize: value > 9999 ? 'text-sm' : 'text-lg'
    };

    return {
      backgroundColor: config.bg,
      color: config.text,
      fontSize: config.fontSize,
    };
  };

  const tileStyle = getTileStyle(value);
  
  return (
    <div
      className={`
        flex items-center justify-center rounded-md font-bold
        transition-all duration-150 ease-in-out
        ${tileStyle.fontSize}
        ${value !== 0 ? 'shadow-md' : ''}
      `}
      style={{
        backgroundColor: tileStyle.backgroundColor,
        color: tileStyle.color,
        width: `${size}px`,
        height: `${size}px`,
        minWidth: `${size}px`,
        minHeight: `${size}px`,
        ...style, // Merge in any additional styles from props
      }}
    >
      {value !== 0 && (
        <span className="select-none">
          {value.toLocaleString()}
        </span>
      )}
    </div>
  );
};

export default Tile;
