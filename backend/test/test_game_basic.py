"""
Unit tests for basic Game class functionality
Tests initialization, configuration validation, and basic state management
"""

import unittest
import sys
import os

# Add parent directory to path to import game module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game import Game


class TestGameBasic(unittest.TestCase):
    """Test basic Game class functionality"""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create a basic game instance for testing
        self.game = Game({'initial_tiles': 0, 'random_new_tiles': 0}, test_mode=True)  # No random tiles for predictable testing
    
    def test_default_initialization(self):
        """Test that game initializes with default values correctly"""
        game = Game()
        
        # Check default configuration values
        self.assertEqual(game.size_x, 4)
        self.assertEqual(game.size_y, 4)
        self.assertEqual(game.win_value, 2048)
        self.assertEqual(game.new_tile_values, [2, 4])
        self.assertEqual(game.max_redo, 3)
        self.assertEqual(game.merge_strategy, 'standard')
        self.assertFalse(game.allow_secondary_merge)
        self.assertFalse(game.use_streak)
        self.assertEqual(game.streak_bonus_percent, 10)
        self.assertEqual(game.number_of_hints, 3)
        self.assertEqual(game.output_mode, 'console')
    
    def test_custom_configuration(self):
        """Test that custom configuration values are applied correctly"""
        config = {
            'size_x': 5,
            'size_y': 6,
            'win_value': 1024,
            'initial_tiles': 1,
            'random_new_tiles': 1,
            'new_tile_values': [2],
            'max_redo': 5,
            'merge_strategy': 'reverse',
            'allow_secondary_merge': True,
            'use_streak': True,
            'streak_bonus_percent': 15,
            'number_of_hints': 2,
            'output_mode': 'web'
        }
        
        game = Game(config, test_mode=True)
        
        self.assertEqual(game.size_x, 5)
        self.assertEqual(game.size_y, 6)
        self.assertEqual(game.win_value, 1024)
        self.assertEqual(game.new_tile_values, [2])
        self.assertEqual(game.max_redo, 5)
        self.assertEqual(game.merge_strategy, 'reverse')
        self.assertTrue(game.allow_secondary_merge)
        self.assertTrue(game.use_streak)
        self.assertEqual(game.streak_bonus_percent, 15)
        self.assertEqual(game.number_of_hints, 2)
        self.assertEqual(game.output_mode, 'web')
    
    def test_board_initialization(self):
        """Test that the board is initialized correctly"""
        # Test with no initial tiles
        game = Game({'initial_tiles': 0, 'random_new_tiles': 0}, test_mode=True)
        
        # Board should be empty (all zeros)
        expected_board = [[0, 0, 0, 0] for _ in range(4)]
        self.assertEqual(game.board, expected_board)
        
        # Test with custom board size
        config = {'size_x': 3, 'size_y': 5, 'initial_tiles': 0, 'random_new_tiles': 0}
        game = Game(config, test_mode=True)
        expected_board = [[0, 0, 0] for _ in range(5)]
        self.assertEqual(game.board, expected_board)
    
    def test_initial_state_values(self):
        """Test that initial state values are set correctly"""
        self.assertEqual(self.game.score, 0)
        self.assertEqual(self.game.streak, 0)
        self.assertEqual(self.game.moves_count, 0)
        self.assertEqual(self.game.hints_used, 0)
        self.assertEqual(self.game.redos_used, 0)
        self.assertFalse(self.game.over)
        self.assertFalse(self.game.won)
        self.assertEqual(self.game.display_message, "Game started!")
    
    def test_property_accessors(self):
        """Test that property accessors work correctly"""
        # Test score property
        self.game.score = 100
        self.assertEqual(self.game.score, 100)
        self.assertEqual(self.game.state['score'], 100)
        
        # Test streak property
        self.game.streak = 5
        self.assertEqual(self.game.streak, 5)
        self.assertEqual(self.game.state['streak'], 5)
        
        # Test moves_count property
        self.game.moves_count = 10
        self.assertEqual(self.game.moves_count, 10)
        self.assertEqual(self.game.state['moves_count'], 10)
        
        # Test boolean properties
        self.game.over = True
        self.assertTrue(self.game.over)
        self.assertTrue(self.game.state['over'])
        
        self.game.won = True
        self.assertTrue(self.game.won)
        self.assertTrue(self.game.state['won'])
    
    def test_state_management(self):
        """Test state copy and restore functionality"""
        # Modify some state values
        self.game.score = 500
        self.game.streak = 3
        self.game.moves_count = 15
        self.game.board[0][0] = 4
        self.game.board[1][1] = 8
        
        # Get state copy
        state_copy = self.game.get_state_copy()
        
        # Verify copy contains correct values
        self.assertEqual(state_copy['score'], 500)
        self.assertEqual(state_copy['streak'], 3)
        self.assertEqual(state_copy['moves_count'], 15)
        self.assertEqual(state_copy['board'][0][0], 4)
        self.assertEqual(state_copy['board'][1][1], 8)
        
        # Modify original state
        self.game.score = 1000
        self.game.streak = 7
        self.game.board[0][0] = 16
        
        # Restore from copy
        self.game.restore_state(state_copy)
        
        # Verify state was restored
        self.assertEqual(self.game.score, 500)
        self.assertEqual(self.game.streak, 3)
        self.assertEqual(self.game.moves_count, 15)
        self.assertEqual(self.game.board[0][0], 4)
        self.assertEqual(self.game.board[1][1], 8)
    
    def test_history_functionality(self):
        """Test save and restore state to history"""
        # Initial state should be saved in history during init
        self.assertEqual(len(self.game.history), 1)
        
        # Modify state and save to history
        self.game.score = 100
        self.game.save_state_to_history()
        self.assertEqual(len(self.game.history), 2)
        
        # Modify state again
        self.game.score = 200
        self.game.streak = 2
        
        # Verify current state
        self.assertEqual(self.game.score, 200)
        self.assertEqual(self.game.streak, 2)
        
        # Check that history contains the correct previous state
        previous_state = self.game.history[-1]  # Most recent history entry
        self.assertEqual(previous_state['score'], 100)
        self.assertEqual(previous_state['streak'], 0)  # Should be initial value
    
    def test_output_mode_management(self):
        """Test output mode setting and validation"""
        # Test setting valid modes
        self.game.set_output_mode('console')
        self.assertEqual(self.game.output_mode, 'console')
        
        self.game.set_output_mode('web')
        self.assertEqual(self.game.output_mode, 'web')
        
        # Test setting invalid mode
        with self.assertRaises(ValueError):
            self.game.set_output_mode('invalid_mode')


class TestGameValidation(unittest.TestCase):
    """Test configuration validation"""
    
    def test_valid_configurations(self):
        """Test that valid configurations pass validation"""
        valid_configs = [
            {'size_x': 3, 'size_y': 3},  # Minimum size
            {'size_x': 12, 'size_y': 12},  # Maximum size
            {'size_x': 4, 'size_y': 5},  # Rectangular board
            {'win_value': 4, 'new_tile_values': [2]},  # Minimum win value, must also have new_tile_values smaller than win_value
            {'win_value': 10000},  # Maximum win value
            {'initial_tiles': 1, 'size_x': 3, 'size_y': 3},  # Minimum initial tiles
            {'new_tile_values': [1]},  # Minimum tile value
            {'new_tile_values': [10]},  # Maximum tile value
            {'max_redo': 0},  # Disabled redo
            {'max_redo': -1},  # Unlimited redo
            {'number_of_hints': 0},  # No hints
            {'number_of_hints': 5},  # Maximum hints
            {'use_streak': True, 'streak_bonus_percent': 0},  # Minimum streak bonus
            {'use_streak': True, 'streak_bonus_percent': 100},  # Maximum streak bonus
        ]
        
        for config in valid_configs:
            config.update({'initial_tiles': 1, 'random_new_tiles': 1})  # Add required fields
            try:
                game = Game(config, test_mode=False)  # test_mode=False to enable validation checks
                # If we get here, validation passed
                self.assertTrue(True)
            except ValueError as e:
                self.fail(f"Valid config {config} failed validation: {e}")
    
    def test_invalid_board_sizes(self):
        """Test that invalid board sizes are rejected"""
        invalid_configs = [
            {'size_x': 2},  # Too small
            {'size_y': 2},  # Too small
            {'size_x': 13},  # Too large
            {'size_y': 13},  # Too large
            {'size_x': 2, 'size_y': 4},  # Total cells < 9
        ]
        
        for config in invalid_configs:
            config.update({'initial_tiles': 1, 'random_new_tiles': 1})
            with self.assertRaises(ValueError):
                Game(config, test_mode=False)  # test_mode=False to enable validation checks
    
    def test_invalid_win_values(self):
        """Test that invalid win values are rejected"""
        invalid_configs = [
            {'win_value': 3},  # Too small
            {'win_value': 10001},  # Too large
        ]
        
        for config in invalid_configs:
            config.update({'initial_tiles': 1, 'random_new_tiles': 1})
            with self.assertRaises(ValueError):
                Game(config, test_mode=False)  # test_mode=False to enable validation checks
    
    def test_invalid_tile_configurations(self):
        """Test that invalid tile configurations are rejected"""
        invalid_configs = [
            {'initial_tiles': 0},  # Too few initial tiles (minimum 1)
            {'size_x': 3, 'size_y': 3, 'initial_tiles': 5},  # Too many initial tiles (max 4 for 3x3)
            {'new_tile_values': []},  # Empty tile values
            {'new_tile_values': [0]},  # Invalid tile value (too small)
            {'new_tile_values': [11]},  # Invalid tile value (too large)
            {'random_new_tiles': 0},  # Too few new tiles per move
            {'size_x': 3, 'size_y': 3, 'random_new_tiles': 5},  # Too many new tiles
            {'win_value': 4, 'new_tile_values': [4]},  # Tile value >= win condition
        ]
        
        for config in invalid_configs:
            if 'initial_tiles' not in config:
                config['initial_tiles'] = 1
            if 'random_new_tiles' not in config:
                config['random_new_tiles'] = 1
            with self.assertRaises(ValueError):
                Game(config, test_mode=False)  # test_mode=False to enable validation checks
    
    def test_invalid_game_settings(self):
        """Test that invalid game settings are rejected"""
        invalid_configs = [
            {'max_redo': -2},  # Invalid redo setting
            {'number_of_hints': -1},  # Too few hints
            {'number_of_hints': 6},  # Too many hints
            {'use_streak': True, 'streak_bonus_percent': -1},  # Invalid streak bonus
            {'use_streak': True, 'streak_bonus_percent': 101},  # Invalid streak bonus
        ]
        
        for config in invalid_configs:
            config.update({'initial_tiles': 1, 'random_new_tiles': 1})
            with self.assertRaises(ValueError):
                Game(config, test_mode=False)  # test_mode=False to enable validation checks


if __name__ == '__main__':
    unittest.main()
