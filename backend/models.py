'''
Module for hosting Pydantic models.
Models for standardizing game-state context for AI system integration.
'''
from datetime import datetime
from typing import List, Optional, Literal, Union, Dict, Any
from pydantic import BaseModel, Field, validator, root_validator


class GameStatus(BaseModel):
    """Game status information"""
    game_over: bool = Field(description="True if the game is over (no valid moves)")
    game_won: bool = Field(description="True if the player has reached the win condition")
    in_progress: bool = Field(description="True if the game is still active")


class ResourceUsage(BaseModel):
    """Resource usage tracking (hints/redos)"""
    used: int = Field(ge=0, description="Number of resources already used")
    remaining: int = Field(ge=-1, description="Number of resources remaining (-1 for unlimited)")
    total: int = Field(ge=-1, description="Total resources allowed (-1 for unlimited)")


class GameResources(BaseModel):
    """All game resources (hints and redos)"""
    hints: ResourceUsage = Field(description="Hint usage tracking")
    redos: ResourceUsage = Field(description="Redo usage tracking")


class GameConfiguration(BaseModel):
    """Complete game configuration settings"""
    # Board settings
    board_size: tuple[int, int] = Field(description="Board dimensions [width, height]")
    win_target: int = Field(ge=4, le=10000, description="Target value to win the game")
    
    # Tile generation settings
    initial_tiles: int = Field(ge=0, description="Number of tiles at game start")
    random_new_tiles: int = Field(ge=0, description="Number of new tiles added per move")
    new_tile_values: List[int] = Field(description="Possible values for new tiles")
    
    # Streak system
    streak_enabled: bool = Field(description="Whether streak bonuses are enabled")
    streak_multiplier: float = Field(ge=1.0, description="Current streak multiplier")
    streak_bonus_percent: int = Field(ge=0, le=100, description="Bonus percentage per streak level")
    
    # Merge mechanics
    merge_strategy: Literal["standard", "reverse"] = Field(
        description="Merge priority direction (standard: away from move, reverse: towards move)"
    )
    allow_secondary_merge: bool = Field(
        description="Allow multiple merges in single move"
    )
    
    # Resource limits
    max_redo: int = Field(ge=-1, description="Maximum redos allowed (-1 for unlimited)")
    number_of_hints: int = Field(ge=0, description="Maximum hints allowed per game")
    
    @validator('board_size')
    def validate_board_size(cls, v):
        width, height = v
        if not (3 <= width <= 12) or not (3 <= height <= 12):
            raise ValueError("Board dimensions must be between 3x3 and 12x12")
        if width * height < 9:
            raise ValueError("Board must have at least 9 cells")
        return v
    
    @validator('new_tile_values')
    def validate_tile_values(cls, v):
        if not v:
            raise ValueError("Must have at least one possible tile value")
        if any(val < 1 or val > 10 for val in v):
            raise ValueError("Tile values must be between 1 and 10")
        return v


class GameState(BaseModel):
    """Current state of the game board and scoring"""
    board: List[List[int]] = Field(description="2D board matrix with tile values")
    score: int = Field(ge=0, description="Current game score")
    streak: int = Field(ge=0, description="Current consecutive merge streak")
    moves: int = Field(ge=0, description="Total number of moves made")
    status: GameStatus = Field(description="Current game status")
    
    @validator('board')
    def validate_board(cls, v):
        if not v:
            raise ValueError("Board cannot be empty")
        
        # Ensure all rows have same length
        row_length = len(v[0])
        if not all(len(row) == row_length for row in v):
            raise ValueError("All board rows must have the same length")
        
        # Ensure all values are non-negative
        if any(any(cell < 0 for cell in row) for row in v):
            raise ValueError("Board cells cannot have negative values")
        
        return v


class MoveHistoryEntry(BaseModel):
    """Single entry in the move history"""
    move_number: int = Field(ge=0, description="Sequential move number")
    direction: Optional[str] = Field(description="Move direction (up/down/left/right)")
    points_earned: int = Field(ge=0, description="Points earned from this move")
    merge_occurred: bool = Field(description="Whether any merges happened")
    streak_after_move: int = Field(ge=0, description="Streak value after move")
    board_state: List[List[int]] = Field(description="Board state after this move")
    timestamp: datetime = Field(description="When the move was made")


class AIHintHistory(BaseModel):
    """History of AI hints requested and their outcomes"""
    hint_number: int = Field(ge=1, description="Sequential hint number")
    requested_at: datetime = Field(description="When hint was requested")
    board_state_when_requested: List[List[int]] = Field(description="Board when hint was given")
    hint_direction: Optional[str] = Field(description="Direction suggested by AI")
    hint_reasoning: Optional[str] = Field(description="AI's reasoning for the suggestion")
    was_followed: Optional[bool] = Field(description="Whether player followed the hint")
    outcome_if_followed: Optional[str] = Field(description="Result if hint was followed")


class GameContext(BaseModel):
    """Complete game context for AI system"""
    # Current game state
    game_state: GameState = Field(description="Current state of the game")
    config: GameConfiguration = Field(description="Game configuration and rules")
    resources: GameResources = Field(description="Resource usage (hints/redos)")
    
    # Historical context
    move_history: List[MoveHistoryEntry] = Field(
        default=[], 
        description="Complete history of moves made"
    )
    hint_history: List[AIHintHistory] = Field(
        default=[], 
        description="History of AI hints and their effectiveness"
    )
    
    # Current context
    message: str = Field(default="", description="Current game message to display")
    last_updated: datetime = Field(description="When this context was last updated")
    
    # AI-specific metadata
    difficulty_assessment: Optional[str] = Field(
        default=None,
        description="AI's assessment of current game difficulty"
    )
    available_moves: Optional[List[str]] = Field(
        default=None,
        description="Currently valid moves that can be made"
    )
    board_analysis: Optional[Dict[str, Any]] = Field(
        default=None,
        description="AI's analysis of current board state"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "game_state": {
                    "board": [[2, 0, 0, 4], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 2]],
                    "score": 0,
                    "streak": 0,
                    "moves": 0,
                    "status": {
                        "game_over": False,
                        "game_won": False,
                        "in_progress": True
                    }
                },
                "config": {
                    "board_size": [4, 4],
                    "win_target": 2048,
                    "initial_tiles": 2,
                    "random_new_tiles": 1,
                    "new_tile_values": [2, 4],
                    "streak_enabled": False,
                    "streak_multiplier": 1.0,
                    "streak_bonus_percent": 10,
                    "merge_strategy": "standard",
                    "allow_secondary_merge": False,
                    "max_redo": 3,
                    "number_of_hints": 3
                },
                "resources": {
                    "hints": {"used": 0, "remaining": 3, "total": 3},
                    "redos": {"used": 0, "remaining": 3, "total": 3}
                },
                "move_history": [],
                "hint_history": [],
                "message": "Game started! Make your first move.",
                "last_updated": "2025-09-12T10:00:00Z"
            }
        }


class GameResponse(BaseModel):
    """
    Standard API response format for frontend
    Wraps game context with additional metadata
    """
    success: bool = Field(description="Whether the request was successful")
    data: GameContext = Field(description="Complete game context")
    message: Optional[str] = Field(default=None, description="Response message for user")
    timestamp: datetime = Field(description="When this response was generated")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "data": {
                    "game_state": {
                        "board": [[2, 0, 0, 4], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 2]],
                        "score": 0,
                        "streak": 0,
                        "moves": 0,
                        "status": {
                            "game_over": False,
                            "game_won": False,
                            "in_progress": True
                        }
                    }
                },
                "message": "Move completed successfully",
                "timestamp": "2025-09-12T10:00:00Z"
            }
        }


class CommandRequest(BaseModel):
    """Request model for game commands from frontend"""
    command: Literal["up", "down", "left", "right", "redo", "hint", "restart"] = Field(
        description="Game command to execute"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "command": "left"
            }
        }


class CommandResponse(BaseModel):
    """Response model for game command execution"""
    success: bool = Field(description="Whether the command was executed successfully")
    command: str = Field(description="The command that was executed")
    game_data: GameContext = Field(description="Updated game context after command")
    game_ended: bool = Field(description="Whether the game ended (won or lost)")
    error_message: Optional[str] = Field(default=None, description="Error message if command failed")
    timestamp: datetime = Field(description="When the command was executed")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "command": "left",
                "game_data": {"game_state": "..."},
                "game_ended": False,
                "error_message": None,
                "timestamp": "2025-09-12T10:00:00Z"
            }
        }


class GameConfigurationRequest(BaseModel):
    """Request model for creating a new game with custom configuration"""
    board_size: Optional[tuple[int, int]] = Field(default=(4, 4), description="Board dimensions [width, height]")
    win_target: Optional[int] = Field(default=2048, description="Target value to win")
    initial_tiles: Optional[int] = Field(default=2, description="Number of initial tiles")
    random_new_tiles: Optional[int] = Field(default=1, description="New tiles per move")
    new_tile_values: Optional[List[int]] = Field(default=[2, 4], description="Possible tile values")
    streak_enabled: Optional[bool] = Field(default=False, description="Enable streak bonuses")
    streak_bonus_percent: Optional[int] = Field(default=10, description="Streak bonus percentage")
    merge_strategy: Optional[Literal["standard", "reverse"]] = Field(default="standard", description="Merge direction priority")
    allow_secondary_merge: Optional[bool] = Field(default=False, description="Allow multiple merges per move")
    max_redo: Optional[int] = Field(default=3, description="Maximum redos (-1 for unlimited)")
    number_of_hints: Optional[int] = Field(default=3, description="Maximum hints per game")
    
    @root_validator(skip_on_failure=True)
    def validate_config(cls, values):
        """Custom validation that can be bypassed for testing"""
        # Get test_mode from context if available
        test_mode = cls.__config__.get('test_mode', False) if hasattr(cls, '__config__') else False
        
        if not test_mode:
            # Apply production validations
            win_target = values.get('win_target')
            if win_target is not None and (win_target < 4 or win_target > 10000):
                raise ValueError("win_target must be between 4 and 10000")
            
            initial_tiles = values.get('initial_tiles')
            if initial_tiles is not None and initial_tiles < 1:
                raise ValueError("initial_tiles must be at least 1")
            
            random_new_tiles = values.get('random_new_tiles')
            if random_new_tiles is not None and random_new_tiles < 1:
                raise ValueError("random_new_tiles must be at least 1")
            
            streak_bonus_percent = values.get('streak_bonus_percent')
            if streak_bonus_percent is not None and (streak_bonus_percent < 0 or streak_bonus_percent > 100):
                raise ValueError("streak_bonus_percent must be between 0 and 100")
            
            max_redo = values.get('max_redo')
            if max_redo is not None and max_redo < -1:
                raise ValueError("max_redo must be -1 or greater")
            
            number_of_hints = values.get('number_of_hints')
            if number_of_hints is not None and (number_of_hints < 0 or number_of_hints > 5):
                raise ValueError("number_of_hints must be between 0 and 5")
            
            # Validate new_tile_values
            new_tile_values = values.get('new_tile_values')
            if new_tile_values is not None:
                if not new_tile_values:  # Empty list
                    raise ValueError("new_tile_values cannot be empty")
                if any(val < 1 or val > 10 for val in new_tile_values):
                    raise ValueError("new_tile_values must be between 1 and 10")
        
        return values
    
    class Config:
        test_mode = False  # Default to production mode
        json_schema_extra = {
            "example": {
                "board_size": [4, 4],
                "win_target": 2048,
                "streak_enabled": True,
                "max_redo": 5,
                "number_of_hints": 3
            }
        }


class TestGameConfigurationRequest(GameConfigurationRequest):
    """Test-specific configuration request that bypasses validation"""
    
    @root_validator(skip_on_failure=True)
    def validate_config(cls, values):
        """Override parent validation to allow test values"""
        # In test mode, skip all validations
        return values
    
    class Config:
        test_mode = True  # Enable test mode to bypass validations
        json_schema_extra = {
            "example": {
                "board_size": [4, 4],
                "initial_tiles": 0,  # Allowed in test mode
                "random_new_tiles": 0,  # Allowed in test mode
                "win_target": 2048
            }
        }


class AIRequest(BaseModel):
    """Request model for AI hint system"""
    context: GameContext = Field(description="Complete game context")
    request_type: Literal["hint", "analysis", "strategy"] = Field(
        description="Type of AI assistance requested"
    )
    specific_question: Optional[str] = Field(
        description="Specific question or area of focus"
    )


class AuthRequest(BaseModel):
    """Request model for authentication with invitation code"""
    invitation_code: str = Field(description="Invitation code for authentication", min_length=1)
    
    class Config:
        json_schema_extra = {
            "example": {
                "invitation_code": "GAME2048"
            }
        }


class AuthResponse(BaseModel):
    """Response model for authentication"""
    success: bool = Field(description="Whether authentication was successful")
    message: str = Field(description="Response message")
    authenticated: bool = Field(description="Whether the user is now authenticated")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Authentication successful",
                "authenticated": True
            }
        }


class AIResponse(BaseModel):
    """Response model from AI hint system"""
    success: bool = Field(description="Whether the AI request was successful")
    suggestion: Optional[str] = Field(default=None, description="Suggested move direction")
    reasoning: str = Field(description="AI's reasoning and analysis")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence in suggestion (0-1)")
    alternative_moves: Optional[List[str]] = Field(default=None, description="Alternative move suggestions")
    strategic_advice: Optional[str] = Field(default=None, description="General strategic advice")
    difficulty_assessment: Optional[str] = Field(default=None, description="Assessment of current situation")
    error_message: Optional[str] = Field(default=None, description="Error message if request failed")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "suggestion": "left",
                "reasoning": "Moving left will consolidate your tiles and create opportunities for merging the two 2s together.",
                "confidence": 0.85,
                "alternative_moves": ["up", "down"],
                "strategic_advice": "Focus on keeping your highest tiles in one corner and building towards them.",
                "difficulty_assessment": "early_game",
                "error_message": None
            }
        }
