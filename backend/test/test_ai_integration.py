#!/usr/bin/env python3
"""
Simple test for AI integration
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game import Game
from ai_chat import AIChat

def test_ai_integration():
    """Test basic AI integration without requiring actual API keys"""
    print("Testing AI integration...")
    
    # Test game with hint functionality
    game = Game(test_mode=True)
    
    # Set up a simple board state
    game.board = [
        [2, 4, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0]
    ]
    
    # Test that hint functionality doesn't crash (even if AI is unavailable)
    try:
        result = game.handle_hint()
        print(f"✓ Hint handling works: {result}")
        print(f"  Message: {game.display_message}")
        print(f"  Hints used: {game.hints_used}")
        print(f"  Hint history length: {len(game.hint_history)}")
        
        # Test hint history tracking
        if game.hint_history:
            latest_hint = game.hint_history[-1]
            print(f"  Latest hint direction: {latest_hint.hint_direction}")
            print(f"  Latest hint reasoning: {latest_hint.hint_reasoning[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ AI integration test failed: {e}")
        return False

def test_ai_chat_structure():
    """Test AIChat class structure"""
    print("\nTesting AIChat class structure...")
    
    try:
        # This will fail without proper env vars, but tests class structure
        chat = AIChat()
        print("❌ Expected environment error, but class loaded")
        return False
    except ValueError as e:
        if "API key or Base URL" in str(e):
            print("✓ AIChat properly validates environment variables")
            return True
        else:
            print(f"❌ Unexpected error: {e}")
            return False
    except Exception as e:
        print(f"❌ Unexpected error type: {e}")
        return False

if __name__ == "__main__":
    print("🤖 Testing AI Integration")
    print("=" * 40)
    
    success1 = test_ai_integration()
    success2 = test_ai_chat_structure()
    
    if success1 and success2:
        print("\n🎉 AI integration tests passed!")
        print("Note: Actual AI functionality requires proper .env.local configuration")
    else:
        print("\n❌ Some tests failed!")
