'''
Module to handle AI chat functionalities.
Connect to remote AI services via OpenAI-compatible API.
For our coding exercise, we will use Qwen hosted on Alibaba Cloud.
'''
import os
from datetime import datetime
from typing import Dict
from dotenv import load_dotenv
from openai import OpenAI  # Use sync client instead
from models import AIResponse, GameContext

load_dotenv(".env.local")

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
            system_prompt = (
                "You are an expert 2048 game assistant. Analyze the game state and provide a helpful hint. "
                "Your response should include:\n"
                "1. A recommended move direction (up/down/left/right)\n"
                "2. Brief reasoning for the recommendation\n"
                "3. General strategy advice\n"
                "Keep your response concise and actionable."
            )
            
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
            
            # Simple parsing to extract move suggestion (look for direction words)
            suggested_move = None
            directions = ['up', 'down', 'left', 'right']
            for direction in directions:
                if direction.lower() in ai_content.lower():
                    suggested_move = direction
                    break
            
            return AIResponse(
                success=True,
                suggestion=suggested_move,
                reasoning=ai_content,
                confidence=0.8,  # Default confidence
                error_message=None
            )
            
        except Exception as e:
            return AIResponse(
                success=False,
                suggestion=None,
                reasoning=f"AI service unavailable: {str(e)}",
                confidence=0.0,
                error_message=str(e)
            )