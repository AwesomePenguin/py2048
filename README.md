# 2048 Game - Enhanced Edition

[![CI/CD Pipeline](https://github.com/AwesomePenguin/py2048/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/AwesomePenguin/py2048/actions/workflows/ci-cd.yml)
[![Docker](https://img.shields.io/badge/Docker-Enabled-blue)](https://ghcr.io/awesomepenguin)
[![Python](https://img.shields.io/badge/Python-3.11+-green)](https://python.org)
[![Next.js](https://img.shields.io/badge/Next.js-15+-black)](https://nextjs.org)

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

## 🎯 Key Highlights

### Smart AI Integration
- **Context-aware hints**: AI understands your current board state and game rules
- **Cost-controlled**: Limited hints per game (3 default, max 5)

### Flexible Configuration
- **Board Dimensions**: Any size from 3x3 to 12x12
- **Win Targets**: Customize victory conditions
- **Tile Generation**: Control how many and which tiles spawn
- **Scoring System**: Optional streak bonuses and multipliers
- **Redo Limits**: From no redos to unlimited undos

### Modern Interface
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Real-time Updates**: Live score, streak, and statistics tracking

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

## 🎮 How to Play (Console Mode)

### Commands
- **UP**: move up
- **DOWN**: move down
- **LEFT**: move left
- **RIGHT**: move right
- **HINT**: request for AI hint (subject to limits)
- **REDO**: undo the last move
- **EXIT**: end the game

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
cd backend/test
python run_tests.py
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

The project includes comprehensive deployment automation:

### Automated Deployment
- **🐳 Docker Containers**: Optimized images for frontend and backend
- **🔄 GitHub Actions**: Automated CI/CD pipeline with testing and deployment
- **📦 GHCR**: Container images stored in GitHub Container Registry
- **🌐 Docker Compose**: Production-ready orchestration with Nginx
- **🔒 Security**: Health checks, rate limiting, and SSL-ready configuration

## 🎮 Play Online

Ask the admin for access

## 📄 License

This project is open source. See LICENSE file for details.

---

**Ready to challenge yourself?** Start with a standard game or create your own custom rules for the ultimate 2048 experience!
