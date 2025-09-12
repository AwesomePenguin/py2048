#!/usr/bin/env python3
"""
Test script to validate the Pydantic models and game context generation
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game import Game
from models import GameContext, AIRequest, AIResponse
import json

def test_basic_model_creation():
    """Test that we can create a game and generate AI context"""
    print("Testing basic model creation...")
    
    # Create a basic game
    game = Game(test_mode=True)
    
    # Generate AI context
    context = game.get_ai_context()
    
    # Validate that we got a proper GameContext object
    assert isinstance(context, GameContext)
    print(f"✓ Successfully created GameContext")
    
    # Print some key information
    print(f"  Board size: {context.config.board_size}")
    print(f"  Current score: {context.game_state.score}")
    print(f"  Game status: {context.game_state.status}")
    print(f"  Available moves: {context.available_moves}")
    print(f"  Hints remaining: {context.resources.hints.remaining}")
    
    return context

def test_json_serialization():
    """Test that the models can be serialized to JSON"""
    print("\nTesting JSON serialization...")
    
    game = Game(test_mode=True)
    context = game.get_ai_context()
    
    # Convert to JSON
    json_str = context.model_dump_json()
    print(f"✓ Successfully serialized to JSON ({len(json_str)} characters)")
    
    # Parse back from JSON
    context_from_json = GameContext.model_validate_json(json_str)
    print(f"✓ Successfully parsed from JSON")
    
    # Verify they're equivalent
    assert context_from_json.game_state.score == context.game_state.score
    assert context_from_json.config.board_size == context.config.board_size
    print(f"✓ Round-trip serialization successful")

def test_custom_configuration():
    """Test with custom game configuration"""
    print("\nTesting custom configuration...")
    
    custom_config = {
        'size_x': 5,
        'size_y': 5,
        'win_value': 1024,
        'use_streak': True,
        'streak_bonus_percent': 15,
        'merge_strategy': 'reverse',
        'max_redo': 5,
        'number_of_hints': 5
    }
    
    game = Game(config=custom_config, test_mode=True)
    context = game.get_ai_context()
    
    # Validate custom settings
    assert context.config.board_size == (5, 5)
    assert context.config.win_target == 1024
    assert context.config.streak_enabled == True
    assert context.config.streak_bonus_percent == 15
    assert context.config.merge_strategy == "reverse"
    assert context.resources.hints.total == 5
    
    print(f"✓ Custom configuration properly reflected in context")

def test_ai_request_response():
    """Test AI request and response models"""
    print("\nTesting AI request/response models...")
    
    game = Game(test_mode=True)
    context = game.get_ai_context()
    
    # Create an AI request
    ai_request = AIRequest(
        context=context,
        request_type="hint",
        specific_question="What's the best move to maximize score?"
    )
    
    print(f"✓ Successfully created AI request")
    
    # Create a mock AI response
    ai_response = AIResponse(
        success=True,
        suggestion="left",
        reasoning="Moving left will consolidate tiles and create merge opportunities",
        confidence=0.85,
        alternative_moves=["up", "down"],
        strategic_advice="Keep your highest tiles in corners",
        difficulty_assessment="early_game"
    )
    
    print(f"✓ Successfully created AI response")
    
    # Test serialization
    request_json = ai_request.model_dump_json()
    response_json = ai_response.model_dump_json()
    
    print(f"✓ AI models can be serialized to JSON")

def print_example_json():
    """Print a pretty example of the JSON structure"""
    print("\nExample GameContext JSON structure:")
    
    game = Game(test_mode=True)
    context = game.get_ai_context()
    
    # Pretty print the JSON
    json_dict = context.model_dump()
    print(json.dumps(json_dict, indent=2, default=str))

if __name__ == "__main__":
    try:
        test_basic_model_creation()
        test_json_serialization()
        test_custom_configuration()
        test_ai_request_response()
        print_example_json()
        print("\n🎉 All tests passed! Models are working correctly.")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        raise
