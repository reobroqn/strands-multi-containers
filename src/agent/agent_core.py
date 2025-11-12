from collections.abc import AsyncGenerator

from loguru import logger
from strands import Agent
from strands.models.gemini import GeminiModel
from strands.session import FileSessionManager
from strands_tools import calculator, stop

from src.config import settings
from src.services.redis_client import RedisClient


class AgentOrchestrator:
    """Simplified agent orchestrator using Strands SDK properly"""

    def __init__(self, chat_id: str):
        self.chat_id = chat_id
        self.requested_stop = False

        # Setup session management
        import os

        os.makedirs(settings.session_dir, exist_ok=True)
        self.session_manager = FileSessionManager(
            session_id=chat_id, storage_dir=settings.session_dir
        )

        # Create model
        self.model = GeminiModel(
            client_args={
                "api_key": settings.gemini_api_key,
            },
            model_id=settings.gemini_model,
            params={
                # some sample model parameters
                "temperature": 0.7,
                "max_output_tokens": 2048,
                "top_p": 0.9,
                "top_k": 40,
            },
        )

    async def stream_response(self, message: str) -> AsyncGenerator[str]:
        """Stream agent response with stop signal checking

        Args:
            message: User message to process

        Yields:
            Response chunks from the agent
        """
        logger.info(f"chat_id=<{self.chat_id}> | Processing message: {message[:100]}")

        # Create agent with Bedrock model, tools, and session management
        agent = Agent(
            agent_id=self.chat_id,
            model=self.model,
            tools=[calculator, stop],  # Use built-in stop tool
            session_manager=self.session_manager,
            system_prompt=(
                "You are a helpful AI assistant. You must follow if user ask you to count from 1 to 1000."
            ),
        )

        logger.info("Starting agent stream")

        # Stream agent response
        async for event in agent.stream_async(message):
            # If already stopped, skip all event processing
            if self.requested_stop:
                continue

            # Check for stop signal during streaming
            if await self._check_stop():
                logger.info(f"chat_id=<{self.chat_id}> | Stop detected during streaming")
                agent.tool.stop()
                yield "[STOPPED]"
                continue  # Skip processing this event after stopping

            logger.info(event)

            if "data" in event:
                yield event["data"]

        logger.info(f"chat_id=<{self.chat_id}> | Processing complete")

    async def _check_stop(self) -> bool:
        """Check if stop signal was sent via Redis

        Returns:
            True if stop was requested
        """
        if self.requested_stop:
            return True

        try:
            stop_detected = await RedisClient.check_stop_signal(self.chat_id)
            if stop_detected:
                self.requested_stop = True
                return True
        except Exception as e:
            logger.error(f"chat_id=<{self.chat_id}> | Failed to check stop: {e}")

        return False
