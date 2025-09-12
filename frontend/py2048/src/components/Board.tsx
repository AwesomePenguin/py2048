// Component to render the game board and handle user interactions

import React from 'react';
import Tile from './Tile';

interface BoardProps {
  board: number[][];
  loading?: boolean;
  onMove?: (direction: 'up' | 'down' | 'left' | 'right') => void;
}

const Board: React.FC<BoardProps> = ({ board, loading = false, onMove }) => {
  const boardRows = board.length;
  const boardCols = board[0]?.length || 0;
  
  // Handle touch/swipe gestures for mobile
  const [touchStart, setTouchStart] = React.useState<{ x: number; y: number } | null>(null);
  const [touchEnd, setTouchEnd] = React.useState<{ x: number; y: number } | null>(null);

  const handleTouchStart = (e: React.TouchEvent) => {
    setTouchEnd(null);
    setTouchStart({
      x: e.targetTouches[0].clientX,
      y: e.targetTouches[0].clientY,
    });
  };

  const handleTouchMove = (e: React.TouchEvent) => {
    setTouchEnd({
      x: e.targetTouches[0].clientX,
      y: e.targetTouches[0].clientY,
    });
  };

  const handleTouchEnd = () => {
    if (!touchStart || !touchEnd || !onMove || loading) return;

    const distanceX = touchStart.x - touchEnd.x;
    const distanceY = touchStart.y - touchEnd.y;
    const isLeftSwipe = distanceX > 5;
    const isRightSwipe = distanceX < -5;
    const isUpSwipe = distanceY > 5;
    const isDownSwipe = distanceY < -5;

    // Determine the dominant direction
    if (Math.abs(distanceX) > Math.abs(distanceY)) {
      // Horizontal swipe
      if (isLeftSwipe) {
        onMove('left');
      } else if (isRightSwipe) {
        onMove('right');
      }
    } else {
      // Vertical swipe
      if (isUpSwipe) {
        onMove('up');
      } else if (isDownSwipe) {
        onMove('down');
      }
    }
  };

  // Dynamic grid sizing based on board dimensions
  const getGridSize = () => {
    if (typeof window !== 'undefined') {
      const baseSize = Math.min(400, window.innerWidth * 0.8);
      return Math.min(baseSize, 500);
    }
    return 400; // Default for server-side rendering
  };

  const gridSize = getGridSize();
  const cellSize = Math.min(90, (gridSize - 60) / Math.max(boardRows, boardCols));

  const gridClass = `grid gap-2 p-4 bg-gray-300 rounded-lg relative`;
  
  return (
    <div className="flex justify-center">
      <div 
        className={gridClass}
        style={{ 
          gridTemplateColumns: `repeat(${boardCols}, minmax(0, 1fr))`,
          gridTemplateRows: `repeat(${boardRows}, minmax(0, 1fr))`,
          width: `${gridSize}px`,
          height: `${gridSize * (boardRows / boardCols)}px`,
        }}
        onTouchStart={handleTouchStart}
        onTouchMove={handleTouchMove}
        onTouchEnd={handleTouchEnd}
      >
        {/* Loading overlay */}
        {loading && (
          <div className="absolute inset-0 bg-white bg-opacity-50 flex items-center justify-center rounded-lg z-10">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          </div>
        )}
        
        {/* Render tiles with explicit grid positioning */}
        {board.map((row, rowIndex) => 
          row.map((value, colIndex) => (
            <Tile 
              key={`${rowIndex}-${colIndex}`} 
              value={value}
              size={cellSize}
              style={{
                gridRow: rowIndex + 1,
                gridColumn: colIndex + 1
              }}
            />
          ))
        )}
      </div>
    </div>
  );
};

export default Board;
