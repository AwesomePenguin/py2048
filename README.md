# 2048 Game - Enhanced Edition

An advanced implementation of the classic 2048 puzzle game with AI assistance, customizable rules, and modern web interface.

## 🎮 Game Features

### Core Gameplay
- **Classic 2048 mechanics** with smooth tile sliding and merging
- **Flexible board sizes**: From 3x3 to 12x12, including rectangular boards (e.g., 3x6, 4x5)
- **Configurable win conditions**: Set your target from 4 to 10,000
- **Custom tile values**: Choose initial tile values and spawn patterns

### Advanced Features
- **🤖 AI Assistant**: Get strategic hints powered by Alibaba Cloud Qwen AI
- **↩️ Redo System**: Undo moves with configurable limits (0 to unlimited)
- **🔥 Streak Scoring**: Bonus points for consecutive successful merges
- **🎯 Custom Merge Rules**: Standard or reverse merge priorities
- **📊 Detailed Statistics**: Track score, moves, streaks, and game history

### Gameplay Modes
- **Standard Game**: Classic 4x4 board with 2048 target
- **Custom Game**: Fully configurable parameters for unique challenges
- **Practice Mode**: Unlimited redos for learning optimal strategies

## 🎯 Key Highlights

### Smart AI Integration
- **Context-aware hints**: AI understands your current board state and game rules
- **Strategic recommendations**: Get suggestions for optimal next moves
- **Cost-controlled**: Limited hints per game (3 default, max 5)
- **Fallback system**: Local hints when AI service is unavailable

### Flexible Configuration
- **Board Dimensions**: Any size from 3x3 to 12x12
- **Win Targets**: Customize victory conditions
- **Tile Generation**: Control how many and which tiles spawn
- **Scoring System**: Optional streak bonuses and multipliers
- **Redo Limits**: From no redos to unlimited undos

### Modern Interface
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Smooth Animations**: Fluid tile movements and merge effects
- **Real-time Updates**: Live score, streak, and statistics tracking
- **Intuitive Controls**: Keyboard arrows, touch gestures, or on-screen buttons

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+

### Running the Game
```bash
# Backend (Game Engine)
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python server.py

# Frontend (Web Interface)
cd frontend
npm install
npm run dev
```

Visit `http://localhost:3000` to play!

## 🎮 How to Play

1. **Start**: Choose standard or custom game mode
2. **Move**: Use arrow keys or swipe to move tiles
3. **Merge**: Identical tiles combine when they collide
4. **Hint**: Ask the AI for strategic advice (limited uses)
5. **Redo**: Undo moves if enabled in your configuration
6. **Win**: Reach your target tile value (default: 2048)

### Game Controls
- **Arrow Keys**: Move tiles in any direction
- **H**: Request AI hint
- **U**: Undo last move (if redos available)
- **R**: Restart game
- **ESC**: Return to main menu

## 🏗️ Technical Overview

Built with modern technologies for performance and scalability:
- **Backend**: Python with FastAPI for high-performance game engine
- **Frontend**: NextJS with React for responsive user interface
- **AI Integration**: Alibaba Cloud Qwen for intelligent hints
- **Deployment**: Docker containers with GitHub Actions CI/CD

## 📁 Project Structure

```
├── backend/           # Python game engine and AI integration
├── frontend/          # NextJS web interface
├── docs/             # Detailed technical documentation
├── .github/          # CI/CD workflows and project automation
└── README.md         # This file
```

## 🎲 Game Examples

### Custom Configurations
- **Speed Run**: 3x3 board, target 64, unlimited redos
- **Challenge Mode**: 6x6 board, target 4096, no redos, streak scoring
- **Learning Mode**: Standard 4x4, unlimited and redos
- **Expert Level**: 5x8 board, custom tile values, reverse merge strategy

## 🔧 Configuration Options

| Setting | Default | Range | Description |
|---------|---------|-------|-------------|
| Board Size | 4x4 | 3x3 to 12x12 | Game grid dimensions |
| Win Target | 2048 | 4 to 10,000 | Victory condition |
| Initial Tiles | 2-4 | 1 to 10 | Starting tile values |
| Redos | 3 | 0 to unlimited | Undo moves allowed |
| AI Hints | 3 | 0 to 5 | Hint requests per game |
| Streak Bonus | Off | 0-100% | Consecutive merge bonus |

## 🧪 Development & Testing

Run tests to ensure game logic and interface work correctly:

### Backend Tests
```bash
cd backend
python -m pytest
```

### Frontend Tests
```bash
cd frontend
npm run test
```

## 📚 Documentation

For detailed technical information, development guidelines, and implementation details:
- **[Project Outline](docs/project-outline.md)** - Complete technical specification
- **[Game Rules](docs/project-outline.md#game-context)** - Detailed gameplay mechanics
- **[Configuration Guide](docs/project-outline.md#configuration-system)** - All customization options

## 🚀 Deployment

The project includes automated deployment with Docker and GitHub Actions:
- **Containerized**: Both frontend and backend run in Docker containers
- **CI/CD Pipeline**: Automated testing, building, and deployment
- **Production Ready**: Nginx reverse proxy, SSL termination, health monitoring

## 🤝 Contributing

We welcome contributions! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 🎮 Play Online

*[Deployment URL will be added once live]*

## 📄 License

This project is open source. See LICENSE file for details.

---

**Ready to challenge yourself?** Start with a standard game or create your own custom rules for the ultimate 2048 experience!
