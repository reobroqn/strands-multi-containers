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
- AWS credentials (for Bedrock model)

### Run with Docker

```bash
# Copy and edit environment
cp .env.example .env
nano .env

# Start all services
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
- `POST /api/v1/stop/bulk` - Stop multiple chats

### Health
- `GET /health` - Check system status

## Configuration

Edit `.env` file:

```bash
# Server
HOST=0.0.0.0
PORT=8000

# Redis
REDIS_HOST=redis
REDIS_PORT=6379

# AWS Bedrock
AWS_REGION=us-west-2
BEDROCK_MODEL_ID=amazon.nova-lite-v1:0
BEDROCK_TEMPERATURE=0.3

# Logging
LOG_LEVEL=INFO
```

## Local Development

```bash
# Install dependencies
uv sync --extra dev

# Start Redis
docker run -d -p 6379:6379 redis:7-alpine

# Run the app
uv run python -m app.main
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

## Commands

```bash
make start    # Start all services
make stop     # Stop all services
make logs     # View logs
make health   # Check health
make clean    # Remove volumes
```

## Tech Stack

- **FastAPI** - Web framework
- **Strands SDK** - AI agent framework
- **AWS Bedrock** - AI inference
- **Redis** - Signal coordination
- **Docker** - Containerization
- **Nginx** - Load balancing
