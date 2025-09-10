# Project Outline: 2048 Game Implementation

## Project Overview
This is a comprehensive code exercise project to create a 2048 game using Python backend with a NextJS frontend. The project emphasizes programming best practices, modular design, comprehensive testing, and proper documentation.

## Game Context
2048 is a number-based puzzle game featuring:
- A square grid (typically 4x4) containing numbered tiles
- Four directional controls (up, down, left, right) to move all tiles
- **Merge mechanics**: When two tiles with identical numbers collide, they merge into a single tile with their sum
- **Win condition**: Create a tile with the number 2048
- **Loss condition**: No valid moves remain and no 2048 tile exists

## Technical Requirements
- **Architecture**: Modular design with proper separation of concerns
- **Testing**: Comprehensive unit and end-to-end testing
- **Documentation**: Inline documentation and comprehensive README
- **Best Practices**: Follow PEP 8 and modern Python/JavaScript standards

## Implementation Plan

### Phase 1: Python Backend Core Engine

#### 1.1 Game State Management
- **Game States**: Win, Game Over, In Progress
- **Board Management**: 
  - Default 4x4 grid with configurable size support
  - Cell state tracking and validation
- **Score System**: Points calculation and move counter

#### 1.2 Input Processing
Seven input types supported:
- `left`, `right`, `up`, `down` - Directional moves
- `hint` - Request AI assistance
- `redo` - Undo last move (if available)
- `exit` - Manual game termination

#### 1.3 Game Mechanics Engine
- **Movement Logic**: Move all tiles in specified direction until collision
- **Merge Rules**:
  - Two identical tiles merge into their sum
  - **3+ tiles (odd count)**: Merge tiles furthest from move direction
    - Example: `[2,2,2]` + left → `[2,4,null]`
  - **4+ tiles (even count)**: Sequential merge with one merge per tile per move
    - Example: `[2,2,2,2]` + left → `[4,4,null,null]` (no secondary merge)
- **Score Calculation**: 
  - **Base Score**: Points awarded when any two cells merge
  - **Score increment** = sum of merged tiles (e.g., 2+2=4 merge adds 4 points)
  - **Streak System** (optional, configurable):
    - **Streak bonus**: Multiplier applied when player merges on consecutive moves
    - **Streak breaks**: When a move produces no merges
    - **Streak multiplier**: Increases with consecutive successful merges
    - **Default**: Disabled (can be enabled in configuration)
- **Redo System**:
  - **Move History**: Maintains stack of previous game states
  - **Redo Limit**: Configurable number of moves that can be undone
  - **State Preservation**: Each move saves board state, score, and streak status
  - **Redo Restrictions**: Cannot redo after hint usage (optional rule)

#### 1.4 Rendering System
- **Console Output**: Clean ASCII art representation
- **Frontend Rendering**: Fixed-size square cells that scale based on board dimensions
- **Adaptive Layout**: Board container adjusts to accommodate different grid sizes
- **Messaging**: Success/warning notifications
- **Status Display**: Current score, move count, game state, streak status, redos remaining

#### 1.5 Configuration System
**Configurable Parameters:**
- **Board Size**: 
  - Default: 4x4
  - Range: min 3x3, max 12x12
  - Rectangular boards allowed (e.g., 3x6, 4x5)
- **Initial Tile Value**: 
  - Default: 2
  - Range: min 1, max 10
  - **Validation**: Must be less than win condition
- **Initial Tile Numbers**:
  - Default: randbetween(2,4)
  - Range: min 1, max half the board
- **Win Condition Number**: 
  - Default: 2048
  - Range: min 4, max 10000
  - **Win Detection Logic**: Uses `>=` to accommodate configurations where exact target may be unreachable
  - **Validation**: Must be greater than initial tile value
- **Random Tile Generation**: 
  - Default: random between 2-4 per move
  - Range: min 1, max half the board
- **Redo System**:
  - **Default**: 3 redos per game
  - **Range**: min 0 (disabled), max -1 (unlimited)
  - **Behavior**: Maintains move history stack for state restoration
- **Streak System**:
  - **Default**: Disabled
  - **Streak Multiplier**: Configurable bonus percentage per consecutive merge
  - **Streak Reset**: On moves without merges or redo usage
- **Merge Behavior**:
  - Multiple merge allowance per move (configurable)
  - Merge direction priority (furthest vs nearest from move direction)

**Configuration Validation Rules:**
```python
# Ensure viable game setup
if initial_tile_value >= win_condition:
    raise ValueError("Initial tile value must be less than win condition")
if board_width < 3 or board_height < 3:
    raise ValueError("Board dimensions must be at least 3x3")
if board_width > 12 or board_height > 12:
    raise ValueError("Board dimensions cannot exceed 12x12")
if redo_limit < 0:
    raise ValueError("Redo limit cannot be negative")
if streak_multiplier < 0:
    raise ValueError("Streak multiplier cannot be negative")
```

### Phase 1.1: AI Integration
- **Remote AI Service**: Integration with Alibaba Cloud Qwen server
- **Dynamic Context Tracking**: 
  - Current game rules and custom configuration parameters
  - Real-time game state (board, score, move count, streak status)
  - Complete move history with timestamps and redo information
  - Previous AI hints and their outcomes
  - Game difficulty assessment based on board size and rules
- **Intelligent Caching Strategy**:
  - Cache AI responses for identical game states (board + configuration)
  - TTL-based cache with 1-hour expiration
  - Edge case handling for custom configurations
  - Cache invalidation when game rules change
- **Hint System**: Strategic move recommendations with context awareness
- **Console Integration**: `hint` command triggers AI consultation with full context

### Phase 2: NextJS Frontend Development

#### 2.1 Architecture
- **Communication**: HTTP REST API with Python backend
- **State Management**: React state management for game data
- **Responsive Design**: Modern, mobile-friendly interface

#### 2.2 User Interface Components

##### Initial Configuration View
- **Game Mode Selection**:
  - Standard Game (default 4x4, 2048 target)
  - Custom Game (user-configurable parameters)
- **Configuration Panel**:
  - Board size selector
  - Win condition number
  - Initial tile values
  - Merge rule preferences

##### Game Play View
- **Central Game Board**: 
  - Visual grid with animated tiles
  - **Fixed-size square cells** that scale proportionally to board dimensions
  - Responsive container that adapts to different grid sizes (3x3 to 12x12)
  - Support for rectangular layouts with consistent cell sizing
- **Game Statistics Panel**:
  - Current score display (cumulative from all merges + streak bonuses)
  - Move counter and streak status
  - Redos remaining indicator
  - Move history log with redo markers
- **Message System**: Success/warning notifications
- **Game Controls**: Keyboard and touch input support

##### AI Chat Interface
- **Collapsible Chat Box**: Slide-in/out functionality
- **Real-time Communication**: Chat with AI assistant
- **Enhanced Context Delivery**: 
  - AI receives complete game configuration
  - Dynamic context updates with each move
  - Historical context of previous hints and outcomes
- **Hint Integration**: Quick hint request buttons with context-aware responses
- **Smart Caching**: Reduces redundant AI calls for similar game states

### Phase 3: Deployment & DevOps

#### 3.1 Containerization
- **Docker Images**: Separate containers for frontend and backend
- **Docker Compose**: Orchestrated multi-container deployment
- **Image Registry**: GitHub Container Registry for image storage

#### 3.2 Infrastructure
- **Reverse Proxy**: Nginx for frontend serving and API routing
- **Security**: Backend not directly exposed to internet
- **SSL/TLS**: HTTPS termination at proxy level

#### 3.3 CI/CD Pipeline
- **GitHub Actions**: Automated build, test, and deployment
- **Multi-stage Pipeline**:
  1. Code quality checks (linting, formatting)
  2. Unit and integration testing
  3. Docker image building
  4. Deployment to remote server
- **Environment Management**: Separate staging and production deployments

## Project Structure
```
py2048/
├── backend/                 # FastAPI game engine
│   ├── src/
│   │   ├── game/           # Core game logic & merge algorithms
│   │   ├── ai/             # Qwen integration & local hint fallback
│   │   ├── api/            # FastAPI endpoints & rate limiting
│   │   ├── auth/           # Invitation code validation
│   │   ├── cache/          # Simple in-memory AI response cache
│   │   └── config/         # Configuration management
│   ├── tests/              # Pytest test suites
│   ├── requirements.txt    # Python dependencies (FastAPI, httpx, etc.)
│   └── Dockerfile          # Backend container
├── frontend/               # NextJS with React Context + React Query
│   ├── src/
│   │   ├── components/     # React components with Framer Motion
│   │   ├── context/        # React Context for global state
│   │   ├── hooks/          # Custom hooks for React Query
│   │   ├── pages/          # NextJS pages (auth, game, config)
│   │   ├── services/       # API communication with React Query
│   │   └── styles/         # CSS/Tailwind styling
│   ├── __tests__/          # Jest + React Testing Library
│   ├── package.json        # Dependencies (framer-motion, react-query)
│   └── Dockerfile          # Frontend container
├── docs/                   # Project documentation
├── .github/                # CI/CD workflows
└── docker-compose.yml      # Multi-container orchestration
```

## Development Timeline & Milestones

### Sprint 1 (Core Game Engine)
- [ ] FastAPI project setup with basic structure
- [ ] Basic game board and tile management classes
- [ ] Movement and merge algorithms implementation
- [ ] **Redo system**: Move history stack and state restoration
- [ ] **Streak system**: Consecutive merge tracking and scoring
- [ ] Console rendering system for development testing
- [ ] Unit tests for core logic with pytest

### Sprint 2 (Advanced Features & Auth)
- [ ] Configuration system for game parameters
- [ ] Invitation code system with manual code generation
- [ ] AI hint rate limiting (3 per game, max 5 configurable)
- [ ] Simple in-memory cache for AI responses
- [ ] Enhanced console UI and comprehensive test coverage

### Sprint 3 (AI Integration)
- [ ] Alibaba Cloud Qwen integration with error handling
- [ ] Local hint algorithm as fallback strategy
- [ ] AI context management and response validation
- [ ] FastAPI endpoints for hint requests with rate limiting
- [ ] Cache implementation with TTL for repeated game states

### Sprint 4 (Frontend Core)
- [ ] NextJS project setup with TypeScript
- [ ] React Context setup for global game state
- [ ] React Query configuration for API management
- [ ] Basic game board visualization
- [ ] Invitation code entry page and validation

### Sprint 5 (Frontend Polish)
- [ ] Framer Motion animations for tile movements
- [ ] Game statistics panel and move history
- [ ] AI chat interface with hint request buttons
- [ ] Responsive design and keyboard controls
- [ ] Frontend testing with Jest and React Testing Library

### Sprint 6 (Integration & Deployment)
- [ ] Frontend-backend integration testing
- [ ] Docker containerization for both services
- [ ] CI/CD pipeline setup with GitHub Actions
- [ ] Production deployment and documentation
- [ ] End-to-end testing with Cypress

## Technical Considerations & Recommendations

### ✅ Strengths of Your Plan
1. **Well-defined scope**: Clear game mechanics and technical requirements
2. **Modern architecture**: Separation of concerns with Python backend and NextJS frontend
3. **AI integration**: Innovative use of external AI service for game assistance
4. **DevOps ready**: Comprehensive deployment strategy with Docker and CI/CD
5. **Configurable design**: Flexible game parameters for enhanced replayability

### 🔧 Technical Implementation Decisions

#### Backend Architecture
- **Framework**: **FastAPI** for high performance and automatic API documentation
- **AI Response Caching**: Simple in-memory cache (Python dict with TTL) - Redis would be overkill for this project scope
- **Rate Limiting**: Built-in hint limiting system (default: 3 hints per game, max configurable: 5 hints)
- **Data Storage**: No persistent storage for this project version (see Future Improvements)
- **Access Control**: Invitation code system for gated access (manually generated codes)

#### Frontend Architecture
- **State Management**: **React Context** for global game state management
- **API Management**: **React Query** for efficient API call handling, caching, and synchronization
- **Animations**: **Framer Motion** for smooth tile movements and transitions
- **Authentication**: Simple invitation code entry on first visit
- **Accessibility**: WCAG compliance for keyboard navigation and screen readers

#### AI Integration Implementation
- **Cost Control**: Default 3 hints per game session, configurable up to 5 hints maximum
- **Advanced Caching Strategy**: 
  - In-memory cache for AI responses to identical game states (TTL: 1 hour)
  - Cache key includes board state + configuration parameters
  - **Edge case optimization**: Special handling for custom configurations
  - Cache invalidation on rule changes
- **Dynamic Context Management**:
  - **Complete Game Context**: Board state, score, move history, configuration
  - **Historical Tracking**: Previous hints and their effectiveness
  - **Adaptive Responses**: AI considers board size and custom rules
- **Fallback Strategy**: Local hint algorithm when AI service is unavailable
- **Response Validation**: Validate AI responses against current game rules and constraints
- **Security**: Secure API key management through environment variables

#### Testing Strategy
- **Backend**: Use `pytest` with high coverage requirements (>90%)
- **Frontend**: Combine `Jest` + `React Testing Library` + `Cypress` for E2E
- **Configuration Validation**: Test all parameter constraints and edge cases
- **Score Calculation**: Verify scoring accuracy across different merge scenarios and streak bonuses
- **Redo System**: Test move history management, state restoration, and limit enforcement
- **Streak System**: Validate streak calculation, multiplier application, and reset conditions
- **Board Rendering**: Test UI scaling for various board dimensions (3x3 to 12x12)
- **AI Context Delivery**: Validate complete context transmission to AI service
- **Load testing**: Test AI integration under concurrent users with rate limiting
- **Game logic validation**: Extensive edge case testing for merge algorithms
- **Invitation system**: Test access control and code validation

#### Deployment & Security
- **Environment variables**: Secure management of API keys and invitation codes
- **Health checks**: Implement container health monitoring
- **Access Control**: Invitation-only access with manually generated codes
- **Monitoring**: Basic logging for development and debugging

### 🚨 Potential Challenges

1. **Complex merge logic**: The multi-tile merge rules are intricate - invest time in thorough testing
2. **AI reliability**: External API dependency may cause latency/availability issues
3. **State synchronization**: Ensure React Context and React Query work seamlessly together
4. **Performance considerations**: 
   - Large board sizes (12x12) may impact Framer Motion animation performance
   - Fixed-size cells need efficient rendering for various board dimensions
5. **Rate limiting enforcement**: Ensure hint limits persist across page refreshes (session storage)
6. **Dynamic context management**: Efficiently tracking and transmitting complete game context to AI
7. **Configuration validation**: Ensure robust validation prevents impossible game setups
8. **Redo state management**: Maintaining accurate game state history without memory bloat
9. **Streak calculation complexity**: Ensuring streak bonuses calculate correctly across different scenarios

### � Future Improvement Plans

#### Phase 4: Data Persistence & Analytics
- **Database Integration**: Add SQLite/PostgreSQL for game statistics and user sessions
- **User Accounts**: Replace invitation codes with proper user authentication
- **Game History**: Persistent storage of completed games and personal records
- **Leaderboards**: Global and personal best scores tracking
- **Statistics Dashboard**: Detailed analytics on playing patterns and improvement

#### Phase 5: Enhanced Features
- **PWA Capabilities**: Make it installable as a Progressive Web App
- **Theme System**: Multiple visual themes and tile designs
- **Advanced AI**: More sophisticated hint algorithms and difficulty levels
- **Social Features**: Share scores and game replays
- **Backup & Sync**: Cloud save functionality for game progress

#### Phase 6: Scalability & Production
- **Redis Caching**: Upgrade to Redis for distributed caching
- **Advanced Monitoring**: Prometheus/Grafana for production metrics
- **Load Balancing**: Multiple backend instances for high availability
- **CDN Integration**: Global content delivery for frontend assets
- **Advanced Security**: Rate limiting, DDoS protection, and security headers

#### Phase 7: Platform Expansion
- **Mobile App**: React Native version for native mobile experience
- **Multiplayer Mode**: Real-time competitive gameplay
- **Tournament System**: Organized competitions and events
- **API Marketplace**: Public API for third-party integrations

### 💡 Current Project Scope Limitations

**Intentionally Excluded for V1:**
- Persistent data storage (games reset on refresh)
- User accounts and authentication (invitation code only)
- Advanced caching (simple in-memory cache)
- Production-grade monitoring
- Social features and sharing
- Advanced AI training and optimization