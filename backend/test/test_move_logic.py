"""
Unit tests for move logic and merge strategies
Tests the core 2048 game mechanics
"""

import unittest
import sys
import os

# Add parent directory to path to import game module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game import Game
from models import TestGameConfigurationRequest, GameConfigurationRequest


class TestMoveLogic(unittest.TestCase):
    """Test move logic and board manipulation"""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create game with no random elements for predictable testing
        config = TestGameConfigurationRequest(initial_tiles=0, random_new_tiles=0)
        self.game = Game(config, test_mode=True)
    
    def set_board(self, board_data):
        """Helper method to set board state for testing"""
        for y in range(len(board_data)):
            for x in range(len(board_data[y])):
                self.game.board[y][x] = board_data[y][x]
    
    def test_move_left_basic(self):
        """Test basic left movement without merging"""
        # Set up board with tiles that should slide left
        self.set_board([
            [0, 2, 0, 4],
            [0, 0, 8, 0],
            [2, 0, 0, 0],
            [0, 0, 0, 16]
        ])
        
        result = self.game.handle_move('left')
        
        self.assertTrue(result)  # Move should be successful
        expected_board = [
            [2, 4, 0, 0],
            [8, 0, 0, 0],
            [2, 0, 0, 0],
            [16, 0, 0, 0]
        ]
        self.assertEqual(self.game.board, expected_board)
    
    def test_move_right_basic(self):
        """Test basic right movement without merging"""
        self.set_board([
            [2, 0, 4, 0],
            [0, 8, 0, 0],
            [0, 0, 0, 2],
            [16, 0, 0, 0]
        ])
        
        result = self.game.handle_move('right')
        
        self.assertTrue(result)
        expected_board = [
            [0, 0, 2, 4],
            [0, 0, 0, 8],
            [0, 0, 0, 2],
            [0, 0, 0, 16]
        ]
        self.assertEqual(self.game.board, expected_board)
    
    def test_move_up_basic(self):
        """Test basic up movement without merging"""
        self.set_board([
            [0, 0, 2, 0],
            [2, 0, 0, 0],
            [0, 8, 0, 4],
            [0, 0, 0, 0]
        ])
        
        result = self.game.handle_move('up')
        
        self.assertTrue(result)
        expected_board = [
            [2, 8, 2, 4],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0]
        ]
        self.assertEqual(self.game.board, expected_board)
    
    def test_move_down_basic(self):
        """Test basic down movement without merging"""
        self.set_board([
            [2, 8, 0, 4],
            [0, 0, 2, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0]
        ])
        
        result = self.game.handle_move('down')
        
        self.assertTrue(result)
        expected_board = [
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [2, 8, 2, 4]
        ]
        self.assertEqual(self.game.board, expected_board)
    
    def test_invalid_move(self):
        """Test that invalid moves are rejected"""
        # Set up board where no movement is possible
        self.set_board([
            [2, 4, 8, 16],
            [4, 8, 16, 32],
            [8, 16, 32, 64],
            [16, 32, 64, 128]
        ])
        
        # Try to move left - should fail because no tiles can move
        result = self.game.handle_move('left')
        self.assertFalse(result)
        self.assertIn("Invalid move", self.game.display_message)
    
    def test_move_with_merging_left(self):
        """Test left movement with tile merging"""
        self.set_board([
            [2, 2, 4, 4],
            [8, 8, 0, 0],
            [2, 4, 2, 0],
            [0, 0, 0, 0]
        ])
        
        result = self.game.handle_move('left')
        
        self.assertTrue(result)
        expected_board = [
            [4, 8, 0, 0],  # 2+2=4, 4+4=8
            [16, 0, 0, 0],  # 8+8=16
            [2, 4, 2, 0],   # No merging possible
            [0, 0, 0, 0]
        ]
        self.assertEqual(self.game.board, expected_board)
        
        # Check score was updated correctly
        expected_score = 4 + 8 + 16  # Points from merges
        self.assertEqual(self.game.score, expected_score)
    
    def test_move_with_merging_right(self):
        """Test right movement with tile merging"""
        self.set_board([
            [2, 2, 4, 4],
            [0, 0, 8, 8],
            [0, 2, 4, 2],
            [0, 0, 0, 0]
        ])
        
        result = self.game.handle_move('right')
        
        self.assertTrue(result)
        expected_board = [
            [0, 0, 4, 8],  # 2+2=4, 4+4=8
            [0, 0, 0, 16], # 8+8=16
            [0, 2, 4, 2],  # No merging possible
            [0, 0, 0, 0]
        ]
        self.assertEqual(self.game.board, expected_board)
    
    def test_multiple_merges_standard_strategy(self):
        """Test multiple merges with standard strategy"""
        # Test with allow_secondary_merge = False (default)
        self.set_board([
            [2, 2, 2, 2],  # Should become [4, 4, 0, 0] with standard strategy
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0]
        ])
        
        result = self.game.handle_move('left')
        
        self.assertTrue(result)
        expected_board = [
            [4, 4, 0, 0],  # Two separate merges: (2,2)->4 and (2,2)->4
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0]
        ]
        self.assertEqual(self.game.board, expected_board)
    
    def test_secondary_merge_enabled(self):
        """Test secondary merges when allow_secondary_merge is True"""
        config = TestGameConfigurationRequest(
            initial_tiles=0, 
            random_new_tiles=0,
            allow_secondary_merge=True
        )
        game = Game(config, test_mode=True)
        
        # Set board state
        for y in range(4):
            for x in range(4):
                game.board[y][x] = 0
        
        game.board[0] = [2, 2, 2, 2]  # Should become [8, 0, 0, 0] with secondary merge
        
        result = game.handle_move('left')
        
        self.assertTrue(result)
        expected_board = [
            [8, 0, 0, 0],  # (2,2)->4, (2,2)->4, then (4,4)->8
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0]
        ]
        self.assertEqual(game.board, expected_board)
    
    def test_reverse_merge_strategy(self):
        """Test reverse merge strategy"""
        config = TestGameConfigurationRequest(
            initial_tiles=0,
            random_new_tiles=0,
            merge_strategy='reverse'
        )
        game = Game(config, test_mode=True)
        
        # Set board state
        for y in range(4):
            for x in range(4):
                game.board[y][x] = 0
        
        game.board[0] = [2, 2, 2, 0]  # Should become [4, 2, 0, 0] with reverse strategy
        
        result = game.handle_move('left')
        
        self.assertTrue(result)
        expected_board = [
            [4, 2, 0, 0],  # First two 2s merge (reverse strategy)
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0]
        ]
        self.assertEqual(game.board, expected_board)
    
    def test_no_movement_possible(self):
        """Test detection of no valid moves"""
        # Create a board where no moves are possible
        self.set_board([
            [2, 4, 2, 4],
            [4, 2, 4, 2],
            [2, 4, 2, 4],
            [4, 2, 4, 2]
        ])
        
        # All moves should be invalid
        self.assertFalse(self.game.handle_move('left'))
        self.assertFalse(self.game.handle_move('right'))
        self.assertFalse(self.game.handle_move('up'))
        self.assertFalse(self.game.handle_move('down'))


class TestMergeStrategies(unittest.TestCase):
    """Test different merge strategies in isolation"""
    
    def setUp(self):
        """Set up test fixtures"""
        config = TestGameConfigurationRequest(initial_tiles=0, random_new_tiles=0)
        self.game = Game(config, test_mode=True)
    
    def test_merge_standard_basic(self):
        """Test standard merge strategy with basic cases"""
        # Test case 1: Simple merge
        result, points, merged = self.game._merge_standard([2, 2])
        self.assertEqual(result, [4])
        self.assertEqual(points, 4)
        self.assertTrue(merged)
        
        # Test case 2: No merge possible
        result, points, merged = self.game._merge_standard([2, 4])
        self.assertEqual(result, [2, 4])
        self.assertEqual(points, 0)
        self.assertFalse(merged)
        
        # Test case 3: Three tiles, one merge
        result, points, merged = self.game._merge_standard([2, 2, 4])
        self.assertEqual(result, [4, 4])
        self.assertEqual(points, 4)
        self.assertTrue(merged)
    
    def test_merge_reverse_basic(self):
        """Test reverse merge strategy"""
        # Test case 1: Three tiles with reverse strategy
        result, points, merged = self.game._merge_reverse([2, 2, 2])
        self.assertEqual(result, [4, 2])  # First two merge in reverse strategy
        self.assertEqual(points, 4)
        self.assertTrue(merged)
        
        # Test case 2: Four identical tiles
        result, points, merged = self.game._merge_reverse([2, 2, 2, 2])
        self.assertEqual(result, [4, 4])  # Two pairs merge
        self.assertEqual(points, 8)
        self.assertTrue(merged)
    
    def test_process_line_complete(self):
        """Test complete line processing with padding"""
        # Test left movement line processing
        original_line = [0, 2, 0, 2]
        result, points, merged = self.game._process_line(original_line)
        
        self.assertEqual(len(result), len(original_line))  # Same length
        self.assertEqual(result, [4, 0, 0, 0])  # Merged and padded
        self.assertEqual(points, 4)
        self.assertTrue(merged)
        
        # Test line with no movement needed
        original_line = [2, 4, 8, 16]
        result, points, merged = self.game._process_line(original_line)
        
        self.assertEqual(result, [2, 4, 8, 16])  # No change
        self.assertEqual(points, 0)
        self.assertFalse(merged)
    
    def test_empty_line_processing(self):
        """Test processing of empty lines"""
        original_line = [0, 0, 0, 0]
        result, points, merged = self.game._process_line(original_line)
        
        self.assertEqual(result, [0, 0, 0, 0])
        self.assertEqual(points, 0)
        self.assertFalse(merged)


class TestGameEndConditions(unittest.TestCase):
    """Test win and game over detection"""
    
    def setUp(self):
        """Set up test fixtures"""
        config = TestGameConfigurationRequest(initial_tiles=0, random_new_tiles=0)
        self.game = Game(config, test_mode=True)
    
    def test_win_condition_detection(self):
        """Test that win condition is detected correctly"""
        # Set up board with winning tile
        self.game.board[0][0] = 2048  # Default win value
        
        self.assertTrue(self.game.check_win())
        self.assertTrue(self.game.won)
        
        # Test with custom win value
        config = TestGameConfigurationRequest(win_target=1024, initial_tiles=0, random_new_tiles=0)
        game = Game(config, test_mode=True)
        game.board[1][1] = 1024
        
        self.assertTrue(game.check_win())
        self.assertTrue(game.won)
    
    def test_win_condition_not_met(self):
        """Test that win condition is not triggered prematurely"""
        # Set up board without winning tile
        self.game.board[0][0] = 1024  # Less than win value
        
        self.assertFalse(self.game.check_win())
        self.assertFalse(self.game.won)
    
    def test_game_over_detection_full_board(self):
        """Test game over detection when board is full with no merges"""
        # Create board with no empty spaces and no possible merges
        board = [
            [2, 4, 8, 16],
            [4, 8, 16, 32],
            [8, 16, 32, 64],
            [16, 32, 64, 128]
        ]
        
        for y in range(4):
            for x in range(4):
                self.game.board[y][x] = board[y][x]
        
        self.assertTrue(self.game.check_game_over())
        self.assertTrue(self.game.over)
    
    def test_game_over_not_triggered_with_empty_cells(self):
        """Test that game over is not triggered when empty cells exist"""
        # Create board with one empty cell
        board = [
            [2, 4, 8, 16],
            [4, 8, 16, 32],
            [8, 16, 32, 64],
            [16, 32, 64, 0]  # One empty cell
        ]
        
        for y in range(4):
            for x in range(4):
                self.game.board[y][x] = board[y][x]
        
        self.assertFalse(self.game.check_game_over())
        self.assertFalse(self.game.over)
    
    def test_game_over_not_triggered_with_possible_merges(self):
        """Test that game over is not triggered when merges are possible"""
        # Create full board with possible horizontal merge
        board = [
            [2, 4, 8, 16],
            [4, 8, 16, 32],
            [8, 16, 32, 64],
            [16, 32, 32, 128]  # Two 32s can merge
        ]
        
        for y in range(4):
            for x in range(4):
                self.game.board[y][x] = board[y][x]
        
        self.assertFalse(self.game.check_game_over())
        self.assertFalse(self.game.over)
        
        # Test with possible vertical merge
        board = [
            [2, 4, 8, 16],
            [4, 8, 16, 32],
            [8, 16, 32, 64],
            [16, 16, 64, 128]  # Two 16s can merge vertically
        ]
        
        for y in range(4):
            for x in range(4):
                self.game.board[y][x] = board[y][x]
        
        self.assertFalse(self.game.check_game_over())
        self.assertFalse(self.game.over)


if __name__ == '__main__':
    unittest.main()
