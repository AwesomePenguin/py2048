'''
Module to handle AI chat functionalities.
Connect to remote AI services via OpenAI-compatible API.
For our coding exercise, we will use Qwen hosted on Alibaba Cloud.
'''
import os
import requests
from datetime import datetime
from typing import Dict
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv(".env.local")

class AIChat:
    def __init__(self):
        self.api_key = os.getenv("DASHSCOPE_API_KEY")
        self.base_url = os.getenv("MODEL_API_URL")
        self.default_model = os.getenv("DEFAULT_MODEL", "qwen-plus")

        self._check_variables()

        # Initialize OpenAI-compatible client
        self.client = AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
    
    def _check_variables(self):
        if not self.api_key or not self.base_url:
            raise ValueError("API key or Base URL is not set in environment variables.")
        if not self.default_model:
            raise ValueError("Default model is not set in environment variables.")

    async def health_check(self) -> Dict[str, any]:
        '''
        Check the health of the AI service.
        '''
        try:
            # Simple API test
            test_response = await self.client.chat.completions.create(
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
        
    async def chat(self, context)