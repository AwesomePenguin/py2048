'''
FastAPI server that exposes the 2048 game functionality via REST API.
'''
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv

from game import Game
from models import (CommandResponse, GameResponse, GameConfigurationRequest, 
                   AIResponse, GameContext, AuthRequest, AuthResponse)

load_dotenv()  # Load environment variables from .env file

class Server:
    """Encapsulates the FastAPI server and game instance."""
    
    def __init__(self):
        self.app = FastAPI(title="2048 Game API", version="1.0.0")
        self.game = None
        
        # Allow CORS for local development (adjust origins as needed)
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        self.setup_routes()
    
    def setup_routes(self):
        """Define API routes."""
        
        @self.app.get("/status")
        def get_status():
            """Check server status."""
            return {"status": "ok", "message": "2048 Game API is running."}
        
        @self.app.post("/new-game", response_model=GameResponse)
        def new_game(config: Optional[GameConfigurationRequest] = None):
            """Start a new game with optional configuration."""
            try:
                # Pass Pydantic model directly to Game constructor
                self.game = Game(config=config)
                return self.game.get_frontend_response("New game started!")
                
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Failed to create game: {str(e)}")
        
        @self.app.post("/move/{direction}", response_model=CommandResponse)
        def make_move(direction: str):
            """Make a move in the specified direction."""
            if not self.game:
                raise HTTPException(status_code=400, detail="Game not initialized. Start a new game first.")

            if direction not in ["up", "down", "left", "right"]:
                raise HTTPException(status_code=400, detail="Invalid move direction.")
            
            return self.game.process_command(direction)
        
        @self.app.post("/hint", response_model=CommandResponse)
        def get_hint():
            """Get an AI-generated hint for the next move."""
            if not self.game:
                raise HTTPException(status_code=400, detail="Game not initialized. Start a new game first.")

            return self.game.process_command("hint")
        
        @self.app.get("/game-state", response_model=GameResponse)
        def get_game_state():
            """Retrieve the current game state."""
            if not self.game:
                raise HTTPException(status_code=400, detail="Game not initialized. Start a new game first.")

            return self.game.get_frontend_response("Current game state")
        
        @self.app.post("/redo", response_model=CommandResponse)
        def redo_move():
            """Redo/undo the last move (in our game, 'redo' means undo)."""
            if not self.game:
                raise HTTPException(status_code=400, detail="Game not initialized. Start a new game first.")
            
            return self.game.process_command("redo")
        
        @self.app.post("/auth", response_model=AuthResponse)
        def auth(request: AuthRequest):
            """Simple authentication with invitation code validation"""
            # Default invitation code if env variable is not set
            valid_invit_code = os.getenv("INVIT_CODE")
            if not valid_invit_code:
                raise HTTPException(status_code=500, detail="Server misconfiguration: INVIT_CODE not set.")
            
            # Case-insensitive comparison
            if request.invitation_code.strip().upper() == valid_invit_code.upper():
                return AuthResponse(
                    success=True,
                    message="Authentication successful! Welcome to py2048.",
                    authenticated=True
                )
            else:
                return AuthResponse(
                    success=False,
                    message="Invalid invitation code. Please try again.",
                    authenticated=False
                )            

def create_server():
    """Factory function to create a server instance."""
    return Server()


if __name__ == "__main__":
    import uvicorn
    
    server = create_server()
    # Use 0.0.0.0 to accept connections from other Docker containers
    uvicorn.run(server.app, host="0.0.0.0", port=8000)