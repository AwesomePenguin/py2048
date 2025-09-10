"""
FastAPI server for 2048 game
Demonstrates how the Game class integrates with web APIs
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import uvicorn

# This would import your Game class
# from game import Game

app = FastAPI(title="2048 Game API", version="1.0.0")

# Global game instance (in production, you'd use sessions/database)
game_instance = None

class GameConfig(BaseModel):
    size_x: int = 4
    size_y: int = 4
    win_value: int = 2048
    max_redo: int = 3
    number_of_hints: int = 3
    use_streak: bool = False

class MoveRequest(BaseModel):
    direction: str

@app.post("/game/new")
async def create_game(config: Optional[GameConfig] = None):
    """Create a new game with optional configuration"""
    global game_instance
    
    config_dict = config.dict() if config else {}
    config_dict['output_mode'] = 'web'  # Force web mode
    
    # game_instance = Game(config_dict)
    # return game_instance.get_api_state()
    
    return {"message": "Game created", "config": config_dict}

@app.get("/game/state")
async def get_game_state():
    """Get current game state"""
    if not game_instance:
        raise HTTPException(status_code=404, detail="No active game")
    
    return game_instance.get_api_state()

@app.post("/game/move")
async def make_move(move: MoveRequest):
    """Make a move in the specified direction"""
    if not game_instance:
        raise HTTPException(status_code=404, detail="No active game")
    
    if move.direction not in ['up', 'down', 'left', 'right']:
        raise HTTPException(status_code=400, detail="Invalid direction")
    
    success = game_instance.handle_move(move.direction)
    if not success:
        raise HTTPException(status_code=400, detail="Invalid move")
    
    return game_instance.get_api_state()

@app.post("/game/redo")
async def redo_move():
    """Undo the last move"""
    if not game_instance:
        raise HTTPException(status_code=404, detail="No active game")
    
    success = game_instance.handle_redo()
    if not success:
        return {"error": game_instance.display_message}
    
    return game_instance.get_api_state()

@app.post("/game/hint")
async def get_hint():
    """Request a hint from the AI"""
    if not game_instance:
        raise HTTPException(status_code=404, detail="No active game")
    
    success = game_instance.handle_hint()
    if not success:
        return {"error": game_instance.display_message}
    
    return game_instance.get_api_state()

@app.delete("/game")
async def end_game():
    """End the current game"""
    global game_instance
    game_instance = None
    return {"message": "Game ended"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
