#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from game import Game

def debug_redo():
    """Debug the redo behavior with move counts"""
    config = {
        'initial_tiles': 0,
        'random_new_tiles': 0,
        'max_redo': 3
    }
    game = Game(config, test_mode=True)
    
    # Set up initial board
    initial_board = [
        [2, 2, 4, 4],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0]
    ]
    
    for y in range(len(initial_board)):
        for x in range(len(initial_board[y])):
            game.board[y][x] = initial_board[y][x]
    
    print("=== DEBUG REDO BEHAVIOR ===")
    print(f"Initial state - moves: {game.moves_count}, history length: {len(game.history)}")
    
    # Save state manually (like the test does)
    game.save_state_to_history()
    print(f"After manual save - moves: {game.moves_count}, history length: {len(game.history)}")
    
    # Move 1
    print("\n--- Move 1 (left) ---")
    result = game.handle_move('left')
    print(f"Move result: {result}")
    print(f"After move 1 - moves: {game.moves_count}, history length: {len(game.history)}")
    print(f"History moves: {[state.get('moves_count', 'unknown') for state in game.history]}")
    
    # Move 2
    print("\n--- Move 2 (right) ---")
    result = game.handle_move('right')
    print(f"Move result: {result}")
    print(f"After move 2 - moves: {game.moves_count}, history length: {len(game.history)}")
    print(f"History moves: {[state.get('moves_count', 'unknown') for state in game.history]}")
    
    # Redo
    print("\n--- Redo ---")
    result = game.handle_redo()
    print(f"Redo result: {result}")
    print(f"After redo - moves: {game.moves_count}, history length: {len(game.history)}")
    print(f"History moves: {[state.get('moves_count', 'unknown') for state in game.history]}")

if __name__ == "__main__":
    debug_redo()
