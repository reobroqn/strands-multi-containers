# FastAPI Agent Chat

A multi-container FastAPI application with an AI agent that can be stopped immediately using Redis as a signal bus.

## Architecture

```
Client → Nginx (port 80) → 3x FastAPI (port 8000) → Redis (port 6379)
```

The system uses Redis to coordinate stop signals across multiple backend instances, allowing the agent to be halted within 100ms.

## Quick Start

### Prerequisites
- Docker and Docker Compose

### Run with Docker

```bash
# Copy and edit environment
cp .env.example .env
nano .env

# Start all services
make build

make start

# Access the app
open http://localhost
```

### Test Stop Functionality

1. Open http://localhost in your browser
2. Enter a chat ID and send a message
3. Click "Stop Agent" while it's responding
4. The agent stops within ~100ms

## API Endpoints

### Chat
- `POST /api/v1/chat/{chat_id}` - Start chat (SSE streaming)
- `GET /api/v1/chat/{chat_id}` - Get chat status
- `DELETE /api/v1/chat/{chat_id}` - Delete chat

### Stop
- `POST /api/v1/stop/{chat_id}` - Stop single chat

## Local Development

```bash
# Install dependencies
uv sync --extra dev

# Start Redis
docker run -d -p 6379:6379 redis:7-alpine

# Run the app
uv run fastapi dev src/main.py
```

## Project Structure

```
app/
├── agent/agent_core.py      # AI agent with stop capability
├── api/chat.py             # Chat endpoints
├── api/stop.py             # Stop endpoints
├── services/redis_client.py # Redis signal bus
├── config.py               # Configuration
└── main.py                 # FastAPI app
```

## Tech Stack

- **FastAPI** - Web framework
- **Strands SDK** - AI agent framework
- **Redis** - Signal coordination
- **Docker** - Containerization
- **Nginx** - Load balancing
