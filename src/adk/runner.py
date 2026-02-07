"""
ADK Runner - Agent Execution with Session Management

Provides the main interface for running the AI Company agents with:
- Session persistence (SQLite via DatabaseSessionService)
- Memory integration (ChromaDB via HybridMemoryService)
- Async execution with streaming support
"""

import os
import asyncio
import logging
from typing import Optional, Dict, Any, AsyncGenerator, List
from datetime import datetime

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService, DatabaseSessionService, Session
from google.genai.types import Content, Part

from src.adk.agents import create_root_agent, get_agent_info
from src.adk.memory import get_memory_service, HybridMemoryService
from src.adk.models import get_token_callback

logger = logging.getLogger(__name__)


# ============================================================================
# SESSION SERVICE WRAPPER
# ============================================================================

class SessionServiceWrapper(InMemorySessionService):
    """
    Wrapper for InMemorySessionService to make get_session accept positional arguments.
    """

    def get_session(self, app_name, user_id, session_id, config=None):
        return super().get_session(
            app_name=app_name,
            user_id=user_id,
            session_id=session_id,
            config=config
        )


# ============================================================================
# SESSION SERVICE FACTORY
# ============================================================================

def create_session_service():
    """
    Create appropriate session service based on configuration.

    Uses wrapped InMemorySessionService for compatibility.
    """
    logger.info("Using wrapped InMemorySessionService")
    return SessionServiceWrapper()


# ============================================================================
# AI COMPANY RUNNER
# ============================================================================

class AICompanyRunner:
    """
    Main runner for the AI Company agent system.

    Handles:
    - Agent initialization
    - Session management
    - Memory integration
    - Request processing
    """

    APP_NAME = "ai_company"

    def __init__(
        self,
        session_service: Optional[Any] = None,
        memory_service: Optional[HybridMemoryService] = None,
    ):
        """
        Initialize the AI Company runner.

        Args:
            session_service: Custom session service (optional)
            memory_service: Custom memory service (optional)
        """
        logger.info("Initializing AICompanyRunner...")

        # Create services
        self.session_service = session_service or create_session_service()
        self.memory_service = memory_service or get_memory_service()

        # Create root agent with all sub-agents
        self.root_agent = create_root_agent()

        # Create ADK runner
        self.runner = Runner(
            agent=self.root_agent,
            app_name=self.APP_NAME,
            session_service=self.session_service,
            auto_create_session=True,
        )

        logger.info("AICompanyRunner initialized successfully")

    async def process_request(
        self,
        query: str,
        user_id: str = "default",
        session_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Process a user request and return the response.

        Args:
            query: User query/request
            user_id: User identifier
            session_id: Session identifier (auto-generated if not provided)

        Returns:
            Dict with response and metadata
        """
        # Generate session ID if not provided
        if session_id is None:
            session_id = f"session_{int(datetime.utcnow().timestamp())}"

        logger.info(f"Processing request for session {session_id}: {query[:50]}...")

        # Set token tracking context
        token_cb = get_token_callback()
        token_cb.set_context(agent_name="HR_Manager", session_id=session_id, user_id=user_id)

        start_time = datetime.utcnow()

        try:
            # Create user message content
            user_content = Content(
                role="user",
                parts=[Part(text=query)]
            )

            # Run the agent
            response_parts = []
            agents_involved = set()

            async for event in self.runner.run_async(
                user_id=user_id,
                session_id=session_id,
                new_message=user_content,
            ):
                # Extract response from events
                if hasattr(event, 'content') and event.content:
                    if hasattr(event.content, 'parts'):
                        for part in event.content.parts:
                            if hasattr(part, 'text') and part.text:
                                response_parts.append(part.text)

                # Track agents involved and update token context
                if hasattr(event, 'author') and event.author:
                    agents_involved.add(event.author)
                    token_cb.set_context(agent_name=event.author, session_id=session_id, user_id=user_id)

            # Combine response
            response_text = "\n".join(response_parts) if response_parts else "Request processed."

            # Calculate latency
            latency_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)

            # Log token usage for agents that don't go through LiteLLM (e.g., Gemini native)
            # LiteLLM models are tracked automatically via callbacks
            model_provider = os.getenv("MODEL_PROVIDER", "gemini")
            if model_provider == "gemini":
                # Estimate tokens for Gemini (native, not via LiteLLM callbacks)
                estimated_in = len(query.split()) * 2  # rough token estimate
                estimated_out = len(response_text.split()) * 2
                try:
                    from src.adk.tools import log_token_usage
                    log_token_usage(
                        agent_name=", ".join(agents_involved) if agents_involved else "HR_Manager",
                        model_name=os.getenv("GEMINI_MODEL_NAME", "gemini-2.0-flash"),
                        model_provider="gemini",
                        tokens_in=estimated_in,
                        tokens_out=estimated_out,
                        query_preview=query[:500],
                        response_preview=response_text[:500],
                        session_id=session_id,
                        user_id=user_id,
                        latency_ms=latency_ms
                    )
                except Exception as te:
                    logger.warning(f"Token logging failed: {te}")

            # Save to memory
            await self._save_to_memory(session_id, query, response_text)

            return {
                "status": "success",
                "result": response_text,
                "session_id": session_id,
                "user_id": user_id,
                "agents_involved": list(agents_involved),
                "latency_ms": latency_ms,
                "timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Error processing request: {e}")
            return {
                "status": "error",
                "error": str(e),
                "session_id": session_id,
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat()
            }

    async def process_request_streaming(
        self,
        query: str,
        user_id: str = "default",
        session_id: Optional[str] = None,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Process a request with streaming response.

        Args:
            query: User query/request
            user_id: User identifier
            session_id: Session identifier

        Yields:
            Dict with partial response and metadata
        """
        if session_id is None:
            session_id = f"session_{int(datetime.utcnow().timestamp())}"

        logger.info(f"Processing streaming request for session {session_id}")

        try:
            user_content = Content(
                role="user",
                parts=[Part(text=query)]
            )

            response_parts = []

            async for event in self.runner.run_async(
                user_id=user_id,
                session_id=session_id,
                new_message=user_content,
            ):
                if hasattr(event, 'content') and event.content:
                    if hasattr(event.content, 'parts'):
                        for part in event.content.parts:
                            if hasattr(part, 'text') and part.text:
                                response_parts.append(part.text)
                                yield {
                                    "type": "partial",
                                    "content": part.text,
                                    "author": getattr(event, 'author', 'unknown'),
                                    "session_id": session_id
                                }

            # Final event
            full_response = "\n".join(response_parts)
            await self._save_to_memory(session_id, query, full_response)

            yield {
                "type": "complete",
                "content": full_response,
                "session_id": session_id,
                "timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Streaming error: {e}")
            yield {
                "type": "error",
                "error": str(e),
                "session_id": session_id
            }

    async def _save_to_memory(self, session_id: str, query: str, response: str):
        """Save conversation to memory"""
        try:
            self.memory_service.chroma_manager.save_conversation(
                session_id=session_id,
                agent_name="AI_Company",
                user_message=query,
                agent_response=response,
                metadata={
                    "app_name": self.APP_NAME,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
        except Exception as e:
            logger.warning(f"Failed to save to memory: {e}")

    def get_conversation_history(
        self,
        session_id: str,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Get conversation history for a session"""
        return self.memory_service.get_conversation_history(session_id, limit)

    def get_agents_info(self) -> Dict[str, Any]:
        """Get information about all agents"""
        return get_agent_info()

    def get_stats(self) -> Dict[str, Any]:
        """Get runner statistics"""
        memory_stats = self.memory_service.get_stats()
        return {
            "app_name": self.APP_NAME,
            "root_agent": self.root_agent.name,
            "sub_agents": len(self.root_agent.sub_agents),
            "memory": memory_stats
        }


# ============================================================================
# SINGLETON ACCESS
# ============================================================================

_runner: Optional[AICompanyRunner] = None


def create_runner(reset: bool = False) -> AICompanyRunner:
    """
    Create or get the global AICompanyRunner instance.

    Args:
        reset: Force create a new instance

    Returns:
        AICompanyRunner instance
    """
    global _runner

    if reset or _runner is None:
        _runner = AICompanyRunner()
        logger.info("Created new AICompanyRunner instance")

    return _runner


def get_runner() -> AICompanyRunner:
    """Get the global runner instance (creates if needed)"""
    return create_runner()


# ============================================================================
# SYNCHRONOUS WRAPPER
# ============================================================================

class SyncAICompanyRunner:
    """
    Synchronous wrapper for AICompanyRunner.

    Useful for non-async contexts like simple scripts or REPL.
    """

    def __init__(self):
        self._async_runner = create_runner()

    def process_request(
        self,
        query: str,
        user_id: str = "default",
        session_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Process request synchronously"""
        return asyncio.run(
            self._async_runner.process_request(query, user_id, session_id)
        )

    def get_conversation_history(self, session_id: str, limit: int = 20):
        """Get conversation history"""
        return self._async_runner.get_conversation_history(session_id, limit)

    def get_agents_info(self):
        """Get agents info"""
        return self._async_runner.get_agents_info()

    def get_stats(self):
        """Get stats"""
        return self._async_runner.get_stats()


def create_sync_runner() -> SyncAICompanyRunner:
    """Create a synchronous runner for non-async contexts"""
    return SyncAICompanyRunner()


# ============================================================================
# TEST
# ============================================================================

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    async def test_runner():
        print("Testing AICompanyRunner...")
        print("=" * 50)

        try:
            # Create runner
            runner = create_runner()
            print(f"✅ Runner created")
            print(f"   App: {runner.APP_NAME}")
            print(f"   Root agent: {runner.root_agent.name}")
            print(f"   Sub-agents: {len(runner.root_agent.sub_agents)}")

            # Get stats
            stats = runner.get_stats()
            print(f"\n✅ Stats retrieved:")
            print(f"   {stats}")

            # Get agents info
            info = runner.get_agents_info()
            print(f"\n✅ Agents info retrieved:")
            print(f"   Root: {info['root_agent']['name']}")

            # Test a simple request
            print("\n🔄 Testing request processing...")
            result = await runner.process_request(
                query="Hello, what can you help me with?",
                session_id="test_session_001"
            )
            print(f"   Status: {result['status']}")
            if result['status'] == 'success':
                print(f"   Response: {result['result'][:100]}...")

            print("\n✅ All tests passed!")

        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()

    asyncio.run(test_runner())
