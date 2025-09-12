#!/usr/bin/env python3
"""
Test for improved AI response parsing
"""

import re

def test_move_parsing():
    """Test various AI response formats"""
    
    test_responses = [
        # Correct format
        "**Recommended move:** LEFT\nThis will consolidate your tiles and create merge opportunities.",
        
        # Alternative format
        "Recommended move: right\nMoving right will help you build up your score.",
        
        # Without asterisks
        "I recommend move: UP to create space at the bottom.",
        
        # Casual format
        "I suggest you try moving down to combine those 4s.",
        
        # Edge case - multiple directions mentioned
        "You could go left or right, but I recommend move: DOWN as the best option.",
        
        # No clear format
        "Moving in any direction would work, but up seems best right now.",
    ]
    
    print("Testing AI response parsing:")
    print("=" * 50)
    
    for i, response in enumerate(test_responses, 1):
        print(f"\nTest {i}: {response[:50]}...")
        
        suggested_move = None
        
        # Look for the specific pattern: **Recommended move:** [DIRECTION]
        move_pattern = r'\*\*Recommended move:\*\*\s*(UP|DOWN|LEFT|RIGHT|up|down|left|right)'
        match = re.search(move_pattern, response, re.IGNORECASE)
        
        if match:
            suggested_move = match.group(1).lower()
            print(f"  ✓ Found with main pattern: {suggested_move}")
        else:
            # Fallback: look for "move:" pattern without asterisks
            fallback_pattern = r'move:\s*(UP|DOWN|LEFT|RIGHT|up|down|left|right)'
            fallback_match = re.search(fallback_pattern, response, re.IGNORECASE)
            if fallback_match:
                suggested_move = fallback_match.group(1).lower()
                print(f"  ✓ Found with fallback pattern: {suggested_move}")
            else:
                # Last resort: look for direction words with context
                directions = ['up', 'down', 'left', 'right']
                for direction in directions:
                    suggest_pattern = rf'(suggest|recommend|try|go)\s+\w*\s*{direction}'
                    if re.search(suggest_pattern, response, re.IGNORECASE):
                        suggested_move = direction
                        print(f"  ✓ Found with context pattern: {suggested_move}")
                        break
                
                if not suggested_move:
                    print(f"  ❌ No move found")

if __name__ == "__main__":
    test_move_parsing()
