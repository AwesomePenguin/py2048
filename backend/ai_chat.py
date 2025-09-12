'''
Module to handle AI chat functionalities.
Connect to remote AI services via OpenAI-compatible API.
For our coding exercise, we will use Qwen hosted on Alibaba Cloud.
'''
import os
import re
from datetime import datetime
from typing import Dict
from dotenv import load_dotenv
from openai import OpenAI  # Use sync client instead
from models import AIResponse, GameContext

load_dotenv()

class AIChat:
    def __init__(self):
        self.api_key = os.getenv("DASHSCOPE_API_KEY")
        self.base_url = os.getenv("MODEL_API_URL")
        self.default_model = os.getenv("DEFAULT_MODEL", "qwen-plus")

        self._check_variables()

        # Initialize OpenAI-compatible client
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
    
    def _check_variables(self):
        if not self.api_key or not self.base_url:
            raise ValueError("API key or Base URL is not set in environment variables.")
        if not self.default_model:
            raise ValueError("Default model is not set in environment variables.")

    def health_check(self) -> Dict[str, any]:
        '''
        Check the health of the AI service.
        '''
        try:
            # Simple API test
            test_response = self.client.chat.completions.create(
                model=self.default_model,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10
            )
            
            return {
                "status": "healthy",
                "default_model": self.default_model,
                "api_available": True,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "api_available": False,
                "timestamp": datetime.utcnow().isoformat()
            }
        
    def chat(self, context: GameContext) -> AIResponse:
        '''
        Send game context to AI and get a response.
        '''
        try:
            # Create comprehensive game rules and context
            game_rules = f"""
=== 2048 GAME RULES ===
OBJECTIVE: Reach the target value of {context.config.win_target} by merging tiles.

MERGE MECHANICS:
- Only tiles with IDENTICAL numbers can merge (e.g., 2+2=4, 4+4=8, 16+16=32). Different numbers will NOT merge (e.g., 2+4 cannot merge).
- When you move tiles in a direction, ALL tiles slide until they hit a wall or another tile
- If two identical tiles collide, they merge into their SUM
- Each tile can only merge ONCE per move
- Merge strategy: {context.config.merge_strategy.upper()} 
  {"(merges happen away from movement direction)" if context.config.merge_strategy == "standard" else "(merges happen towards movement direction)"}

BOARD CONFIGURATION:
- Board size: {context.config.board_size[0]}x{context.config.board_size[1]}
- Win target: {context.config.win_target}
- Scoring: Points = sum of merged tiles{"+ streak bonus" if context.config.streak_enabled else ""}

MOVEMENT RULES:
- UP: All tiles slide toward the top row
- DOWN: All tiles slide toward the bottom row  
- LEFT: All tiles slide toward the leftmost column
- RIGHT: All tiles slide toward the rightmost column
- Invalid moves: No tiles can move in that direction (board unchanged)

STRATEGY PRINCIPLES:
1. Keep your highest tile in one corner
2. Build tiles in ascending order toward that corner
3. Avoid spreading high-value tiles across the board
4. Plan moves to create merge opportunities
5. Consider the placement of new tiles (they spawn randomly in empty spots)
"""

            system_prompt = f"""You are an expert 2048 game strategist with deep understanding of tile-merging mechanics.

{game_rules}

RESPONSE FORMAT (MANDATORY):
**Recommended move:** [UP/DOWN/LEFT/RIGHT]
**Reasoning:** [Explain why this move is optimal, considering merges and positioning]
**Strategy:** [Brief advice for next 1-2 moves]

ANALYSIS REQUIREMENTS:
- Identify all possible merges for each direction
- Consider tile positioning after merges
- Account for where new tiles might spawn
- Prioritize moves that create the most merges or best positioning
- Avoid moves that separate high-value tiles
- Never suggest impossible moves (check available moves list)"""
            
            # Create a concise context summary
            board_str = "\n".join([" ".join(f"{cell:4}" for cell in row) for row in context.game_state.board])
            context_summary = (
                f"Current board:\n{board_str}\n"
                f"Score: {context.game_state.score}, Moves: {context.game_state.moves}\n"
                f"Available moves: {context.available_moves}\n"
                f"Win target: {context.config.win_target}"
            )
            
            response = self.client.chat.completions.create(
                model=self.default_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": context_summary}
                ],
                max_tokens=200,
                temperature=0.3  # Low temperature for focused responses
            )
            
            ai_content = response.choices[0].message.content.strip()
            
            # Smart parsing to extract move suggestion from "Recommended move:" pattern
            suggested_move = None
            
                        # Enhanced parsing for the consistent "**Recommended move:** **DIRECTION**" pattern
            suggested_move = None
            
            # Primary pattern: **Recommended move:** **DIRECTION**
            primary_pattern = r'\*\*Recommended move:\*\*\s*\*\*(UP|DOWN|LEFT|RIGHT|up|down|left|right)\*\*'
            match = re.search(primary_pattern, ai_content, re.IGNORECASE)
            
            if match:
                suggested_move = match.group(1).lower()
                print(f"[DEBUG] Found recommended move via primary pattern: {suggested_move}")
            else:
                # Secondary pattern: **Recommended move:** DIRECTION (without second set of asterisks)
                secondary_pattern = r'\*\*Recommended move:\*\*\s*(UP|DOWN|LEFT|RIGHT|up|down|left|right)'
                secondary_match = re.search(secondary_pattern, ai_content, re.IGNORECASE)
                
                if secondary_match:
                    suggested_move = secondary_match.group(1).lower()
                    print(f"[DEBUG] Found recommended move via secondary pattern: {suggested_move}")
                else:
                    # Tertiary pattern: "Recommended move:" (without asterisks)
                    tertiary_pattern = r'Recommended move:\s*(UP|DOWN|LEFT|RIGHT|up|down|left|right)'
                    tertiary_match = re.search(tertiary_pattern, ai_content, re.IGNORECASE)
                    
                    if tertiary_match:
                        suggested_move = tertiary_match.group(1).lower()
                        print(f"[DEBUG] Found recommended move via tertiary pattern: {suggested_move}")
                    else:
                        # Final fallback: look for any direction after "suggest", "recommend", "try"
                        action_words = ['suggest', 'recommend', 'try', 'move', 'go']
                        directions = ['up', 'down', 'left', 'right']
                        
                        for action in action_words:
                            for direction in directions:
                                fallback_pattern = rf'{action}\s+\w*\s*{direction}'
                                if re.search(fallback_pattern, ai_content, re.IGNORECASE):
                                    suggested_move = direction
                                    print(f"[DEBUG] Found move via fallback pattern ({action} + {direction}): {suggested_move}")
                                    break
                            if suggested_move:
                                break
                        
                        # Ultimate fallback: first available move
                        if not suggested_move and context.available_moves:
                            suggested_move = context.available_moves[0]
                            print(f"[DEBUG] Using first available move as fallback: {suggested_move}")
                        
                        if not suggested_move:
                            print(f"[DEBUG] No move pattern found in AI response: {ai_content[:200]}...")
            move_pattern = r'\*\*Recommended move:\*\*\s*(UP|DOWN|LEFT|RIGHT|up|down|left|right)'
            match = re.search(move_pattern, ai_content, re.IGNORECASE)
            
            if match:
                suggested_move = match.group(1).lower()
            else:
                # Fallback: look for "move:" pattern without asterisks
                fallback_pattern = r'move:\s*(UP|DOWN|LEFT|RIGHT|up|down|left|right)'
                fallback_match = re.search(fallback_pattern, ai_content, re.IGNORECASE)
                if fallback_match:
                    suggested_move = fallback_match.group(1).lower()
                else:
                    # Last resort: look for direction words, but prioritize based on context
                    directions = ['up', 'down', 'left', 'right']
                    # Look for directions that appear after keywords like "suggest", "recommend", "try"
                    for direction in directions:
                        suggest_pattern = rf'(suggest|recommend|try|go)\s+\w*\s*{direction}'
                        if re.search(suggest_pattern, ai_content, re.IGNORECASE):
                            suggested_move = direction
                            break
                    
                    # If still no match, fall back to first available move
                    if not suggested_move and context.available_moves:
                        suggested_move = context.available_moves[0]
            
            # Extract alternative moves from available moves
            alternative_moves = None
            if context.available_moves and suggested_move:
                alternative_moves = [move for move in context.available_moves if move != suggested_move]
            
            return AIResponse(
                success=True,
                suggestion=suggested_move,
                reasoning=ai_content,
                confidence=0.8,  # Default confidence
                alternative_moves=alternative_moves,
                strategic_advice="Focus on keeping your highest tiles in one corner",
                difficulty_assessment="moderate",
                error_message=None
            )
            
        except Exception as e:
            return AIResponse(
                success=False,
                suggestion=None,
                reasoning=f"AI service unavailable: {str(e)}",
                confidence=0.0,
                alternative_moves=None,
                strategic_advice=None,
                difficulty_assessment=None,
                error_message=str(e)
            )