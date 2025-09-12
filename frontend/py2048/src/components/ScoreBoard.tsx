import React from 'react';

interface ScoreBoardProps {
  score: number;
  highScore: number;
  moves: number;
  streakCount: number;
  hintsRemaining: number;
  canRedo: boolean;
  lastMoveScore: number;
  gameMessage?: string;
}

const ScoreBoard: React.FC<ScoreBoardProps> = ({
  score,
  highScore,
  moves,
  streakCount,
  hintsRemaining,
  canRedo,
  lastMoveScore,
  gameMessage
}) => {
  return (
    <div className="bg-white rounded-lg shadow-lg p-4 mb-6">
      {/* Main Stats Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
        <div>
          <p className="text-sm text-gray-600">Score</p>
          <p className="text-xl font-bold">{score.toLocaleString()}</p>
        </div>
        <div>
          <p className="text-sm text-gray-600">Best</p>
          <p className="text-xl font-bold">{highScore.toLocaleString()}</p>
        </div>
        <div>
          <p className="text-sm text-gray-600">Moves</p>
          <p className="text-xl font-bold">{moves}</p>
        </div>
        <div>
          <p className="text-sm text-gray-600">Streak</p>
          <p className="text-xl font-bold">{streakCount}</p>
        </div>
      </div>
      
      {/* Secondary Stats Grid */}
      <div className="grid grid-cols-2 gap-4 mt-4 text-center">
        <div>
          <p className="text-xs text-gray-500">Hints Remaining</p>
          <p className="text-lg font-medium text-blue-600">{hintsRemaining}</p>
        </div>
        <div>
          <p className="text-xs text-gray-500">Undo Available</p>
          <p className="text-lg font-medium text-green-600">{canRedo ? 'Yes' : 'No'}</p>
        </div>
      </div>
      
      {/* Last Move Score Celebration */}
      {lastMoveScore > 0 && (
        <div className="text-center mt-2">
          <span className="text-green-600 font-medium">
            +{lastMoveScore} points last move!
          </span>
        </div>
      )}
      
      {/* Game Message */}
      {gameMessage && (
        <div className="text-center mt-2">
          <span className="text-blue-600 text-sm">
            {gameMessage}
          </span>
        </div>
      )}
    </div>
  );
};

export default ScoreBoard;