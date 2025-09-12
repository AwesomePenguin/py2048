"""
Integration tests for complete game workflows and command processing
"""

import unittest
import sys
import os

# Add parent directory to path to import game module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game import Game
from models import CommandResponse, GameContext, TestGameConfigurationRequest


class TestGameIntegration(unittest.TestCase):
    """Test complete game workflows and integration scenarios"""
    
    def setUp(self):
        """Set up test fixtures"""
        config = TestGameConfigurationRequest(
            initial_tiles=0,
            random_new_tiles=0,
            streak_enabled=True,
            streak_bonus_percent=10,
            max_redo=3
        )
        self.game = Game(config, test_mode=True)
    
    def set_board(self, board_data):
        """Helper method to set board state"""
        for y in range(len(board_data)):
            for x in range(len(board_data[y])):
                self.game.board[y][x] = board_data[y][x]
    
    def test_complete_game_workflow(self):
        """Test a complete game workflow with multiple moves, streaks, and redos"""
        # Start with initial board state
        initial_board = [
            [2, 2, 4, 4],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0]
        ]
        self.set_board(initial_board)
        self.game.save_state_to_history()  # Save initial state
        
        # Move 1: Left - should create merges and start streak
        result = self.game.handle_move('left')
        self.assertTrue(result)
        self.assertEqual(self.game.moves_count, 1)
        self.assertEqual(self.game.streak, 1)
        self.assertGreater(self.game.score, 0)
        expected_after_left = [
            [4, 8, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0]
        ]
        self.assertEqual(self.game.board, expected_after_left)
        
        # Store intermediate state
        intermediate_score = self.game.score
        intermediate_streak = self.game.streak
        
        # Move 2: Setup for another merge to continue streak
        self.set_board([
            [4, 8, 0, 0],
            [4, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0]
        ])
        
        result = self.game.handle_move('down')
        self.assertTrue(result)
        self.assertEqual(self.game.moves_count, 2)
        self.assertEqual(self.game.streak, 2)  # Streak should continue
        self.assertGreater(self.game.score, intermediate_score)
        
        # Test redo functionality
        current_score = self.game.score
        current_moves = self.game.moves_count
        current_board = [row[:] for row in self.game.board]
        
        print(f'move count before redo: {self.game.moves_count}')
        result = self.game.handle_redo()
        self.assertTrue(result)
        self.assertEqual(self.game.redos_used, 1)
        print(f'move count after redo: {self.game.moves_count}')
        self.assertEqual(self.game.moves_count, current_moves - 1)
        self.assertEqual(self.game.score, intermediate_score)
        self.assertNotEqual(self.game.board, current_board)
    
    def test_win_condition_workflow(self):
        """Test complete workflow leading to win condition"""
        # Set up board close to winning
        winning_board = [
            [1024, 1024, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0]
        ]
        self.set_board(winning_board)
        
        # Make winning move
        result = self.game.handle_move('left')
        
        self.assertTrue(result)
        self.assertTrue(self.game.check_win())
        self.assertTrue(self.game.won)
        
        # Verify winning tile exists
        has_winning_tile = any(
            cell >= self.game.win_value 
            for row in self.game.board 
            for cell in row
        )
        self.assertTrue(has_winning_tile)
    
    def test_game_over_workflow(self):
        """Test complete workflow leading to game over"""
        # Set up board with no possible moves
        game_over_board = [
            [2, 4, 8, 16],
            [4, 8, 16, 32],
            [8, 16, 32, 64],
            [16, 32, 64, 128]
        ]
        self.set_board(game_over_board)
        
        # Verify game over detection
        self.assertTrue(self.game.check_game_over())
        self.assertTrue(self.game.over)
        
        # Verify no valid moves
        self.assertFalse(self.game.handle_move('left'))
        self.assertFalse(self.game.handle_move('right'))
        self.assertFalse(self.game.handle_move('up'))
        self.assertFalse(self.game.handle_move('down'))
    
    def test_streak_break_and_recovery(self):
        """Test streak system through break and recovery"""
        # Build up streak
        self.set_board([
            [2, 2, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0]
        ])
        
        self.game.handle_move('left')
        self.assertEqual(self.game.streak, 1)
        
        # Continue streak
        self.set_board([
            [4, 0, 0, 0],
            [4, 4, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0]
        ])
        
        self.game.handle_move('left')
        self.assertEqual(self.game.streak, 2)
        
        # Break streak with move without merge
        self.set_board([
            [8, 0, 0, 0],
            [2, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0]
        ])
        
        self.game.handle_move('right')  # No merge possible
        self.assertEqual(self.game.streak, 0)  # Streak broken
        
        # Start new streak
        self.set_board([
            [0, 0, 8, 0],
            [0, 0, 2, 0],
            [2, 2, 0, 0],
            [0, 0, 0, 0]
        ])
        
        self.game.handle_move('left')
        self.assertEqual(self.game.streak, 1)  # New streak started
    
    def test_multiple_redo_workflow(self):
        """Test multiple redos in sequence"""
        # Make several moves
        moves_data = [
            [2, 2, 0, 0],
            [4, 0, 2, 2],
            [4, 4, 0, 0]
        ]
        
        move_scores = []
        
        for i, board_state in enumerate(moves_data):
            self.set_board([
                board_state,
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0]
            ])
            
            self.game.handle_move('left')
            move_scores.append(self.game.score)
            self.assertEqual(self.game.moves_count, i + 1)
        
        # Redo moves in reverse order
        for i in range(len(moves_data)):
            result = self.game.handle_redo()
            self.assertTrue(result)
            self.assertEqual(self.game.redos_used, i + 1)
            
            expected_moves = len(moves_data) - i - 1
            self.assertEqual(self.game.moves_count, expected_moves)
            
            if expected_moves > 0:
                self.assertEqual(self.game.score, move_scores[expected_moves - 1])
            else:
                self.assertEqual(self.game.score, 0)  # Back to initial state


class TestCommandProcessing(unittest.TestCase):
    """Test web API command processing functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        config = TestGameConfigurationRequest(
            initial_tiles=0,
            random_new_tiles=0
        )
        self.game = Game(config, test_mode=True)
        self.game.set_output_mode('web')  # Set output mode after initialization
    
    def test_process_command_move(self):
        """Test processing move commands via API"""
        # Set up board for valid move
        self.game.board[0] = [2, 2, 0, 0]
        
        # Process move command
        result = self.game.process_command('left')
        
        # Verify return type is CommandResponse
        self.assertIsInstance(result, CommandResponse)
        
        # Test the response structure
        self.assertTrue(result.success)
        self.assertIsNone(result.error_message)
        self.assertFalse(result.game_ended)
        self.assertEqual(result.command, 'left')
        self.assertIsInstance(result.game_data, GameContext)
        
        # Verify game state was updated
        self.assertEqual(self.game.moves_count, 1)
        self.assertGreater(self.game.score, 0)
    
    def test_process_command_invalid_move(self):
        """Test processing invalid move commands"""
        # Set up board where no movement is possible
        self.game.board = [
            [2, 4, 8, 16],
            [4, 8, 16, 32],
            [8, 16, 32, 64],
            [16, 32, 64, 128]
        ]
        
        result = self.game.process_command('left')
        
        self.assertIsInstance(result, CommandResponse)
        self.assertFalse(result.success)
        self.assertIsNotNone(result.error_message)
        self.assertIsInstance(result.game_data, GameContext)
    
    def test_process_command_redo(self):
        """Test processing redo commands via API"""
        # Make a move first
        self.game.board[0] = [2, 2, 0, 0]
        self.game.process_command('left')
        
        # Now test redo
        result = self.game.process_command('redo')
        
        self.assertIsInstance(result, CommandResponse)
        self.assertTrue(result.success)
        self.assertIsNone(result.error_message)
        self.assertEqual(result.command, 'redo')
        self.assertEqual(self.game.redos_used, 1)
    
    def test_process_command_hint(self):
        """Test processing hint commands via API"""
        result = self.game.process_command('hint')
        
        self.assertIsInstance(result, CommandResponse)
        self.assertTrue(result.success)
        self.assertIsNone(result.error_message)
        self.assertEqual(result.command, 'hint')
        self.assertEqual(self.game.hints_used, 1)
    
    def test_process_command_restart(self):
        """Test processing restart commands via API"""
        # Make some changes to game state
        self.game.score = 100
        self.game.moves_count = 5
        
        result = self.game.process_command('restart')
        
        self.assertIsInstance(result, CommandResponse)
        self.assertTrue(result.success)
        self.assertIsNone(result.error_message)
        self.assertEqual(result.command, 'restart')
        
        # Verify game was restarted
        self.assertEqual(self.game.score, 0)
        self.assertEqual(self.game.moves_count, 0)
    
    def test_process_command_invalid(self):
        """Test processing invalid commands"""
        result = self.game.process_command('invalid_command')
        
        self.assertIsInstance(result, CommandResponse)
        self.assertFalse(result.success)
        self.assertEqual(result.command, 'invalid_command')
        self.assertIn('Invalid command', result.error_message)
        # The GameContext should still be provided even for invalid commands
        self.assertIsInstance(result.game_data, GameContext)
    
    def test_process_command_win_detection(self):
        """Test that command processing detects win conditions"""
        # Set up board for winning move
        self.game.board[0] = [1024, 1024, 0, 0]
        
        result = self.game.process_command('left')
        
        self.assertIsInstance(result, CommandResponse)
        self.assertTrue(result.success)
        self.assertTrue(result.game_ended)
        self.assertEqual(result.command, 'left')
        self.assertIn('Congratulations', self.game.display_message)
    
    def test_process_command_game_over_detection(self):
        """Test that command processing detects game over conditions"""
        # Set up board that will be game over after move
        self.game.board = [
            [2, 4, 8, 16],
            [4, 8, 16, 2],  # This will become 32 after right move
            [8, 16, 32, 64],
            [16, 32, 64, 128]
        ]
        
        # Make a move that results in a full board with no merges
        result = self.game.process_command('right')
        
        self.assertIsInstance(result, CommandResponse)
        self.assertEqual(result.command, 'right')
        
        # The result depends on whether this actually creates a game over state
        # Let's check if game over was detected
        if self.game.check_game_over():
            self.assertTrue(result.game_ended)
            self.assertIn('Game Over', self.game.display_message)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions"""
    
    def setUp(self):
        """Set up test fixtures"""
        config = TestGameConfigurationRequest(
            initial_tiles=0,
            random_new_tiles=0
        )
        self.game = Game(config, test_mode=True)
    
    def test_empty_board_operations(self):
        """Test operations on empty board"""
        # All moves should be invalid on empty board
        for direction in ['up', 'down', 'left', 'right']:
            result = self.game.handle_move(direction)
            self.assertFalse(result)
    
    def test_single_tile_operations(self):
        """Test operations with single tile"""
        self.game.board[1][1] = 2
        
        # Moves should work (tile should slide) but no merges
        result = self.game.handle_move('left')
        self.assertTrue(result)
        self.assertEqual(self.game.board[1][0], 2)  # Tile moved to left edge
        self.assertEqual(self.game.score, 0)  # No merges, no score
    
    def test_board_state_after_invalid_move(self):
        """Test that board state is unchanged after invalid move"""
        initial_board = [
            [2, 4, 8, 16],
            [4, 8, 16, 32],
            [8, 16, 32, 64],
            [16, 32, 64, 128]
        ]
        
        # Set board and store copy
        for y in range(4):
            for x in range(4):
                self.game.board[y][x] = initial_board[y][x]
        
        board_copy = [row[:] for row in self.game.board]
        initial_score = self.game.score
        initial_moves = self.game.moves_count
        
        # Try invalid move
        result = self.game.handle_move('left')
        
        self.assertFalse(result)
        self.assertEqual(self.game.board, board_copy)  # Board unchanged
        self.assertEqual(self.game.score, initial_score)  # Score unchanged
        self.assertEqual(self.game.moves_count, initial_moves)  # Moves unchanged
    
    def test_large_numbers(self):
        """Test game behavior with large tile values"""
        # Set up board with large numbers
        self.game.board[0] = [512, 512, 1024, 1024]
        
        result = self.game.handle_move('left')
        
        self.assertTrue(result)
        expected_board = [1024, 2048, 0, 0]
        self.assertEqual(self.game.board[0], expected_board)
        
        # Check score calculation with large numbers
        expected_score = 1024 + 2048  # Points from merges
        self.assertEqual(self.game.score, expected_score)
    
    def test_custom_board_sizes(self):
        """Test game functionality with non-standard board sizes"""
        # Test small board
        config = TestGameConfigurationRequest(
            board_size=(3, 3),
            initial_tiles=0,
            random_new_tiles=0
        )
        small_game = Game(config, test_mode=True)
        
        small_game.board[0] = [2, 2, 4]
        result = small_game.handle_move('left')
        
        self.assertTrue(result)
        self.assertEqual(small_game.board[0], [4, 4, 0])
        
        # Test rectangular board
        config = TestGameConfigurationRequest(
            board_size=(5, 3),
            initial_tiles=0,
            random_new_tiles=0
        )
        rect_game = Game(config, test_mode=True)
        
        rect_game.board[0] = [2, 2, 4, 4, 8]
        result = rect_game.handle_move('left')
        
        self.assertTrue(result)
        self.assertEqual(rect_game.board[0], [4, 8, 8, 0, 0])
    
    def test_state_consistency_after_errors(self):
        """Test that game state remains consistent after various errors"""
        initial_state = self.game.get_state_copy()
        
        # Try various invalid operations
        self.game.handle_move('invalid_direction')  # Should be caught earlier
        self.game.handle_redo()  # No history to redo
        
        # When hints are exhausted
        for _ in range(self.game.number_of_hints + 2):
            self.game.handle_hint()
        
        # State should remain valid
        current_state = self.game.get_state_copy()
        
        # Some fields may have changed (like hints_used), but structure should be intact
        self.assertEqual(len(current_state), len(initial_state))
        for key in initial_state:
            self.assertIn(key, current_state)


if __name__ == '__main__':
    unittest.main()
