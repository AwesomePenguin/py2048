'''
Core module for the 2048 game logic
'''

import copy
import random
from typing import Optional
from datetime import datetime
import json
from ai_chat import AIChat
from models import (GameContext, GameState, GameStatus, GameConfiguration, 
                   GameResources, ResourceUsage, GameResponse, CommandResponse, 
                   MoveHistoryEntry, AIHintHistory, GameConfigurationRequest)

class Game:
    def __init__(self, config: Optional[GameConfigurationRequest] = None, test_mode: bool = False):
        '''
        Initialize the game state
        If no config is provided, use default settings
        '''
        # Initialize config first
        self.pydantic_config = config
        self.test_mode = test_mode  # If true, suppress random elements for testing

        # Extract configuration values from Pydantic model or use defaults
        if config:
            self.size_x, self.size_y = config.board_size if config.board_size else (4, 4)
            self.win_value = config.win_target if config.win_target else 2048
            self.initial_tiles = config.initial_tiles if config.initial_tiles is not None else random.randint(2, 4)
            self.random_new_tiles = config.random_new_tiles if config.random_new_tiles is not None else random.randint(2, 4)
            self.new_tile_values = config.new_tile_values if config.new_tile_values else [2, 4]
            self.max_redo = config.max_redo if config.max_redo is not None else 3
            self.merge_strategy = config.merge_strategy if config.merge_strategy else 'standard'
            self.allow_secondary_merge = config.allow_secondary_merge if config.allow_secondary_merge is not None else False
            self.use_streak = config.streak_enabled if config.streak_enabled is not None else False
            self.streak_bonus_percent = config.streak_bonus_percent if config.streak_bonus_percent is not None else 10
            self.number_of_hints = config.number_of_hints if config.number_of_hints is not None else 3
        else:
            # Default values
            self.size_x = 4
            self.size_y = 4
            self.win_value = 2048
            self.initial_tiles = random.randint(2, 4)
            self.random_new_tiles = random.randint(2, 4)
            self.new_tile_values = [2, 4]
            self.max_redo = 3
            self.merge_strategy = 'standard'
            self.allow_secondary_merge = False
            self.use_streak = False
            self.streak_bonus_percent = 10
            self.number_of_hints = 3

        # set output mode: 'console' or 'web'
        self.output_mode = 'console'  # Keep this as default for now

        # non-configurable parameters
        self.valid_commands = ['up', 'down', 'left', 'right', 'redo', 'hint', 'exit', 'restart']
        self.command_descriptions = {
            'up': 'Move tiles up',
            'down': 'Move tiles down',
            'left': 'Move tiles left',
            'right': 'Move tiles right',
            'redo': 'Redo last action',
            'hint': 'Get a hint',
            'exit': 'Exit the game',
            'restart': 'Restart the game'
        }

        # Initialize game state dictionary - this will be the single source of truth
        self.state = {
            'board': [[0] * self.size_x for _ in range(self.size_y)],
            'score': 0,
            'streak': 0,
            'streak_multiplier': 1,
            'over': False,
            'won': False,
            'display_message': "",
            'moves_count': 0,
            'move_history': [],  # List to track move history
        }
        
        # Session-persistent counters (not part of state that gets saved/restored)
        self.hints_used = 0
        self.redos_used = 0
        
        # History to store previous states (list of state dictionaries)
        self.history = []

        # History of hints
        self.hint_history = []

        # Initialize the game
        self.init_game()

    # Property accessors for seamless state management
    @property
    def board(self):
        return self.state['board']
    
    @board.setter
    def board(self, value):
        self.state['board'] = value
    
    @property
    def score(self):
        return self.state['score']
    
    @score.setter
    def score(self, value):
        self.state['score'] = value
    
    @property
    def streak(self):
        return self.state['streak']
    
    @streak.setter
    def streak(self, value):
        self.state['streak'] = value
    
    @property
    def over(self):
        return self.state['over']
    
    @over.setter
    def over(self, value):
        self.state['over'] = value
    
    @property
    def won(self):
        return self.state['won']
    
    @won.setter
    def won(self, value):
        self.state['won'] = value
    
    @property
    def display_message(self):
        return self.state['display_message']
    
    @display_message.setter
    def display_message(self, value):
        self.state['display_message'] = value
    
    @property
    def moves_count(self):
        return self.state['moves_count']
    
    @moves_count.setter
    def moves_count(self, value):
        self.state['moves_count'] = value

    @property
    def move_history(self):
        return self.state['move_history']
    
    @move_history.setter
    def move_history(self, value):
        self.state['move_history'] = value

    def get_state_copy(self):
        '''
        Get a deep copy of the current state for history storage
        '''
        return {
            'board': copy.deepcopy(self.state['board']),  # Deep copy of board
            'score': self.state['score'],
            'streak': self.state['streak'],
            'streak_multiplier': self.state['streak_multiplier'],
            'over': self.state['over'],
            'won': self.state['won'],
            'display_message': self.state['display_message'],
            'moves_count': self.state['moves_count'],
            'move_history': copy.deepcopy(self.state['move_history'])  # Deep copy of move history
        }
    
    def restore_state(self, saved_state):
        '''
        Restore game state from a saved state dictionary
        '''
        self.state['board'] = [row[:] for row in saved_state['board']]  # Deep copy
        self.state['score'] = saved_state['score']
        self.state['streak'] = saved_state['streak']
        self.state['streak_multiplier'] = saved_state['streak_multiplier']
        self.state['over'] = saved_state['over']
        self.state['won'] = saved_state['won']
        self.state['display_message'] = saved_state['display_message']
        self.state['moves_count'] = saved_state['moves_count']
        self.state['move_history'] = copy.deepcopy(saved_state.get('move_history', []))
    
    def save_state_to_history(self):
        '''
        Save current state to history before making a move
        '''
        self.history.append(self.get_state_copy())

    def validate_config(self):
        '''
        Validate the configuration params against the constraints
        '''
        # check board size constraints
        if not (3 <= self.size_x <= 12):
            raise ValueError("size_x must be between 3 and 12")
        if not (3 <= self.size_y <= 12):
            raise ValueError("size_y must be between 3 and 12")
        if self.size_x * self.size_y < 9:
            raise ValueError("Board size must be at least 9 cells")
        
        # check win value constraints
        if not (4 <= self.win_value <= 10000):
            raise ValueError("win_value must be between 4 and 10000")
        
        # check initial tiles constraints
        if not self.test_mode: # Skip this check in test mode
            if not (1 <= self.initial_tiles <= self.size_x * self.size_y // 2):
                raise ValueError("initial_tiles must be at least 1 and at most half of the board size")
        
        # check new tile values constraints
        if not all(v in range(1, 11) for v in self.new_tile_values):
            raise ValueError("new_tile_values must be between 1 and 10")
        if len(self.new_tile_values) == 0:
            raise ValueError("new_tile_values must contain at least one value")
        if not self.test_mode: # Skip this check in test mode
            if not (1 <= self.random_new_tiles <= self.size_x * self.size_y // 2):
                raise ValueError("random_new_tiles must be at least 1 and at most half of the board size")   
        
        # check max_redo constraints
        if not (self.max_redo >= -1):
            raise ValueError("max_redo must be -1 (unlimited) or at least 0 (disabled)")
        
        # check number_of_hints constraints
        if not (0 <= self.number_of_hints <= 5):
            raise ValueError("number_of_hints must be between 0 and 5")
        
        # check initial tile value vs win condition
        if any(v >= self.win_value for v in self.new_tile_values):
            raise ValueError("All new tile values must be less than win condition")
        
        # check streak multiplier if using streak
        if self.use_streak and hasattr(self, 'streak_bonus_percent'):
            if not (0 <= self.streak_bonus_percent <= 100):
                raise ValueError("streak_bonus_percent must be between 0 and 100")

    def init_game(self):
        '''
        Initialize the game board and add initial tiles
        '''
        # Validate configuration before starting

        self.validate_config()
        
        # Reset all state values
        self.state['board'] = [[0] * self.size_x for _ in range(self.size_y)]
        self.state['score'] = 0
        self.state['streak'] = 0
        self.state['streak_multiplier'] = 1
        self.state['over'] = False
        self.state['won'] = False
        self.state['display_message'] = "Game started!"
        self.state['moves_count'] = 0
        self.state['move_history'] = []  # Reset move history
        
        # Reset session-persistent counters
        self.hints_used = 0
        self.redos_used = 0
        
        # Clear history
        self.history = []
        self.hint_history = []  # Reset hint history
        
        # Add initial tiles
        for _ in range(self.initial_tiles):
            self.add_random_tile()
        
        # Save initial state to history
        self.save_state_to_history()
    
    def add_random_tile(self):
        '''
        Add a random tile to an empty cell on the board
        '''
        empty_cells = [(y, x) for y in range(self.size_y) for x in range(self.size_x) if self.board[y][x] == 0]
        if not empty_cells:
            return False  # No empty cells available
        y, x = random.choice(empty_cells)
        self.board[y][x] = random.choice(self.new_tile_values)
        return True
    
    def get_display_data(self):
        '''
        Get all data needed for display in a structured format
        This method prepares data for both console and web output
        '''
        return {
            'board': self.board,
            'score': self.score,
            'streak': self.streak,
            'streak_multiplier': self.state['streak_multiplier'],
            'moves_count': self.moves_count,
            'hints_used': self.hints_used,
            'redos_used': self.redos_used,
            'redos_remaining': max(0, self.max_redo - self.redos_used) if self.max_redo != -1 else -1,
            'hints_remaining': max(0, self.number_of_hints - self.hints_used),
            'game_over': self.over,
            'game_won': self.won,
            'display_message': self.display_message,
            'board_size': {'width': self.size_x, 'height': self.size_y},
            'win_value': self.win_value,
            'streak_enabled': self.use_streak
        }
    
    def render_console(self):
        '''
        Render the game state for console output
        '''
        data = self.get_display_data()
        
        # Display message if any
        if data['display_message']:
            print(f"\n{data['display_message']}")
        
        # Display the board
        print("\n" + "="*50)
        for row in data['board']:
            print("│ " + " │ ".join(str(val).rjust(4) if val != 0 else "    " for val in row) + " │")
        print("="*50)
        
        # Display game statistics
        print(f"Score: {data['score']:<8} Moves: {data['moves_count']:<4}", end="")
        if data['streak_enabled']:
            print(f" Streak: {data['streak']:<3} (×{data['streak_multiplier']:.1f})", end="")
        print()
        
        # Display remaining resources
        redos_text = f"{data['redos_remaining']}" if data['redos_remaining'] != -1 else "∞"
        print(f"Hints: {data['hints_remaining']}/{self.number_of_hints}  Redos: {redos_text}")
        
        # Display game status
        if data['game_won']:
            print("🎉 CONGRATULATIONS! YOU WON! 🎉")
        elif data['game_over']:
            print("💀 GAME OVER! No more valid moves!")
        
        print()  # Extra spacing
    
    def get_json_response(self):
        '''
        Get game state as JSON for web API responses
        '''
        data = self.get_display_data()
        
        # Add additional metadata for web client
        web_data = {
            **data,
            'config': {
                'board_size': {'width': self.size_x, 'height': self.size_y},
                'win_value': self.win_value,
                'max_redos': self.max_redo,
                'max_hints': self.number_of_hints,
                'streak_enabled': self.use_streak,
                'streak_bonus_percent': self.streak_bonus_percent,
                'merge_strategy': self.merge_strategy,
                'allow_secondary_merge': self.allow_secondary_merge
            },
            'available_commands': self.valid_commands,
            'timestamp': __import__('datetime').datetime.now().isoformat()
        }
        
        return json.dumps(web_data, indent=2)
    
    def print_board(self):
        '''
        Display the game state according to the output mode
        '''
        if self.output_mode == 'console':
            self.render_console()
        elif self.output_mode == 'web':
            # For web mode, just return the JSON data
            # The actual HTTP response will be handled by the API layer
            return self.get_json_response()
        else:
            raise ValueError(f"Unknown output mode: {self.output_mode}")
        
        # Clear display message after showing it
        self.display_message = ""
    
    def get_api_state(self):
        '''
        Get a clean state dictionary for API responses
        Optimized for frontend consumption
        '''
        return {
            'game_state': {
                'board': self.board,
                'score': self.score,
                'streak': self.streak,
                'moves': self.moves_count,
                'status': {
                    'game_over': self.over,
                    'game_won': self.won,
                    'in_progress': not (self.over or self.won)
                }
            },
            'resources': {
                'hints': {
                    'used': self.hints_used,
                    'remaining': max(0, self.number_of_hints - self.hints_used),
                    'total': self.number_of_hints
                },
                'redos': {
                    'used': self.redos_used,
                    'remaining': max(0, self.max_redo - self.redos_used) if self.max_redo != -1 else -1,
                    'total': self.max_redo
                }
            },
            'config': {
                'board_size': [self.size_x, self.size_y],
                'win_target': self.win_value,
                'streak_enabled': self.use_streak,
                'streak_multiplier': self.state['streak_multiplier']
            },
            'message': self.display_message,
            'last_updated': __import__('datetime').datetime.now().isoformat()
        }
    
    def get_ai_context(self) -> GameContext:
        '''
        Get complete game context for AI system integration
        Returns standardized Pydantic model with all game state and history
        '''
        # Create game status
        status = GameStatus(
            game_over=self.over,
            game_won=self.won,
            in_progress=not (self.over or self.won)
        )
        
        # Create current game state
        game_state = GameState(
            board=copy.deepcopy(self.board),
            score=self.score,
            streak=self.streak,
            moves=self.moves_count,
            status=status
        )
        
        # Create game configuration
        config = GameConfiguration(
            board_size=(self.size_x, self.size_y),
            win_target=self.win_value,
            initial_tiles=self.initial_tiles,
            random_new_tiles=self.random_new_tiles,
            new_tile_values=self.new_tile_values,
            streak_enabled=self.use_streak,
            streak_multiplier=self.state['streak_multiplier'],
            streak_bonus_percent=self.streak_bonus_percent,
            merge_strategy=self.merge_strategy,
            allow_secondary_merge=self.allow_secondary_merge,
            max_redo=self.max_redo,
            number_of_hints=self.number_of_hints
        )
        
        # Create resource usage tracking
        hints_remaining = max(0, self.number_of_hints - self.hints_used)
        redos_remaining = max(0, self.max_redo - self.redos_used) if self.max_redo != -1 else -1
        
        resources = GameResources(
            hints=ResourceUsage(
                used=self.hints_used,
                remaining=hints_remaining,
                total=self.number_of_hints
            ),
            redos=ResourceUsage(
                used=self.redos_used,
                remaining=redos_remaining,
                total=self.max_redo
            )
        )
        
        # Determine available moves
        available_moves = []
        for direction in ['up', 'down', 'left', 'right']:
            # Test move without changing state
            original_board = [row[:] for row in self.board]
            test_points, test_merged = self._execute_move(direction)
            if self.board != original_board:
                available_moves.append(direction)
            # Restore original board after test
            self.board = original_board
        
        # Create complete context
        context = GameContext(
            game_state=game_state,
            config=config,
            resources=resources,
            move_history=self.move_history,  # Use actual move history
            hint_history=self.hint_history,  # Use actual hint history
            message=self.display_message,
            last_updated=datetime.now(),
            available_moves=available_moves
        )
        
        return context
    
    def process_command(self, command: str) -> CommandResponse:
        """
        Process a command and return standardized Pydantic response for frontend API
        """
        if command not in self.valid_commands:
            return CommandResponse(
                success=False,
                command=command,
                game_data=self.get_ai_context(),
                game_ended=False,
                error_message=f"Invalid command. Valid commands: {', '.join(self.valid_commands)}",
                timestamp=datetime.now()
            )
        
        success = True
        error_message = None
        
        try:
            if command == 'redo':
                success = self.handle_redo()
                if not success:
                    error_message = self.display_message
            elif command == 'hint':
                success = self.handle_hint()
                if not success:
                    error_message = self.display_message
            elif command in ['up', 'down', 'left', 'right']:
                success = self.handle_move(command)
                if not success:
                    error_message = self.display_message
            elif command == 'restart':
                self.init_game()
                success = True
            else:
                success = False
                error_message = f"Command '{command}' not implemented"
                
        except Exception as e:
            success = False
            error_message = str(e)
        
        # Check for game end conditions after processing command
        game_ended = False
        if command in ['up', 'down', 'left', 'right']:
            if self.check_win():
                self.display_message = "Congratulations! You've reached the target tile!"
                game_ended = True
            elif self.check_game_over():
                self.display_message = "No more valid moves! Game Over!"
                game_ended = True
        
        return CommandResponse(
            success=success,
            command=command,
            game_data=self.get_ai_context(),
            game_ended=game_ended,
            error_message=error_message,
            timestamp=datetime.now()
        )
    
    def get_frontend_response(self, message: str = "") -> GameResponse:
        """
        Get a standardized response for frontend using Pydantic models
        """
        return GameResponse(
            success=True,
            data=self.get_ai_context(),
            message=message or self.display_message,
            timestamp=datetime.now()
        )
    
    def set_output_mode(self, mode: str):
        '''
        Change the output mode (console/web)
        '''
        if mode not in ['console', 'web']:
            raise ValueError("Output mode must be 'console' or 'web'")
        self.output_mode = mode
    
    def display(self, message: str = ""):
        '''
        Universal display method that works for both console and web
        '''
        if message:
            self.display_message = message
        
        if self.output_mode == 'console':
            self.render_console()
        # For web mode, the message will be included in the next API response
        
        return self.get_api_state() if self.output_mode == 'web' else None

    def check_game_over(self):
        '''
        Check if the game is over (no valid moves left)
        '''
        for y in range(self.size_y):
            for x in range(self.size_x):
                if self.board[y][x] == 0:
                    return False  # Found an empty cell
                if x < self.size_x - 1 and self.board[y][x] == self.board[y][x + 1]:
                    return False  # Found a horizontal merge
                if y < self.size_y - 1 and self.board[y][x] == self.board[y + 1][x]:
                    return False  # Found a vertical merge
        self.over = True
        return True
    
    def check_win(self):
        '''
        Check if the player has won the game
        '''
        for row in self.board:
            if any(val >= self.win_value for val in row):
                self.won = True
                return True
        return False
    
    def handle_redo(self):
        '''
        Method to handle redo action
        '''
        # Check if redo is disabled
        if self.max_redo == 0:
            self.display_message = "Redo is disabled!"
            return False
        
        # Check if redo limit reached
        if self.redos_used >= self.max_redo and self.max_redo != -1:
            self.display_message = "No redos left!"
            return False
        
        # Check if there's history to redo to
        if len(self.history) <= 1:  # Need at least initial state + one move
            self.display_message = "No moves to redo!"
            return False
        
        # Remove current state from history and restore previous state
        self.history.pop()  # Remove current state
        if self.history:
            previous_state = self.history[-1]  # Get previous state (but keep it in history)
            self.restore_state(previous_state)
            
            # Increment session-persistent redo counter
            self.redos_used += 1

            self.display_message = f"Move undone! Redos used: {self.redos_used}/{self.max_redo if self.max_redo != -1 else '∞'}"
            return True
        
        return False
    
    def handle_hint(self):
        '''
        Method to handle hint action with AI integration
        '''
        # Check if hints are available
        if self.hints_used >= self.number_of_hints:
            self.display_message = "No hints left!"
            return False
        
        try:
            # Generate hint using AI system
            chat = AIChat()
            context = self.get_ai_context()
            ai_response = chat.chat(context)
            
            if ai_response.success:
                # Create hint history entry
                hint_entry = AIHintHistory(
                    hint_number=self.hints_used + 1,
                    requested_at=datetime.now(),
                    board_state_when_requested=copy.deepcopy(self.board),
                    hint_direction=ai_response.suggestion,
                    hint_reasoning=ai_response.reasoning,
                    was_followed=None,  # Will be updated when player makes next move
                    outcome_if_followed=None
                )
                self.hint_history.append(hint_entry)
                
                # Update counters and display message
                self.hints_used += 1
                hint_message = f"AI Hint ({self.number_of_hints - self.hints_used} left): {ai_response.reasoning}"
                if ai_response.suggestion:
                    hint_message = f"Suggested move: {ai_response.suggestion.upper()}. {ai_response.reasoning}"
                
                self.display_message = hint_message
                return True
            else:
                # AI failed, provide fallback
                self.hints_used += 1
                self.display_message = f"Hint service unavailable. Hints left: {self.number_of_hints - self.hints_used}"
                return True
                
        except Exception as e:
            # Fallback for any errors
            self.hints_used += 1
            self.display_message = f"Hint used but an error occurred. Hints left: {self.number_of_hints - self.hints_used}"
            print(f"Hint error: {e}")
            return True

    def handle_move(self, direction: str):
        '''
        Handle a move in the specified direction
        '''
        if direction not in ['up', 'down', 'left', 'right']:
            self.display_message = "Invalid direction!"
            return False

        # Store original board to check if move was valid
        original_board = [row[:] for row in self.board]
        
        # Execute the move
        points_earned, merge_occurred = self._execute_move(direction)
        
        # Check if board actually changed
        if self.board == original_board:
            self.display_message = "Invalid move! No tiles can move in that direction."
            return False
        
        # Valid move occurred - apply all changes
        self.moves_count += 1
        self.score += points_earned
        
        # Create move history entry
        move_entry = MoveHistoryEntry(
            move_number=self.moves_count,
            direction=direction,
            points_earned=points_earned,
            merge_occurred=merge_occurred,
            streak_after_move=self.streak,
            board_state=copy.deepcopy(self.board),
            timestamp=datetime.now()
        )
        self.move_history.append(move_entry)
        
        # Handle streak system
        if self.use_streak:
            if merge_occurred:
                self.streak += 1
                # Apply streak bonus to points earned
                streak_bonus = int(points_earned * (self.streak_bonus_percent / 100) * self.streak)
                self.score += streak_bonus
                self.state['streak_multiplier'] = 1 + (self.streak * self.streak_bonus_percent / 100)
                self.display_message = f"Move successful! Streak: {self.streak} (+{streak_bonus} bonus points)"
            else:
                # Move without merge breaks streak
                self.streak = 0
                self.state['streak_multiplier'] = 1
                self.display_message = "Move successful! (no merges, streak reset)"
        else:
            self.display_message = "Move successful!"
        
        # Add random tiles after successful move
        tiles_added = 0
        for _ in range(self.random_new_tiles):
            if self.add_random_tile():
                tiles_added += 1
            else:
                break  # Board is full

        # Save the state after the move is complete for future redo
        self.save_state_to_history()
        
        return True
    
    def _execute_move(self, direction: str):
        '''
        Execute the move logic and return points earned and merge status
        '''
        points_earned = 0
        merge_occurred = False
        
        if direction == 'left':
            points_earned, merge_occurred = self._move_left()
        elif direction == 'right':
            points_earned, merge_occurred = self._move_right()
        elif direction == 'up':
            points_earned, merge_occurred = self._move_up()
        elif direction == 'down':
            points_earned, merge_occurred = self._move_down()
        
        return points_earned, merge_occurred
    
    def _move_left(self):
        '''Move all tiles left and handle merging'''
        points_earned = 0
        merge_occurred = False
        
        for row_idx in range(self.size_y):
            row = self.board[row_idx]
            new_row, row_points, row_merged = self._process_line(row)
            self.board[row_idx] = new_row
            points_earned += row_points
            if row_merged:
                merge_occurred = True
        
        return points_earned, merge_occurred
    
    def _move_right(self):
        '''Move all tiles right and handle merging'''
        points_earned = 0
        merge_occurred = False
        
        for row_idx in range(self.size_y):
            row = self.board[row_idx]
            # Reverse, process, then reverse back for right movement
            reversed_row = row[::-1]
            new_row, row_points, row_merged = self._process_line(reversed_row)
            self.board[row_idx] = new_row[::-1]
            points_earned += row_points
            if row_merged:
                merge_occurred = True
        
        return points_earned, merge_occurred
    
    def _move_up(self):
        '''Move all tiles up and handle merging'''
        points_earned = 0
        merge_occurred = False
        
        for col_idx in range(self.size_x):
            # Extract column
            column = [self.board[row_idx][col_idx] for row_idx in range(self.size_y)]
            new_column, col_points, col_merged = self._process_line(column)
            # Put column back
            for row_idx in range(self.size_y):
                self.board[row_idx][col_idx] = new_column[row_idx]
            points_earned += col_points
            if col_merged:
                merge_occurred = True
        
        return points_earned, merge_occurred
    
    def _move_down(self):
        '''Move all tiles down and handle merging'''
        points_earned = 0
        merge_occurred = False
        
        for col_idx in range(self.size_x):
            # Extract column
            column = [self.board[row_idx][col_idx] for row_idx in range(self.size_y)]
            # Reverse, process, then reverse back for down movement
            reversed_column = column[::-1]
            new_column, col_points, col_merged = self._process_line(reversed_column)
            new_column = new_column[::-1]
            # Put column back
            for row_idx in range(self.size_y):
                self.board[row_idx][col_idx] = new_column[row_idx]
            points_earned += col_points
            if col_merged:
                merge_occurred = True
        
        return points_earned, merge_occurred
    
    def _process_line(self, line):
        '''
        Process a single line (row or column) for movement and merging
        Returns: (new_line, points_earned, merge_occurred)
        '''
        # Remove zeros (compress line)
        non_zero = [x for x in line if x != 0]
        
        if len(non_zero) == 0:
            return line, 0, False  # No tiles to move
        
        points_earned = 0
        merge_occurred = False
        result = []
        
        # Apply merge strategy based on configuration
        if self.merge_strategy == 'standard':
            result, points_earned, merge_occurred = self._merge_standard(non_zero)
        elif self.merge_strategy == 'reverse':
            result, points_earned, merge_occurred = self._merge_reverse(non_zero)
        else:
            # Default to standard if unknown strategy
            result, points_earned, merge_occurred = self._merge_standard(non_zero)
        
        # Pad with zeros to original length
        while len(result) < len(line):
            result.append(0)
        
        return result, points_earned, merge_occurred
    
    def _merge_reverse(self, tiles):
        '''
        Reverse merge strategy: merge tiles towards direction
        Example: [2,2,2] -> [4,2,0] (first two 2s merge, towards movement direction)
        This processes from left to right, prioritizing merges towards the movement direction
        '''
        if len(tiles) == 0:
            return [], 0, False
        
        result = []
        points_earned = 0
        merge_occurred = False
        i = 0
        
        while i < len(tiles):
            if i + 1 < len(tiles) and tiles[i] == tiles[i + 1]:
                # Merge these two tiles
                merged_value = tiles[i] + tiles[i + 1]
                result.append(merged_value)
                points_earned += merged_value
                merge_occurred = True
                i += 2  # Skip both merged tiles
                # Continue processing remaining tiles for independent merges
            else:
                # No merge possible, just move the tile
                result.append(tiles[i])
                i += 1
        
        # Handle secondary merge (whether merged tiles can merge again in same move)
        # Only applies when allow_secondary_merge is True
        if self.allow_secondary_merge and merge_occurred and len(result) > 1:
            # Recursively apply reverse merging
            secondary_result, secondary_points, secondary_merged = self._merge_reverse(result)
            if secondary_merged:
                return secondary_result, points_earned + secondary_points, True
        
        return result, points_earned, merge_occurred
    
    def _merge_standard(self, tiles):
        '''
        Standard merge strategy: merge tiles away from direction
        Example: [2,2,2] -> [2,4,0] (last two 2s merge, away from movement direction)
        This processes from right to left, prioritizing merges away from the movement direction
        '''
        if len(tiles) == 0:
            return [], 0, False
        
        result = []
        points_earned = 0
        merge_occurred = False
        i = len(tiles) - 1  # Start from the end
        
        while i >= 0:
            if i - 1 >= 0 and tiles[i] == tiles[i - 1]:
                # Merge these two tiles (current and previous)
                merged_value = tiles[i] + tiles[i - 1]
                result.insert(0, merged_value)  # Insert at beginning
                points_earned += merged_value
                merge_occurred = True
                i -= 2  # Skip both merged tiles
                # Continue processing remaining tiles for independent merges
            else:
                # No merge possible, just move the tile
                result.insert(0, tiles[i])  # Insert at beginning
                i -= 1
        
        # Handle secondary merge (whether merged tiles can merge again in same move)
        # Only applies when allow_secondary_merge is True
        if self.allow_secondary_merge and merge_occurred and len(result) > 1:
            # Recursively apply standard merging
            secondary_result, secondary_points, secondary_merged = self._merge_standard(result)
            if secondary_merged:
                return secondary_result, points_earned + secondary_points, True
        
        return result, points_earned, merge_occurred

    def run_game(self):
        '''
        Run the game loop for console mode
        '''
        while True:
            # First, check for win or game over
            if self.check_win():
                self.display("Congratulations! You've reached the target tile!")
                break
            if self.check_game_over():
                self.display("No more valid moves! Game Over!")
                break
                
            # Display current game state
            self.display()
            
            # Get user input (only for console mode)
            if self.output_mode == 'console':
                command = input("Enter command (up, down, left, right, redo, hint, exit, restart): ").strip().lower()
                if command not in self.valid_commands:
                    self.display_message = "Invalid command! Please try again."
                    continue
                if command == 'exit':
                    print("Exiting game. Goodbye!")
                    break
                if command == 'restart':
                    print("Restarting game...")
                    self.init_game()
                    continue
                if command == 'redo':
                    self.handle_redo()
                elif command == 'hint':
                    self.handle_hint()
                elif command in ['up', 'down', 'left', 'right']:
                    self.handle_move(command)
            else:
                # For web mode, break the loop as this should be handled by API calls
                break

if __name__ == "__main__":
    # Example of running the game in console mode
    game = Game()
    game.set_output_mode('console')
    game.run_game()