"""
Hybrid Memory Service - ADK Memory backed by ChromaDB

Combines ADK's memory interface with ChromaDB for persistent vector storage.
Provides semantic search capabilities across conversations and knowledge.
"""

import os
import json
import logging
from typing import Optional, List, Dict, Any, AsyncGenerator
from datetime import datetime

logger = logging.getLogger(__name__)


class HybridMemoryService:
    """
    ADK-compatible memory service backed by ChromaDB.

    This service implements the ADK memory interface while using
    ChromaDB for persistent vector storage and semantic search.
    """

    def __init__(self, persist_directory: Optional[str] = None):
        """
        Initialize hybrid memory service.

        Args:
            persist_directory: Directory for ChromaDB persistence.
                              Defaults to MEMORY_PERSIST_DIRECTORY env var.
        """
        self.persist_directory = persist_directory or os.getenv(
            "MEMORY_PERSIST_DIRECTORY",
            "./data/memory"
        )

        # Lazy load ChromaDB manager
        self._chroma_manager = None
        logger.info(f"HybridMemoryService initialized with persist_directory: {self.persist_directory}")

    @property
    def chroma_manager(self):
        """Lazy load ChromaDB manager"""
        if self._chroma_manager is None:
            from src.memory_manager import LocalMemoryManager
            self._chroma_manager = LocalMemoryManager(self.persist_directory)
        return self._chroma_manager

    async def add_session_to_memory(self, session: Any) -> None:
        """
        Extract and store relevant information from a completed session.

        This is called when a conversation session ends to save
        important information for future retrieval.

        Args:
            session: ADK Session object containing conversation history
        """
        try:
            # Extract session data
            session_id = getattr(session, 'id', str(datetime.utcnow().timestamp()))
            user_id = getattr(session, 'user_id', 'default')
            app_name = getattr(session, 'app_name', 'ai_company')

            # Get conversation events
            events = getattr(session, 'events', [])

            # Extract user messages and agent responses
            conversation_text = []
            for event in events:
                author = getattr(event, 'author', 'unknown')
                content = getattr(event, 'content', None)

                if content:
                    # Handle different content formats
                    if hasattr(content, 'parts'):
                        for part in content.parts:
                            if hasattr(part, 'text'):
                                conversation_text.append(f"{author}: {part.text}")
                    elif isinstance(content, str):
                        conversation_text.append(f"{author}: {content}")
                    elif isinstance(content, dict) and 'text' in content:
                        conversation_text.append(f"{author}: {content['text']}")

            if conversation_text:
                # Save to ChromaDB
                combined_text = "\n".join(conversation_text)

                self.chroma_manager.save_conversation(
                    session_id=session_id,
                    agent_name=app_name,
                    user_message=conversation_text[0] if conversation_text else "",
                    agent_response=combined_text,
                    metadata={
                        "user_id": user_id,
                        "app_name": app_name,
                        "timestamp": datetime.utcnow().isoformat(),
                        "event_count": len(events)
                    }
                )

                logger.info(f"Session {session_id} saved to memory ({len(conversation_text)} messages)")

        except Exception as e:
            logger.error(f"Error saving session to memory: {e}")

    async def search_memory(
        self,
        query: str,
        app_name: Optional[str] = None,
        user_id: Optional[str] = None,
        num_results: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search memory for relevant information.

        Args:
            query: Search query
            app_name: Filter by application name (optional)
            user_id: Filter by user ID (optional)
            num_results: Maximum number of results

        Returns:
            List of relevant memory entries
        """
        try:
            results = []

            # Search conversations
            conv_results = self.chroma_manager.search_conversations(
                query=query,
                n_results=num_results
            )
            results.extend(conv_results)

            # Search knowledge base
            kb_results = self.chroma_manager.search_knowledge(
                query=query,
                n_results=num_results
            )
            results.extend(kb_results)

            # Deduplicate and sort by relevance
            seen = set()
            unique_results = []
            for result in results:
                content = result.get('content', '')
                if content not in seen:
                    seen.add(content)
                    unique_results.append(result)

            # Sort by relevance score if available
            unique_results.sort(
                key=lambda x: x.get('relevance_score', x.get('similarity', 0)),
                reverse=True
            )

            return unique_results[:num_results]

        except Exception as e:
            logger.error(f"Error searching memory: {e}")
            return []

    def save_knowledge(
        self,
        knowledge_id: str,
        title: str,
        content: str,
        category: str,
        tags: Optional[List[str]] = None,
        source: Optional[str] = None
    ) -> str:
        """
        Save knowledge to the knowledge base.

        Args:
            knowledge_id: Unique identifier
            title: Knowledge title
            content: Knowledge content
            category: Category for organization
            tags: Optional list of tags
            source: Optional source reference

        Returns:
            Knowledge ID
        """
        return self.chroma_manager.save_knowledge(
            knowledge_id=knowledge_id,
            title=title,
            content=content,
            category=category,
            tags=tags,
            source=source
        )

    def search_knowledge(
        self,
        query: str,
        category: Optional[str] = None,
        n_results: int = 5
    ) -> List[Dict]:
        """
        Search the knowledge base.

        Args:
            query: Search query
            category: Filter by category (optional)
            n_results: Maximum number of results

        Returns:
            List of matching knowledge entries
        """
        return self.chroma_manager.search_knowledge(
            query=query,
            category=category,
            n_results=n_results
        )

    def get_conversation_history(
        self,
        session_id: str,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Get conversation history for a session.

        Args:
            session_id: Session identifier
            limit: Maximum number of messages

        Returns:
            List of conversation entries
        """
        return self.chroma_manager.get_conversation_history(
            session_id=session_id,
            limit=limit
        )

    def save_agent_output(
        self,
        output_id: str,
        agent_name: str,
        task: str,
        output: str,
        output_type: str = "text",
        success: bool = True,
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Save agent output for tracking.

        Args:
            output_id: Unique output identifier
            agent_name: Name of the agent
            task: Task description
            output: Output content
            output_type: Type of output (text, code, report, etc.)
            success: Whether the task succeeded
            metadata: Additional metadata

        Returns:
            Output ID
        """
        return self.chroma_manager.save_agent_output(
            output_id=output_id,
            agent_name=agent_name,
            task=task,
            output=output,
            output_type=output_type,
            success=success,
            metadata=metadata
        )

    def get_stats(self) -> Dict[str, int]:
        """Get memory statistics"""
        return self.chroma_manager.get_stats()

    def health_check(self) -> Dict[str, Any]:
        """Check memory service health"""
        return self.chroma_manager.health_check()


# ============================================================================
# MEMORY TOOL FOR AGENTS
# ============================================================================

class MemoryTool:
    """
    Tool wrapper for memory operations.

    This class provides a tool interface for agents to interact
    with the memory service.
    """

    def __init__(self, memory_service: Optional[HybridMemoryService] = None):
        self.memory_service = memory_service or HybridMemoryService()

    async def load_memory(self, query: str) -> Dict[str, Any]:
        """
        Load relevant memories for a query.

        Args:
            query: Query to search for relevant memories

        Returns:
            Dict with relevant memory entries
        """
        results = await self.memory_service.search_memory(query)

        formatted_results = []
        for result in results:
            formatted_results.append({
                "content": result.get('content', '')[:500],
                "metadata": result.get('metadata', {}),
                "relevance": result.get('relevance_score', result.get('similarity', 0))
            })

        return {
            "status": "success",
            "query": query,
            "memories": formatted_results,
            "count": len(formatted_results)
        }

    def save_memory(self, content: str, category: str = "general") -> Dict[str, Any]:
        """
        Save content to memory.

        Args:
            content: Content to save
            category: Category for organization

        Returns:
            Dict with save status
        """
        knowledge_id = f"mem_{hash(content) % 1000000}"

        self.memory_service.save_knowledge(
            knowledge_id=knowledge_id,
            title="Agent Memory",
            content=content,
            category=category
        )

        return {
            "status": "success",
            "message": "Memory saved successfully",
            "knowledge_id": knowledge_id
        }


# ============================================================================
# SINGLETON ACCESS
# ============================================================================

_memory_service: Optional[HybridMemoryService] = None


def get_memory_service(
    persist_directory: Optional[str] = None,
    reset: bool = False
) -> HybridMemoryService:
    """
    Get or create shared memory service instance.

    Args:
        persist_directory: Custom persist directory (optional)
        reset: Force recreate the instance

    Returns:
        HybridMemoryService instance
    """
    global _memory_service

    if reset or _memory_service is None:
        _memory_service = HybridMemoryService(persist_directory)
        logger.info(f"Memory service initialized: {_memory_service}")

    return _memory_service


def reset_memory_service():
    """Reset the global memory service instance"""
    global _memory_service
    _memory_service = None
    logger.info("Memory service reset")


# ============================================================================
# TEST
# ============================================================================

if __name__ == "__main__":
    import asyncio

    async def test_memory():
        print("Testing HybridMemoryService...")
        print("=" * 50)

        # Initialize
        memory = get_memory_service()

        # Test save
        print("\nSaving test knowledge...")
        memory.save_knowledge(
            knowledge_id="test_001",
            title="Test Knowledge",
            content="This is a test knowledge entry about AI agents.",
            category="test"
        )
        print("✅ Knowledge saved")

        # Test search
        print("\nSearching memory...")
        results = await memory.search_memory("AI agents")
        print(f"✅ Found {len(results)} results")

        # Test stats
        print("\nMemory stats:")
        stats = memory.get_stats()
        for key, value in stats.items():
            print(f"  {key}: {value}")

        # Health check
        print("\nHealth check:")
        health = memory.health_check()
        print(f"  Status: {health['status']}")

        print("\n✅ All tests passed!")

    asyncio.run(test_memory())
