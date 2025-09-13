// Component to render the game board and handle user interactions

import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import Tile from './Tile';

interface BoardProps {
  board: number[][];
  loading?: boolean;
  onMove?: (direction: 'up' | 'down' | 'left' | 'right') => void;
}

type Direction = 'up' | 'down' | 'left' | 'right' | null;

const Board: React.FC<BoardProps> = ({ board, loading = false, onMove }) => {
  const boardRows = board.length;
  const boardCols = board[0]?.length || 0;
  
  // Handle touch/swipe gestures for mobile
  const [touchStart, setTouchStart] = React.useState<{ x: number; y: number } | null>(null);
  const [touchEnd, setTouchEnd] = React.useState<{ x: number; y: number } | null>(null);
  const [previousBoard, setPreviousBoard] = React.useState<number[][]>(board);
  const [isMoving, setIsMoving] = React.useState(false);
  const [lastMoveDirection, setLastMoveDirection] = React.useState<Direction>(null);
  const [animationKey, setAnimationKey] = React.useState(0);
  const boardRef = React.useRef<HTMLDivElement>(null);

  // Update previous board state for animation tracking
  React.useEffect(() => {
    if (JSON.stringify(previousBoard) !== JSON.stringify(board)) {
      setIsMoving(true);
      setAnimationKey(prev => prev + 1); // Force re-render of animations
      const timer = setTimeout(() => setIsMoving(false), 300); // Increased duration
      setPreviousBoard(board);
      return () => clearTimeout(timer);
    }
  }, [board, previousBoard]);

  // Enhanced move handler that tracks direction
  const handleMove = React.useCallback((direction: Direction) => {
    if (!onMove || loading || isMoving) return;
    setLastMoveDirection(direction);
    if (direction) {
      onMove(direction);
    }
  }, [onMove, loading, isMoving]);

  const handleTouchStart = (e: React.TouchEvent) => {
    // Prevent default browser behavior that might interfere
    e.preventDefault();
    e.stopPropagation();
    setTouchEnd(null);
    setTouchStart({
      x: e.targetTouches[0].clientX,
      y: e.targetTouches[0].clientY,
    });
  };

  const handleTouchMove = (e: React.TouchEvent) => {
    // Prevent scrolling and other browser gestures
    e.preventDefault();
    e.stopPropagation();
    if (e.targetTouches.length > 0) {
      setTouchEnd({
        x: e.targetTouches[0].clientX,
        y: e.targetTouches[0].clientY,
      });
    }
  };

  const handleTouchEnd = (e: React.TouchEvent) => {
    // Prevent default to avoid triggering clicks or other gestures
    e.preventDefault();
    e.stopPropagation();
    
    if (!touchStart || !touchEnd || !onMove || loading || isMoving) return;

    const distanceX = touchStart.x - touchEnd.x;
    const distanceY = touchStart.y - touchEnd.y;
    const minSwipeDistance = 30; // Increased minimum distance to avoid accidental swipes
    const totalDistance = Math.sqrt(distanceX * distanceX + distanceY * distanceY);
    
    // Require minimum total distance for any swipe
    if (totalDistance < minSwipeDistance) return;
    
    const isLeftSwipe = distanceX > minSwipeDistance;
    const isRightSwipe = distanceX < -minSwipeDistance;
    const isUpSwipe = distanceY > minSwipeDistance;
    const isDownSwipe = distanceY < -minSwipeDistance;

    // Determine the dominant direction with better threshold
    if (Math.abs(distanceX) > Math.abs(distanceY)) {
      // Horizontal swipe
      if (isLeftSwipe) {
        handleMove('left');
      } else if (isRightSwipe) {
        handleMove('right');
      }
    } else {
      // Vertical swipe
      if (isUpSwipe) {
        handleMove('up');
      } else if (isDownSwipe) {
        handleMove('down');
      }
    }
    
    // Clear touch state
    setTouchStart(null);
    setTouchEnd(null);
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

  const gridClass = `grid gap-2 p-4 bg-gray-300 rounded-lg relative overflow-hidden game-board no-select`;
  
  // Animation configuration based on move direction
  const getDirectionalAnimations = (direction: Direction) => {
    const distance = Math.max(cellSize, 100); // Distance to animate
    
    const animations = {
      exit: { x: 0, y: 0, opacity: 0, scale: 0.9 },
      enter: { x: 0, y: 0, opacity: 0.7, scale: 0.9 }
    };

    switch (direction) {
      case 'left':
        animations.exit = { x: -distance, y: 0, opacity: 0, scale: 0.9 };
        animations.enter = { x: distance, y: 0, opacity: 0.7, scale: 0.9 };
        break;
      case 'right':
        animations.exit = { x: distance, y: 0, opacity: 0, scale: 0.9 };
        animations.enter = { x: -distance, y: 0, opacity: 0.7, scale: 0.9 };
        break;
      case 'up':
        animations.exit = { x: 0, y: -distance, opacity: 0, scale: 0.9 };
        animations.enter = { x: 0, y: distance, opacity: 0.7, scale: 0.9 };
        break;
      case 'down':
        animations.exit = { x: 0, y: distance, opacity: 0, scale: 0.9 };
        animations.enter = { x: 0, y: -distance, opacity: 0.7, scale: 0.9 };
        break;
      default:
        // No direction - use scale-based animations
        break;
    }

    return animations;
  };

  const directionAnimations = getDirectionalAnimations(lastMoveDirection);

  return (
    <div className="flex justify-center">
      <motion.div 
        ref={boardRef}
        className={gridClass}
        style={{ 
          gridTemplateColumns: `repeat(${boardCols}, minmax(0, 1fr))`,
          gridTemplateRows: `repeat(${boardRows}, minmax(0, 1fr))`,
          width: `${gridSize}px`,
          height: `${gridSize * (boardRows / boardCols)}px`,
          touchAction: 'none', // Prevent all browser touch gestures
          userSelect: 'none', // Prevent text selection
          WebkitUserSelect: 'none',
          WebkitTouchCallout: 'none',
          WebkitTapHighlightColor: 'transparent',
        }}
        onTouchStart={handleTouchStart}
        onTouchMove={handleTouchMove}
        onTouchEnd={handleTouchEnd}
        // Prevent context menu on long press
        onContextMenu={(e) => e.preventDefault()}
        // Additional event handlers to ensure proper touch handling
        onTouchCancel={(e) => {
          e.preventDefault();
          setTouchStart(null);
          setTouchEnd(null);
        }}
      >
        {/* Loading overlay */}
        {loading && (
          <motion.div 
            className="absolute inset-0 bg-white bg-opacity-50 flex items-center justify-center rounded-lg z-10"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          </motion.div>
        )}
        
        {/* Render tiles with directional animations */}
        <AnimatePresence mode="wait">
          {board.map((row, rowIndex) => 
            row.map((value, colIndex) => {
              // Create a unique key that includes animation key for re-mounting
              const key = `tile-${rowIndex}-${colIndex}-${value}-${animationKey}`;
              const isNew = previousBoard && 
                (previousBoard[rowIndex]?.[colIndex] !== value && value !== 0);
              const isEmpty = value === 0;
              
              return (
                <motion.div
                  key={key}
                  layout={!isMoving} // Disable layout animation during moves
                  initial={
                    isEmpty ? { scale: 1, opacity: 1 } :
                    isMoving && lastMoveDirection ? directionAnimations.enter :
                    { scale: 0.8, opacity: 0.8 }
                  }
                  animate={{ 
                    scale: 1, 
                    opacity: isEmpty ? 1 : 1,
                    x: 0,
                    y: 0
                  }}
                  exit={
                    isEmpty ? { scale: 1, opacity: 1 } :
                    isMoving && lastMoveDirection ? directionAnimations.exit :
                    { scale: 0.8, opacity: 0 }
                  }
                  transition={{
                    layout: {
                      type: "spring",
                      stiffness: 400,
                      damping: 30,
                      duration: 0.2
                    },
                    default: {
                      type: "spring",
                      stiffness: 300,
                      damping: 25,
                      duration: isMoving ? 0.25 : 0.15
                    },
                    // Stagger entrance animations slightly
                    delay: isMoving && !isEmpty ? (rowIndex + colIndex) * 0.02 : 0
                  }}
                  style={{
                    gridRow: rowIndex + 1,
                    gridColumn: colIndex + 1,
                    zIndex: value !== 0 ? 2 : 1
                  }}
                  whileHover={value !== 0 && !isMoving ? { 
                    scale: 1.02,
                    transition: { duration: 0.1 }
                  } : undefined}
                  whileTap={value !== 0 ? { 
                    scale: 0.98,
                    transition: { duration: 0.05 }
                  } : undefined}
                >
                  <Tile 
                    value={value}
                    size={cellSize}
                    isNew={isNew && !isMoving}
                    isMerged={false} // We could enhance this by tracking merges
                  />
                </motion.div>
              );
            })
          )}
        </AnimatePresence>
      </motion.div>
    </div>
  );
};

export default Board;
