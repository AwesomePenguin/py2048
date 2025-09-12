"""
Unit tests for streak system, redo functionality, and advanced game features
"""

import unittest
import sys
import os

# Add parent directory to path to import game module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game import Game
from models import TestGameConfigurationRequest


class TestStreakSystem(unittest.TestCase):
    """Test streak scoring system"""
    
    def setUp(self):
        """Set up test fixtures"""
        config = TestGameConfigurationRequest(
            initial_tiles=0,
            random_new_tiles=0,
            streak_enabled=True,
            streak_bonus_percent=10
        )
        self.game = Game(config, test_mode=True)
    
    def set_board(self, board_data):
        """Helper method to set board state for testing"""
        for y in range(len(board_data)):
            for x in range(len(board_data[y])):
                self.game.board[y][x] = board_data[y][x]
    
    def test_streak_with_merge(self):
        """Test that streak increases when merges occur"""
        # Set up board for merge
        self.set_board([
            [2, 2, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0]
        ])
        
        # Perform move that results in merge
        result = self.game.handle_move('left')
        
        self.assertTrue(result)
        self.assertEqual(self.game.streak, 1)
        self.assertEqual(self.game.state['streak_multiplier'], 1.1)  # 1 + (1 * 10%)
        
        # Base points = 4, streak bonus = 4 * 10% * 1 = 0.4 -> 0 (int)
        # Total score = 4 + 0 = 4
        self.assertEqual(self.game.score, 4)
    
    def test_streak_accumulation(self):
        """Test that streaks accumulate over multiple moves with merges"""
        # First merge
        self.set_board([
            [2, 2, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0]
        ])
        
        self.game.handle_move('left')
        self.assertEqual(self.game.streak, 1)
        first_score = self.game.score
        
        # Second merge (modify board for another merge)
        self.set_board([
            [4, 0, 0, 0],
            [4, 4, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0]
        ])
        
        self.game.handle_move('left')
        self.assertEqual(self.game.streak, 2)
        self.assertEqual(self.game.state['streak_multiplier'], 1.2)  # 1 + (2 * 10%)
        
        # Base points = 8, streak bonus = 8 * 10% * 2 = 1.6 -> 1 (int)
        # Total added = 8 + 1 = 9
        expected_score = first_score + 9
        self.assertEqual(self.game.score, expected_score)
    
    def test_streak_broken_by_move_without_merge(self):
        """Test that streak is broken when a move doesn't result in a merge"""
        # Build up a streak first
        self.set_board([
            [2, 2, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0]
        ])
        
        self.game.handle_move('left')
        self.assertEqual(self.game.streak, 1)
        
        # Now make a move without merge
        self.set_board([
            [4, 0, 0, 0],
            [2, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0]
        ])
        
        self.game.handle_move('right')  # Move tiles right, no merge
        
        self.assertEqual(self.game.streak, 0)  # Streak should be broken
        self.assertEqual(self.game.state['streak_multiplier'], 1)  # Reset to 1
        self.assertIn("streak reset", self.game.display_message)
    
    def test_streak_disabled(self):
        """Test that streak system can be disabled"""
        config = TestGameConfigurationRequest(
            initial_tiles=0,
            random_new_tiles=0,
            streak_enabled=False
        )
        game = Game(config, test_mode=True)
        
        # Set up board for merge
        game.board[0] = [2, 2, 0, 0]
        
        game.handle_move('left')
        
        # Streak should remain 0 when disabled
        self.assertEqual(game.streak, 0)
        self.assertEqual(game.state['streak_multiplier'], 1)
        
        # Score should be just the base points (4)
        self.assertEqual(game.score, 4)
    
    def test_custom_streak_bonus(self):
        """Test custom streak bonus percentage"""
        config = TestGameConfigurationRequest(
            initial_tiles=0,
            random_new_tiles=0,
            streak_enabled=True,
            streak_bonus_percent=25  # 25% bonus instead of 10%
        )
        game = Game(config, test_mode=True)
        
        # Set up board for merge
        game.board[0] = [2, 2, 0, 0]
        
        game.handle_move('left')
        
        self.assertEqual(game.streak, 1)
        self.assertEqual(game.state['streak_multiplier'], 1.25)  # 1 + (1 * 25%)
        
        # Base points = 4, streak bonus = 4 * 25% * 1 = 1
        # Total score = 4 + 1 = 5
        self.assertEqual(game.score, 5)


class TestRedoFunctionality(unittest.TestCase):
    """Test redo/undo functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        config = TestGameConfigurationRequest(
            initial_tiles=0,
            random_new_tiles=0,
            max_redo=3
        )
        self.game = Game(config, test_mode=True)
    
    def set_board(self, board_data):
        """Helper method to set board state"""
        for y in range(len(board_data)):
            for x in range(len(board_data[y])):
                self.game.board[y][x] = board_data[y][x]
    
    def test_redo_after_move(self):
        """Test redo functionality after a valid move"""
        # Set initial board state
        initial_board = [
            [2, 2, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0]
        ]
        self.set_board(initial_board)
        # Save the state after setting up the board so redo can restore to this state
        self.game.save_state_to_history()
        initial_score = self.game.score
        initial_moves = self.game.moves_count
        
        # Make a move
        self.game.handle_move('left')
        
        # Verify move was successful
        self.assertNotEqual(self.game.board, initial_board)
        self.assertGreater(self.game.score, initial_score)
        self.assertEqual(self.game.moves_count, initial_moves + 1)
        
        # Perform redo
        result = self.game.handle_redo()
        
        self.assertTrue(result)
        self.assertEqual(self.game.board, initial_board)
        self.assertEqual(self.game.score, initial_score)
        self.assertEqual(self.game.moves_count, initial_moves)
        self.assertEqual(self.game.redos_used, 1)
    
    def test_redo_limit(self):
        """Test that redo is limited by max_redo setting"""
        # Set up for multiple moves
        for i in range(4):  # Try to use more redos than allowed
            self.set_board([
                [2, 2, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0]
            ])
            self.game.handle_move('left')
            
            if i < 3:  # Within limit
                result = self.game.handle_redo()
                self.assertTrue(result)
            else:  # Exceeds limit
                result = self.game.handle_redo()
                print(f'redo attempts {self.game.redos_used}')
                self.assertFalse(result)
                self.assertIn("No redos left", self.game.display_message)
    
    def test_redo_disabled(self):
        """Test redo when disabled (max_redo = 0)"""
        config = TestGameConfigurationRequest(
            initial_tiles=0,
            random_new_tiles=0,
            max_redo=0
        )
        game = Game(config, test_mode=True)
        
        # Set up and make a move
        game.board[0] = [2, 2, 0, 0]
        game.handle_move('left')
        
        # Try redo - should fail
        result = game.handle_redo()
        self.assertFalse(result)
        self.assertIn("Redo is disabled", game.display_message)
    
    def test_redo_unlimited(self):
        """Test unlimited redo (max_redo = -1)"""
        config = TestGameConfigurationRequest(
            initial_tiles=0,
            random_new_tiles=0,
            max_redo=-1
        )
        game = Game(config, test_mode=True)
        
        # Make several moves and redos
        for i in range(10):  # Much more than typical limit
            game.board[0] = [2, 2, 0, 0]
            game.handle_move('left')
            result = game.handle_redo()
            self.assertTrue(result)
    
    def test_redo_without_moves(self):
        """Test redo when no moves have been made"""
        # Try redo immediately after initialization
        result = self.game.handle_redo()
        
        self.assertFalse(result)
        self.assertIn("No moves to redo", self.game.display_message)
    
    def test_redo_state_consistency(self):
        """Test that redo restores complete game state"""
        # Set up initial state
        self.set_board([
            [2, 4, 0, 0],
            [8, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0]
        ])
        # Save the state after setting up the board so redo can restore to this state
        self.game.save_state_to_history()
        
        initial_state = {
            'board': [row[:] for row in self.game.board],
            'score': self.game.score,
            'streak': self.game.streak,
            'moves_count': self.game.moves_count,
            'over': self.game.over,
            'won': self.game.won
        }
        
        # Make a move that changes multiple state values
        self.game.handle_move('right')
        
        # Verify state changed
        self.assertNotEqual(self.game.board, initial_state['board'])
        
        # Redo and verify complete state restoration
        self.game.handle_redo()
        
        self.assertEqual(self.game.board, initial_state['board'])
        self.assertEqual(self.game.score, initial_state['score'])
        self.assertEqual(self.game.streak, initial_state['streak'])
        self.assertEqual(self.game.moves_count, initial_state['moves_count'])
        self.assertEqual(self.game.over, initial_state['over'])
        self.assertEqual(self.game.won, initial_state['won'])


class TestHintSystem(unittest.TestCase):
    """Test hint system functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        config = TestGameConfigurationRequest(
            initial_tiles=0,
            random_new_tiles=0,
            number_of_hints=3
        )
        self.game = Game(config, test_mode=True)
    
    def test_hint_usage(self):
        """Test basic hint usage and counting"""
        # Use a hint
        result = self.game.handle_hint()
        
        self.assertTrue(result)
        self.assertEqual(self.game.hints_used, 1)
        self.assertIn("Hint used", self.game.display_message)
    
    def test_hint_limit(self):
        """Test that hints are limited by number_of_hints setting"""
        # Use all available hints
        for i in range(3):
            result = self.game.handle_hint()
            self.assertTrue(result)
            self.assertEqual(self.game.hints_used, i + 1)
        
        # Try to use one more hint - should fail
        result = self.game.handle_hint()
        self.assertFalse(result)
        self.assertIn("No hints left", self.game.display_message)
    
    def test_hints_disabled(self):
        """Test when hints are disabled (number_of_hints = 0)"""
        config = TestGameConfigurationRequest(
            initial_tiles=0,
            random_new_tiles=0,
            number_of_hints=0
        )
        game = Game(config, test_mode=True)
        
        # Try to use hint - should fail immediately
        result = game.handle_hint()
        self.assertFalse(result)
        self.assertIn("No hints left", game.display_message)


class TestRandomTileGeneration(unittest.TestCase):
    """Test random tile generation and board management"""
    
    def setUp(self):
        """Set up test fixtures"""
        config = TestGameConfigurationRequest(
            initial_tiles=0,
            random_new_tiles=1,
            new_tile_values=[2]  # Predictable tile value
        )
        self.game = Game(config, test_mode=True)
    
    def test_add_random_tile_success(self):
        """Test successful random tile addition"""
        # Ensure board has empty space
        self.game.board[0][0] = 0
        
        result = self.game.add_random_tile()
        
        self.assertTrue(result)
        # Check that a tile was added somewhere
        total_tiles = sum(1 for row in self.game.board for cell in row if cell != 0)
        self.assertEqual(total_tiles, 1)
    
    def test_add_random_tile_full_board(self):
        """Test random tile addition when board is full"""
        # Fill the entire board
        for y in range(4):
            for x in range(4):
                self.game.board[y][x] = 2
        
        result = self.game.add_random_tile()
        
        self.assertFalse(result)  # Should fail when board is full
    
    def test_specific_tile_values(self):
        """Test that tiles are generated with correct values"""
        config = TestGameConfigurationRequest(
            initial_tiles=0,
            random_new_tiles=1,
            new_tile_values=[4, 8]  # Only 4s and 8s
        )
        game = Game(config, test_mode=True)
        
        # Add several tiles and check their values
        added_values = []
        for _ in range(10):
            game.add_random_tile()
            for row in game.board:
                for cell in row:
                    if cell != 0 and cell not in added_values:
                        added_values.append(cell)
        
        # All added values should be in the allowed set
        for value in added_values:
            self.assertIn(value, [4, 8])


class TestDisplayAndAPI(unittest.TestCase):
    """Test display methods and API response generation"""
    
    def setUp(self):
        """Set up test fixtures"""
        config = TestGameConfigurationRequest(
            initial_tiles=0,
            random_new_tiles=0
        )
        self.game = Game(config, test_mode=True)
    
    def test_get_display_data(self):
        """Test display data generation"""
        # Set up some game state
        self.game.score = 100
        self.game.streak = 2
        self.game.moves_count = 5
        self.game.hints_used = 1
        self.game.redos_used = 1
        
        data = self.game.get_display_data()
        
        # Verify all expected fields are present
        expected_fields = [
            'board', 'score', 'streak', 'streak_multiplier', 'moves_count',
            'hints_used', 'redos_used', 'redos_remaining', 'hints_remaining',
            'game_over', 'game_won', 'display_message', 'board_size',
            'win_value', 'streak_enabled'
        ]
        
        for field in expected_fields:
            self.assertIn(field, data)
        
        # Verify some specific values
        self.assertEqual(data['score'], 100)
        self.assertEqual(data['streak'], 2)
        self.assertEqual(data['moves_count'], 5)
        self.assertEqual(data['hints_remaining'], 2)  # 3 total - 1 used
        self.assertEqual(data['redos_remaining'], 2)  # 3 total - 1 used
    
    def test_get_api_state(self):
        """Test API state generation for web responses"""
        # Set up game state
        self.game.score = 200
        self.game.streak = 1
        self.game.display_message = "Test message"
        
        api_state = self.game.get_api_state()
        
        # Verify structure
        self.assertIn('game_state', api_state)
        self.assertIn('resources', api_state)
        self.assertIn('config', api_state)
        self.assertIn('message', api_state)
        self.assertIn('last_updated', api_state)
        
        # Verify nested structure
        self.assertIn('board', api_state['game_state'])
        self.assertIn('score', api_state['game_state'])
        self.assertIn('status', api_state['game_state'])
        
        self.assertIn('hints', api_state['resources'])
        self.assertIn('redos', api_state['resources'])
        
        # Verify values
        self.assertEqual(api_state['game_state']['score'], 200)
        self.assertEqual(api_state['message'], "Test message")
    
    def test_output_mode_switching(self):
        """Test switching between console and web output modes"""
        # Test console mode
        self.game.set_output_mode('console')
        self.assertEqual(self.game.output_mode, 'console')
        
        # Test web mode
        self.game.set_output_mode('web')
        self.assertEqual(self.game.output_mode, 'web')
        
        # Test invalid mode
        with self.assertRaises(ValueError):
            self.game.set_output_mode('invalid')
    
    def test_json_response_generation(self):
        """Test JSON response generation for web API"""
        self.game.set_output_mode('web')
        self.game.score = 150
        
        json_response = self.game.get_json_response()
        
        # Should be valid JSON
        import json
        data = json.loads(json_response)
        
        # Verify key fields
        self.assertIn('score', data)
        self.assertIn('config', data)
        self.assertIn('available_commands', data)
        self.assertIn('timestamp', data)
        
        self.assertEqual(data['score'], 150)


if __name__ == '__main__':
    unittest.main()
