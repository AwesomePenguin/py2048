import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Board from '../components/Board';
import Button from '../components/Button';
import MessageBubble from '../components/MessageBubble';
import ScoreBoard from '../components/ScoreBoard';
import AIHintModal from '../components/AIHintModal';

// Type definitions for backend responses
interface FullGameConfig {
  board_size: [number, number];
  win_target: number;
  initial_tiles: number;
  random_new_tiles: number;
  merge_strategy: 'standard' | 'reverse';
  streak_enabled: boolean;
  streak_multiplier: number;
  hint_limit: number;
  redo_limit: number;
}

interface MoveHistoryEntry {
  move_number: number;
  direction: string;
  score_before: number;
  score_after: number;
  points_earned: number;
  tiles_merged: number;
  new_tile_position?: [number, number];
  new_tile_value?: number;
  timestamp: string;
}

interface HintHistoryEntry {
  hint_number: number;
  request_timestamp: string;
  ai_response: string;
  parsed_suggestion: string | null;
  was_followed: boolean | null;
  confidence_score?: number;
}

interface BoardAnalysis {
  empty_tiles: number;
  max_tile: number;
  mergeable_pairs: number;
  corner_strategy_score: number;
  monotonicity_score: number;
  smoothness_score: number;
}

// Backend response structure matching the Pydantic models
interface BackendGameResponse {
  success: boolean;
  data: {
    game_state: {
      board: number[][];
      score: number;
      streak: number;
      moves: number;
      status: {
        game_over: boolean;
        game_won: boolean;
        in_progress: boolean;
      };
    };
    config: FullGameConfig;
    resources: {
      hints: {
        used: number;
        remaining: number;
        total: number;
      };
      redos: {
        used: number;
        remaining: number;
        total: number;
      };
    };
    move_history: MoveHistoryEntry[];
    hint_history: HintHistoryEntry[];
    message: string;
    last_updated: string;
    difficulty_assessment: string | null;
    available_moves: string[] | null;
    board_analysis: BoardAnalysis;
  };
  message: string;
  timestamp: string;
}

interface BackendCommandResponse {
  success: boolean;
  command: string;
  game_data: {
    game_state: {
      board: number[][];
      score: number;
      streak: number;
      moves: number;
      status: {
        game_over: boolean;
        game_won: boolean;
        in_progress: boolean;
      };
    };
    resources: {
      hints: {
        used: number;
        remaining: number;
        total: number;
      };
      redos: {
        used: number;
        remaining: number;
        total: number;
      };
    };
    message: string;
    config?: FullGameConfig;
    move_history?: MoveHistoryEntry[];
    hint_history?: HintHistoryEntry[];
    available_moves?: string[] | null;
    board_analysis?: BoardAnalysis;
    difficulty_assessment?: string | null;
    last_updated?: string;
  };
  game_ended: boolean;
  error_message: string | null;
  timestamp: string;
}

// Frontend-friendly game state interface
interface GameState {
  board: number[][];
  score: number;
  high_score: number;
  moves: number;
  game_over: boolean;
  win: boolean;
  can_redo: boolean;
  streak_count: number;
  last_move_score: number;
  message: string;
  hints_remaining: number;
  available_moves?: string[];
}

// Frontend-friendly game config interface for API requests (all fields optional)
interface GameConfigRequest {
  board_size?: [number, number];
  win_target?: number;
  initial_tiles?: number;
  random_new_tiles?: number;
  merge_strategy?: 'standard' | 'reverse';
  streak_enabled?: boolean;
  streak_multiplier?: number;
  hint_limit?: number;
  redo_limit?: number;
}

const API_BASE_URL = 'http://localhost:8000';

// Helper function to convert backend response to frontend game state
const convertBackendResponse = (
  backendResponse: BackendGameResponse | BackendCommandResponse,
  lastMoveScore: number = 0
): GameState => {
  let gameData;
  let message = '';
  
  if ('data' in backendResponse) {
    // GameResponse format
    gameData = backendResponse.data;
    message = backendResponse.message || backendResponse.data.message || '';
  } else {
    // CommandResponse format
    gameData = backendResponse.game_data;
    message = gameData.message || '';
  }

  return {
    board: gameData.game_state.board,
    score: gameData.game_state.score,
    high_score: gameData.game_state.score, // Backend doesn't track high score separately yet
    moves: gameData.game_state.moves,
    game_over: gameData.game_state.status.game_over,
    win: gameData.game_state.status.game_won,
    can_redo: gameData.resources.redos.remaining > 0,
    streak_count: gameData.game_state.streak,
    last_move_score: lastMoveScore,
    message: message,
    hints_remaining: gameData.resources.hints.remaining,
    available_moves: gameData.available_moves || [],
  };
};

export default function Game() {
  const router = useRouter();
  const { mode } = router.query;
  
  const [gameState, setGameState] = useState<GameState | null>(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<{
    text: string;
    type: 'success' | 'error' | 'info' | 'warning' | 'hint';
    timestamp: number;
  } | null>(null);
  
  // AI Hint Modal state
  const [showHintModal, setShowHintModal] = useState(false);
  const [aiHintMessage, setAiHintMessage] = useState('');
  const [fullAiHint, setFullAiHint] = useState<{
    suggestion?: string;
    reasoning: string;
    strategy?: string;
    confidence?: number;
    alternatives?: string[];
  } | null>(null);
  // Separate state for persistent ScoreBoard hint message
  const [persistentHintMessage, setPersistentHintMessage] = useState<string>('');

  // Function to parse AI response into structured format
  const parseAiResponse = (response: string) => {
    const sections = {
      suggestion: '',
      reasoning: '',
      strategy: '',
    };

    // Extract recommended move
    const moveMatch = response.match(/\*\*Recommended move:\*\*\s*\*?(UP|DOWN|LEFT|RIGHT|up|down|left|right)\*?/i);
    if (moveMatch) {
      sections.suggestion = moveMatch[1].toUpperCase();
    }

    // Extract reasoning (replace newlines with spaces for easier parsing)
    const cleanResponse = response.replace(/\n/g, ' ');
    const reasoningMatch = cleanResponse.match(/\*\*Reasoning:\*\*(.*?)(?=\*\*Strategy:\*\*|$)/i);
    if (reasoningMatch) {
      sections.reasoning = reasoningMatch[1].trim();
    }

    // Extract strategy
    const strategyMatch = cleanResponse.match(/\*\*Strategy:\*\*(.*?)$/i);
    if (strategyMatch) {
      sections.strategy = strategyMatch[1].trim();
    }

    return sections;
  };

  // Function to create brief hint message for scoreboard
  const createBriefHintMessage = (parsed: ReturnType<typeof parseAiResponse>) => {
    if (parsed.suggestion) {
      return `💡 AI suggests: ${parsed.suggestion} - Click for details`;
    }
    return '💡 AI hint available - Click for details';
  };

  // Function to handle hint message click (opens modal with full hint)
  const handleHintMessageClick = () => {
    if (fullAiHint) {
      setShowHintModal(true);
    }
  };

  // Helper functions for centralized messaging
  const showMessage = (text: string, type: 'success' | 'error' | 'info' | 'warning' | 'hint') => {
    setMessage({ text, type, timestamp: Date.now() });
  };

  const clearMessage = () => setMessage(null);

  const showError = (text: string) => showMessage(text, 'error');
  const showSuccess = (text: string) => showMessage(text, 'success');
  const showInfo = (text: string) => showMessage(text, 'info');

  useEffect(() => {
    // Check authentication
    const isAuthenticated = sessionStorage.getItem('py2048_authenticated');
    if (!isAuthenticated) {
      router.push('/auth');
      return;
    }

    // Initialize game when component mounts and mode is available
    if (mode) {
      initializeGame();
    }
  }, [router, mode]);

  const initializeGame = async () => {
    setLoading(true);
    clearMessage();
    // Clear any existing hint data when starting a new game
    setPersistentHintMessage('');
    setFullAiHint(null);
    setAiHintMessage('');
    
    try {
      let config: GameConfigRequest = {};
      
      if (mode === 'custom') {
        const storedConfig = sessionStorage.getItem('py2048_custom_config');
        if (storedConfig) {
          config = JSON.parse(storedConfig) as GameConfigRequest;
        }
      }
      // For standard mode, we use empty config (backend defaults)

      const response = await fetch(`${API_BASE_URL}/new-game`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(config),
      });

      if (!response.ok) {
        throw new Error(`Failed to start game: ${response.statusText}`);
      }

      const backendResponse: BackendGameResponse = await response.json();
      if (!backendResponse.success) {
        throw new Error('Backend returned unsuccessful response');
      }
      
      const gameState = convertBackendResponse(backendResponse);
      setGameState(gameState);
      showSuccess('Game started successfully!');
    } catch (err) {
      console.error('Error initializing game:', err);
      showError('Failed to start the game. Please check if the backend server is running.');
    } finally {
      setLoading(false);
    }
  };

  const makeMove = async (direction: 'up' | 'down' | 'left' | 'right') => {
    if (!gameState || gameState.game_over || loading) return;
    
    setLoading(true);
    clearMessage();
    
    try {
      const response = await fetch(`${API_BASE_URL}/move/${direction}`, {
        method: 'POST',
      });

      if (!response.ok) {
        throw new Error(`Move failed: ${response.statusText}`);
      }

      const backendResponse: BackendCommandResponse = await response.json();
      if (!backendResponse.success) {
        const errorMessage = backendResponse.error_message || 'Move failed';
        
        // Handle invalid move errors gracefully
        if (errorMessage.toLowerCase().includes('invalid move') || 
            errorMessage.toLowerCase().includes('no tiles can move')) {
          showInfo(`No tiles can move ${direction.toUpperCase()}. Try a different direction!`);
          return; // Don't treat as fatal error, just show message
        }
        
        // Other errors are still treated as fatal
        throw new Error(errorMessage);
      }
      
      // Calculate points earned this move (difference in scores)
      const oldScore = gameState.score;
      const newScore = backendResponse.game_data.game_state.score;
      const lastMoveScore = newScore - oldScore;
      
      const newGameState = convertBackendResponse(backendResponse, lastMoveScore);
      setGameState(newGameState);
      
      // Clear hint data when board state changes after a successful move
      setPersistentHintMessage('');
      setFullAiHint(null);
      setAiHintMessage('');
      
      // Show success message for good moves
      if (lastMoveScore > 0) {
        showSuccess(`Great move! +${lastMoveScore} points`);
      }
    } catch (err) {
      console.error('Error making move:', err);
      showError('Failed to make move. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const getAIHint = async () => {
    if (!gameState || gameState.game_over || loading) return;
    
    // If there's already a hint available, just show the modal with existing data
    if (fullAiHint && persistentHintMessage) {
      setShowHintModal(true);
      return;
    }
    
    setLoading(true);
    setShowHintModal(true); // Open the modal
    setAiHintMessage(''); // Clear previous hint
    setFullAiHint(null); // Clear previous structured hint
    
    try {
      const response = await fetch(`${API_BASE_URL}/hint`, {
        method: 'POST',
      });

      if (!response.ok) {
        throw new Error(`Hint request failed: ${response.statusText}`);
      }

      const backendResponse: BackendCommandResponse = await response.json();
      if (!backendResponse.success) {
        throw new Error(backendResponse.error_message || 'Failed to get hint');
      }

      const newGameState = convertBackendResponse(backendResponse);
      setGameState(newGameState);
      
      // Parse the AI response for better formatting
      const parsedHint = parseAiResponse(newGameState.message);
      setFullAiHint({
        suggestion: parsedHint.suggestion,
        reasoning: parsedHint.reasoning,
        strategy: parsedHint.strategy,
        confidence: 0.8, // Default confidence
        alternatives: newGameState.available_moves?.filter((move: string) => move !== parsedHint.suggestion.toLowerCase()) || []
      });
      
      // Set brief message for scoreboard (persistent) and full message for modal
      const briefMessage = createBriefHintMessage(parsedHint);
      setPersistentHintMessage(briefMessage); // This persists on ScoreBoard
      setAiHintMessage(newGameState.message); // Full message for modal
      
      // Show temporary bubble message
      showMessage(briefMessage, 'hint');
      
    } catch (err) {
      console.error('Error getting AI hint:', err);
      showError('Failed to get AI hint. Please try again.');
      setShowHintModal(false); // Close modal on error
    } finally {
      setLoading(false);
    }
  };

  const undoMove = async () => {
    if (!gameState || !gameState.can_redo || loading) return;
    
    setLoading(true);
    clearMessage();
    
    try {
      const response = await fetch(`${API_BASE_URL}/redo`, {
        method: 'POST',
      });

      if (!response.ok) {
        throw new Error(`Undo failed: ${response.statusText}`);
      }

      const backendResponse: BackendCommandResponse = await response.json();
      if (!backendResponse.success) {
        throw new Error(backendResponse.error_message || 'Undo failed');
      }

      const newGameState = convertBackendResponse(backendResponse);
      setGameState(newGameState);
      showSuccess('Move undone successfully!');
    } catch (err) {
      console.error('Error undoing move:', err);
      showError('Failed to undo move. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const restartGame = () => {
    initializeGame();
  };

  const goBack = () => {
    router.push('/game-select');
  };

  // Keyboard controls
  useEffect(() => {
    const handleKeyPress = (e: KeyboardEvent) => {
      if (loading) return;
      
      switch (e.key) {
        case 'ArrowUp':
        case 'w':
        case 'W':
          e.preventDefault();
          makeMove('up');
          break;
        case 'ArrowDown':
        case 's':
        case 'S':
          e.preventDefault();
          makeMove('down');
          break;
        case 'ArrowLeft':
        case 'a':
        case 'A':
          e.preventDefault();
          makeMove('left');
          break;
        case 'ArrowRight':
        case 'd':
        case 'D':
          e.preventDefault();
          makeMove('right');
          break;
        case 'h':
        case 'H':
          e.preventDefault();
          getAIHint();
          break;
        case 'u':
        case 'U':
          e.preventDefault();
          undoMove();
          break;
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [loading, gameState]);

  if (loading && !gameState) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Starting your game...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="max-w-2xl mx-auto">
        {/* Header */}
        <div className="text-center mb-6">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">py2048</h1>
          <p className="text-gray-600 capitalize">{mode} Mode</p>
        </div>

        {/* Centralized Message Display */}
        <MessageBubble message={message} onDismiss={clearMessage} />

        {gameState ? (
          <>
            {/* Score Display - Now using ScoreBoard component */}
            <ScoreBoard
              score={gameState.score}
              highScore={gameState.high_score}
              moves={gameState.moves}
              streakCount={gameState.streak_count}
              hintsRemaining={gameState.hints_remaining}
              canRedo={gameState.can_redo}
              lastMoveScore={gameState.last_move_score}
              gameMessage={persistentHintMessage}
              onHintMessageClick={handleHintMessageClick}
            />

            {/* Game Board */}
            <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
              <Board 
                board={gameState.board} 
                loading={loading}
                onMove={makeMove}
              />
            </div>

            {/* Game Status */}
            {(gameState.win || gameState.game_over) && (
              <div className="bg-white rounded-lg shadow-lg p-6 mb-6 text-center">
                {gameState.win && (
                  <div className="text-green-600 mb-2">
                    <h2 className="text-2xl font-bold">🎉 You Win!</h2>
                    <p>Congratulations! You have reached the target!</p>
                  </div>
                )}
                {gameState.game_over && (
                  <div className="text-red-600 mb-2">
                    <h2 className="text-2xl font-bold">Game Over</h2>
                    <p>No more moves available!</p>
                  </div>
                )}
              </div>
            )}

            {/* Controls */}
            <div className="bg-white rounded-lg shadow-lg p-6">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                <Button 
                  onClick={() => makeMove('up')} 
                  disabled={loading || gameState.game_over}
                  variant="move"
                >
                  ↑ Up (W)
                </Button>
                <Button 
                  onClick={() => makeMove('down')} 
                  disabled={loading || gameState.game_over}
                  variant="move"
                >
                  ↓ Down (S)
                </Button>
                <Button 
                  onClick={() => makeMove('left')} 
                  disabled={loading || gameState.game_over}
                  variant="move"
                >
                  ← Left (A)
                </Button>
                <Button 
                  onClick={() => makeMove('right')} 
                  disabled={loading || gameState.game_over}
                  variant="move"
                >
                  → Right (D)
                </Button>
              </div>
              
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                <Button 
                  onClick={getAIHint} 
                  disabled={loading || gameState.game_over || gameState.hints_remaining <= 0}
                  variant="secondary"
                >
                  💡 AI Hint (H) {gameState.hints_remaining > 0 ? `(${gameState.hints_remaining})` : '(0)'}
                </Button>
                <Button 
                  onClick={undoMove} 
                  disabled={loading || !gameState.can_redo || gameState.game_over}
                  variant="secondary"
                >
                  ↶ Undo (U)
                </Button>
                <Button 
                  onClick={restartGame} 
                  disabled={loading}
                  variant="secondary"
                >
                  🔄 Restart
                </Button>
              </div>
              
              <div className="flex justify-between items-center mt-6 pt-4 border-t border-gray-200">
                <Button 
                  onClick={goBack}
                  variant="ghost"
                >
                  ← Back to Menu
                </Button>
                
                <div className="text-sm text-gray-500 text-right">
                  <p>Use arrow keys or WASD to move</p>
                  <p>Press H for hints, U to undo</p>
                </div>
              </div>
            </div>

            {/* AI Hint Modal */}
            <AIHintModal
              isOpen={showHintModal}
              isLoading={loading}
              hintMessage={aiHintMessage}
              fullHint={fullAiHint}
              onClose={() => setShowHintModal(false)}              
            />
          </>
        ) : (
          <div className="text-center py-12">
            <p className="text-gray-600 mb-4">Failed to load the game.</p>
            <Button onClick={initializeGame}>
              Try Again
            </Button>
          </div>
        )}
      </div>
    </div>
  );
}
