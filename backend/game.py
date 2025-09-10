'''
Core module for the 2048 game logic
'''

import random
from typing import Optional

class Game:
    def __init__(self, config: Optional[dict] = None):
        '''
        Initialize the game state
        If no config is provided, use default settings
        '''
        # Initialize config first
        self.config = config or {}
        
        # configurable parameters (set before board initialization)
        self.size_x = self.config.get('size_x', 4)
        self.size_y = self.config.get('size_y', 4)
        self.win_value = self.config.get('win_value', 2048)
        
        # Initialize board with correct dimensions
        self.board = [[0] * self.size_x for _ in range(self.size_y)]
        self.score = 0
        self.streak = 0
        self.streak_multiplier = 1
        self.over = False
        self.won = False
        self.history = []  # to store previous states
        self.display_message = ""

        # configurable parameters
        self.size_x = self.config.get('size_x', 4)
        self.size_y = self.config.get('size_y', 4)
        self.win_value = self.config.get('win_value', 2048)
        self.initial_tiles = self.config.get('initial_tiles', random.randint(2, 4)) # number of initial tiles, default random between 2 and 4
        self.random_new_tiles = self.config.get('random_new_tiles', random.randint(2, 4)) # number of new tiles per move, default random between 2 and 4
        self.new_tile_values = self.config.get('new_tile_values', [2, 4])
        self.max_redo = self.config.get('max_redo', 3)  # max number of redo allowed, 0 means no redo, -1 means infinite
        
        # advanced settings
        # merge strateg is one of 'standard', 'reverse'
        # 'standard': prioririze merging cells away from the direction, i.e. [2,2,2] -> left -> [2,4,0]
        # 'reverse': prioririze merging cells towards the direction, i.e. [2,2,2] -> left -> [4,2,0]
        self.merge_strategy = self.config.get('merge_strategy', 'standard')
        self.allow_secondary_merge = self.config.get('allow_secondary_merge', False) # allow multiple merges in one move, e.g. [2,2,2,2] -> left -> [8,0,0,0]
        self.use_streak = self.config.get('use_streak', False) # whether to use streak system
        self.streak_bonus_percent = self.config.get('streak_bonus_percent', 10) # percentage bonus per streak level (default 10%)
        self.number_of_hints = self.config.get('number_of_hints', 3) # number of AI hint that can be requested per game
        
        # Additional state tracking
        self.hints_used = 0  # track how many hints have been used
        self.redos_used = 0  # track how many redos have been used
        self.moves_count = 0  # track total moves made

        # set output mode: 'console' or 'web'
        self.output_mode = self.config.get('output_mode', 'console')

        # Initialize the game
        self.init_game()

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
        if not (1 <= self.initial_tiles <= self.size_x * self.size_y // 2):
            raise ValueError("initial_tiles must be at least 1 and at most half of the board size")
        
        # check new tile values constraints
        if not all(v in range(1, 11) for v in self.new_tile_values):
            raise ValueError("new_tile_values must be between 1 and 10")
        if len(self.new_tile_values) == 0:
            raise ValueError("new_tile_values must contain at least one value")
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
        
        # Clear the board
        self.board = [[0] * self.size_x for _ in range(self.size_y)]
        
        # Add initial tiles
        for _ in range(self.initial_tiles):
            self.add_random_tile()
        
        # Reset game state
        self.score = 0
        self.streak = 0
        self.over = False
        self.won = False
        self.history = []
        self.hints_used = 0
        self.redos_used = 0
        self.moves_count = 0
        self.display_message = "Game started!"
    
    def add_random_tile(self):
        '''
        Add a random tile to an empty cell on the board
        '''
        empty_cells = []
        for y in range(self.size_y):
            for x in range(self.size_x):
                if self.board[y][x] == 0:
                    empty_cells.append((y, x))
        
        if empty_cells:
            y, x = random.choice(empty_cells)
            self.board[y][x] = random.choice(self.new_tile_values)
            return True
        return False