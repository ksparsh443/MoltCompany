"""
Memory Manager - Enhanced Local Vector Store using ChromaDB
Handles conversation history, agent memory, and knowledge base
"""
import os
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from contextlib import contextmanager
import chromadb
from chromadb.config import Settings as ChromaSettings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MemoryException(Exception):
    """Custom exception for memory operations"""
    pass


class LocalMemoryManager:
    """
    Enhanced local memory management using ChromaDB
    - Persistent vector storage
    - Semantic search capabilities
    - Multiple collection types
    - Automatic timestamping and metadata
    """
    
    # Collection names as constants
    CONVERSATIONS = "conversations"
    PROJECTS = "projects"
    EMPLOYEES = "employees"
    KNOWLEDGE = "knowledge"
    AGENT_OUTPUTS = "agent_outputs"
    
    def __init__(
        self,
        persist_directory: str = "./data/memory",
        embedding_function: Optional[Any] = None
    ):
        """
        Initialize Memory Manager
        
        Args:
            persist_directory: Directory to store the vector database
            embedding_function: Custom embedding function (optional)
        """
        self.persist_directory = persist_directory
        self._ensure_directory()
        
        try:
            # Use new PersistentClient (ChromaDB 0.4+)
            self.client = chromadb.PersistentClient(
                path=persist_directory,
                settings=ChromaSettings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            logger.info(f"✅ ChromaDB initialized at: {persist_directory}")
        except Exception as e:
            raise MemoryException(f"Failed to initialize ChromaDB: {e}")
        
        # Initialize collections with metadata
        self.collections = self._initialize_collections(embedding_function)
    
    def _ensure_directory(self):
        """Create persist directory if it doesn't exist"""
        try:
            os.makedirs(self.persist_directory, exist_ok=True)
        except Exception as e:
            raise MemoryException(f"Cannot create directory {self.persist_directory}: {e}")
    
    def _initialize_collections(
        self,
        embedding_function: Optional[Any] = None
    ) -> Dict[str, Any]:
        """Initialize or get all collections"""
        collections = {}
        collection_configs = {
            self.CONVERSATIONS: "User and agent conversation history",
            self.PROJECTS: "Project information and tracking",
            self.EMPLOYEES: "Employee records and skills",
            self.KNOWLEDGE: "Company knowledge base",
            self.AGENT_OUTPUTS: "Agent task outputs and artifacts"
        }
        
        for name, description in collection_configs.items():
            try:
                collections[name] = self.client.get_or_create_collection(
                    name=name,
                    metadata={
                        "description": description,
                        "hnsw:space": "cosine"  # Cosine similarity for semantic search
                    },
                    embedding_function=embedding_function
                )
                logger.info(f"✓ Collection '{name}' ready")
            except Exception as e:
                logger.error(f"Failed to create collection '{name}': {e}")
                raise MemoryException(f"Collection initialization failed: {e}")
        
        return collections
    
    @contextmanager
    def _safe_operation(self, operation_name: str):
        """Context manager for safe database operations"""
        try:
            yield
            logger.debug(f"Operation '{operation_name}' completed")
        except Exception as e:
            logger.error(f"Operation '{operation_name}' failed: {e}")
            raise MemoryException(f"{operation_name} failed: {e}")
    
    # ==================== CONVERSATION METHODS ====================
    
    def save_conversation(
        self,
        session_id: str,
        agent_name: str,
        user_message: str,
        agent_response: str,
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Save a conversation turn
        
        Returns:
            Document ID of saved conversation
        """
        timestamp = datetime.utcnow()
        doc_id = f"{session_id}_{int(timestamp.timestamp() * 1000)}"
        
        document = f"User: {user_message}\n{agent_name}: {agent_response}"
        
        meta = {
            "session_id": session_id,
            "agent_name": agent_name,
            "timestamp": timestamp.isoformat(),
            "message_length": len(user_message) + len(agent_response),
            **(metadata or {})
        }
        
        with self._safe_operation("save_conversation"):
            self.collections[self.CONVERSATIONS].add(
                documents=[document],
                metadatas=[meta],
                ids=[doc_id]
            )
        
        logger.info(f"💬 Conversation saved: {doc_id[:16]}...")
        return doc_id
    
    def get_conversation_history(
        self,
        session_id: str,
        limit: int = 20,
        include_metadata: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Retrieve conversation history for a session
        
        Args:
            session_id: Unique session identifier
            limit: Maximum number of messages to retrieve
            include_metadata: Include metadata in results
        
        Returns:
            List of conversation entries
        """
        try:
            results = self.collections[self.CONVERSATIONS].get(
                where={"session_id": session_id},
                limit=limit
            )
            
            history = []
            if results and results['documents']:
                for i, doc in enumerate(results['documents']):
                    entry = {"content": doc}
                    if include_metadata and results['metadatas']:
                        entry["metadata"] = results['metadatas'][i]
                    history.append(entry)
            
            # Sort by timestamp
            if include_metadata:
                history.sort(key=lambda x: x.get('metadata', {}).get('timestamp', ''))
            
            return history
        except Exception as e:
            logger.error(f"Failed to get conversation history: {e}")
            return []
    
    def search_conversations(
        self,
        query: str,
        session_id: Optional[str] = None,
        n_results: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Semantic search across conversations
        
        Args:
            query: Search query
            session_id: Filter by session (optional)
            n_results: Number of results to return
        """
        where_filter = {"session_id": session_id} if session_id else None
        
        try:
            results = self.collections[self.CONVERSATIONS].query(
                query_texts=[query],
                n_results=n_results,
                where=where_filter
            )
            
            matches = []
            if results and results['documents']:
                for docs, metas, distances in zip(
                    results['documents'][0],
                    results['metadatas'][0],
                    results['distances'][0]
                ):
                    matches.append({
                        "content": docs,
                        "metadata": metas,
                        "similarity": 1 - distances  # Convert distance to similarity
                    })
            
            return matches
        except Exception as e:
            logger.error(f"Conversation search failed: {e}")
            return []
    
    def clear_session(self, session_id: str) -> int:
        """Delete all conversations for a session"""
        try:
            # Get all IDs for this session
            results = self.collections[self.CONVERSATIONS].get(
                where={"session_id": session_id}
            )
            
            if results and results['ids']:
                self.collections[self.CONVERSATIONS].delete(ids=results['ids'])
                count = len(results['ids'])
                logger.info(f"🗑️ Cleared {count} messages from session {session_id}")
                return count
            return 0
        except Exception as e:
            logger.error(f"Failed to clear session: {e}")
            return 0
    
    # ==================== PROJECT METHODS ====================
    
    def save_project(
        self,
        project_id: str,
        project_name: str,
        description: str,
        assigned_agents: List[str],
        status: str = "active",
        additional_metadata: Optional[Dict] = None
    ) -> str:
        """Save or update project information"""
        document = f"{project_name}: {description}"
        
        metadata = {
            "project_id": project_id,
            "project_name": project_name,
            "assigned_agents": json.dumps(assigned_agents),
            "status": status,
            "created_at": datetime.utcnow().isoformat(),
            "agent_count": len(assigned_agents),
            **(additional_metadata or {})
        }
        
        with self._safe_operation("save_project"):
            # Check if project exists, update or create
            try:
                self.collections[self.PROJECTS].delete(ids=[project_id])
            except:
                pass  # Project doesn't exist yet
            
            self.collections[self.PROJECTS].add(
                documents=[document],
                metadatas=[metadata],
                ids=[project_id]
            )
        
        logger.info(f"📁 Project saved: {project_name}")
        return project_id
    
    def get_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Get project by ID"""
        try:
            results = self.collections[self.PROJECTS].get(ids=[project_id])
            
            if results and results['documents']:
                return {
                    "content": results['documents'][0],
                    "metadata": results['metadatas'][0]
                }
            return None
        except Exception as e:
            logger.error(f"Failed to get project {project_id}: {e}")
            return None
    
    def list_projects(
        self,
        status: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """List all projects, optionally filtered by status"""
        where_filter = {"status": status} if status else None
        
        try:
            results = self.collections[self.PROJECTS].get(
                where=where_filter,
                limit=limit
            )
            
            projects = []
            if results and results['documents']:
                for doc, meta in zip(results['documents'], results['metadatas']):
                    projects.append({
                        "content": doc,
                        "metadata": meta
                    })
            
            return projects
        except Exception as e:
            logger.error(f"Failed to list projects: {e}")
            return []
    
    def search_projects(self, query: str, n_results: int = 10) -> List[Dict]:
        """Semantic search for projects"""
        try:
            results = self.collections[self.PROJECTS].query(
                query_texts=[query],
                n_results=n_results
            )
            
            matches = []
            if results and results['documents']:
                for docs, metas in zip(results['documents'][0], results['metadatas'][0]):
                    matches.append({
                        "content": docs,
                        "metadata": metas
                    })
            
            return matches
        except Exception as e:
            logger.error(f"Project search failed: {e}")
            return []
    
    # ==================== EMPLOYEE METHODS ====================
    
    def save_employee(
        self,
        employee_id: str,
        name: str,
        role: str,
        skills: List[str],
        projects: Optional[List[str]] = None,
        bio: Optional[str] = None
    ) -> str:
        """Save or update employee record"""
        skills_text = ', '.join(skills)
        document = f"{name} - {role}: {skills_text}"
        if bio:
            document += f"\n{bio}"
        
        metadata = {
            "employee_id": employee_id,
            "name": name,
            "role": role,
            "skills": json.dumps(skills),
            "projects": json.dumps(projects or []),
            "skill_count": len(skills),
            "created_at": datetime.utcnow().isoformat()
        }
        
        with self._safe_operation("save_employee"):
            try:
                self.collections[self.EMPLOYEES].delete(ids=[employee_id])
            except:
                pass
            
            self.collections[self.EMPLOYEES].add(
                documents=[document],
                metadatas=[metadata],
                ids=[employee_id]
            )
        
        logger.info(f"👤 Employee saved: {name}")
        return employee_id
    
    def get_employee(self, employee_id: str) -> Optional[Dict]:
        """Get employee by ID"""
        try:
            results = self.collections[self.EMPLOYEES].get(ids=[employee_id])
            
            if results and results['documents']:
                return {
                    "content": results['documents'][0],
                    "metadata": results['metadatas'][0]
                }
            return None
        except Exception as e:
            logger.error(f"Failed to get employee: {e}")
            return None
    
    def search_employees(
        self,
        query: str,
        role: Optional[str] = None,
        n_results: int = 10
    ) -> List[Dict]:
        """Search employees by skills, role, or name"""
        where_filter = {"role": role} if role else None
        
        try:
            results = self.collections[self.EMPLOYEES].query(
                query_texts=[query],
                n_results=n_results,
                where=where_filter
            )
            
            matches = []
            if results and results['documents']:
                for docs, metas in zip(results['documents'][0], results['metadatas'][0]):
                    matches.append({
                        "content": docs,
                        "metadata": metas
                    })
            
            return matches
        except Exception as e:
            logger.error(f"Employee search failed: {e}")
            return []
    
    # ==================== KNOWLEDGE BASE METHODS ====================
    
    def save_knowledge(
        self,
        knowledge_id: str,
        title: str,
        content: str,
        category: str,
        tags: Optional[List[str]] = None,
        source: Optional[str] = None
    ) -> str:
        """Save knowledge base entry"""
        document = f"{title}\n\n{content}"
        
        metadata = {
            "knowledge_id": knowledge_id,
            "title": title,
            "category": category,
            "tags": json.dumps(tags or []),
            "source": source or "internal",
            "content_length": len(content),
            "created_at": datetime.utcnow().isoformat()
        }
        
        with self._safe_operation("save_knowledge"):
            try:
                self.collections[self.KNOWLEDGE].delete(ids=[knowledge_id])
            except:
                pass
            
            self.collections[self.KNOWLEDGE].add(
                documents=[document],
                metadatas=[metadata],
                ids=[knowledge_id]
            )
        
        logger.info(f"📚 Knowledge saved: {title}")
        return knowledge_id
    
    def search_knowledge(
        self,
        query: str,
        category: Optional[str] = None,
        n_results: int = 5
    ) -> List[Dict]:
        """Search knowledge base with semantic search"""
        where_filter = {"category": category} if category else None
        
        try:
            results = self.collections[self.KNOWLEDGE].query(
                query_texts=[query],
                n_results=n_results,
                where=where_filter
            )
            
            matches = []
            if results and results['documents']:
                for docs, metas, distances in zip(
                    results['documents'][0],
                    results['metadatas'][0],
                    results['distances'][0]
                ):
                    matches.append({
                        "content": docs,
                        "metadata": metas,
                        "relevance_score": 1 - distances
                    })
            
            return matches
        except Exception as e:
            logger.error(f"Knowledge search failed: {e}")
            return []
    
    def list_categories(self) -> List[str]:
        """Get all unique knowledge categories"""
        try:
            results = self.collections[self.KNOWLEDGE].get()
            if results and results['metadatas']:
                categories = set(meta.get('category') for meta in results['metadatas'])
                return sorted(list(categories))
            return []
        except Exception as e:
            logger.error(f"Failed to list categories: {e}")
            return []
    
    # ==================== AGENT OUTPUT METHODS ====================
    
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
        """Save agent output (code, reports, analyses, etc.)"""
        document = f"Task: {task}\n\nOutput:\n{output}"
        
        meta = {
            "output_id": output_id,
            "agent_name": agent_name,
            "output_type": output_type,
            "success": success,
            "output_length": len(output),
            "created_at": datetime.utcnow().isoformat(),
            **(metadata or {})
        }
        
        with self._safe_operation("save_agent_output"):
            try:
                self.collections[self.AGENT_OUTPUTS].delete(ids=[output_id])
            except:
                pass
            
            self.collections[self.AGENT_OUTPUTS].add(
                documents=[document],
                metadatas=[meta],
                ids=[output_id]
            )
        
        logger.info(f"🤖 Agent output saved: {agent_name} - {output_type}")
        return output_id
    
    def get_agent_outputs(
        self,
        agent_name: str,
        output_type: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict]:
        """Get recent outputs from specific agent"""
        where_filter = {"agent_name": agent_name}
        if output_type:
            where_filter["output_type"] = output_type
        
        try:
            results = self.collections[self.AGENT_OUTPUTS].get(
                where=where_filter,
                limit=limit
            )
            
            outputs = []
            if results and results['documents']:
                for doc, meta in zip(results['documents'], results['metadatas']):
                    outputs.append({
                        "content": doc,
                        "metadata": meta
                    })
            
            # Sort by timestamp (most recent first)
            outputs.sort(
                key=lambda x: x['metadata'].get('created_at', ''),
                reverse=True
            )
            
            return outputs
        except Exception as e:
            logger.error(f"Failed to get agent outputs: {e}")
            return []
    
    def search_agent_outputs(
        self,
        query: str,
        agent_name: Optional[str] = None,
        n_results: int = 5
    ) -> List[Dict]:
        """Search agent outputs semantically"""
        where_filter = {"agent_name": agent_name} if agent_name else None
        
        try:
            results = self.collections[self.AGENT_OUTPUTS].query(
                query_texts=[query],
                n_results=n_results,
                where=where_filter
            )
            
            matches = []
            if results and results['documents']:
                for docs, metas in zip(results['documents'][0], results['metadatas'][0]):
                    matches.append({
                        "content": docs,
                        "metadata": metas
                    })
            
            return matches
        except Exception as e:
            logger.error(f"Output search failed: {e}")
            return []
    
    # ==================== UTILITY METHODS ====================
    
    def get_stats(self) -> Dict[str, int]:
        """Get statistics about stored data"""
        stats = {}
        for name, collection in self.collections.items():
            try:
                count = collection.count()
                stats[name] = count
            except Exception as e:
                logger.error(f"Failed to get stats for {name}: {e}")
                stats[name] = 0
        
        stats['total'] = sum(stats.values())
        return stats
    
    def health_check(self) -> Dict[str, Any]:
        """Check health of memory manager"""
        health = {
            "status": "healthy",
            "persist_directory": self.persist_directory,
            "collections": {},
            "total_documents": 0
        }
        
        for name, collection in self.collections.items():
            try:
                count = collection.count()
                health["collections"][name] = {
                    "status": "ok",
                    "document_count": count
                }
                health["total_documents"] += count
            except Exception as e:
                health["collections"][name] = {
                    "status": "error",
                    "error": str(e)
                }
                health["status"] = "degraded"
        
        return health
    
    def export_collection(
        self,
        collection_name: str,
        output_file: str
    ) -> bool:
        """Export collection to JSON file"""
        if collection_name not in self.collections:
            logger.error(f"Collection '{collection_name}' not found")
            return False
        
        try:
            results = self.collections[collection_name].get()
            
            export_data = {
                "collection": collection_name,
                "exported_at": datetime.utcnow().isoformat(),
                "count": len(results['ids']) if results else 0,
                "data": []
            }
            
            if results and results['ids']:
                for i, doc_id in enumerate(results['ids']):
                    export_data['data'].append({
                        "id": doc_id,
                        "document": results['documents'][i],
                        "metadata": results['metadatas'][i]
                    })
            
            with open(output_file, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            logger.info(f"📤 Exported {collection_name} to {output_file}")
            return True
        except Exception as e:
            logger.error(f"Export failed: {e}")
            return False
    
    def reset(self, confirm: bool = False):
        """
        Reset all collections (WARNING: deletes all data)
        
        Args:
            confirm: Must be True to actually reset
        """
        if not confirm:
            logger.warning("⚠️ Reset called without confirmation. No action taken.")
            return
        
        logger.warning("🗑️ Resetting all collections...")
        
        for collection_name in list(self.collections.keys()):
            try:
                self.client.delete_collection(collection_name)
                logger.info(f"✓ Deleted collection: {collection_name}")
            except Exception as e:
                logger.error(f"Failed to delete {collection_name}: {e}")
        
        # Reinitialize collections
        self.collections = self._initialize_collections()
        logger.info("✅ All collections reset and reinitialized")
    
    def __repr__(self) -> str:
        stats = self.get_stats()
        return f"<LocalMemoryManager: {stats['total']} documents across {len(self.collections)} collections>"


# ==================== SINGLETON PATTERN ====================

_memory_manager: Optional[LocalMemoryManager] = None


def get_memory_manager(
    persist_directory: Optional[str] = None,
    reset: bool = False
) -> LocalMemoryManager:
    """
    Get or create shared memory manager instance (singleton)
    
    Args:
        persist_directory: Custom persist directory (optional)
        reset: Force recreate the instance
    
    Returns:
        LocalMemoryManager instance
    """
    global _memory_manager
    
    if reset or _memory_manager is None:
        persist_dir = persist_directory or os.getenv(
            "MEMORY_PERSIST_DIRECTORY",
            "./data/memory"
        )
        _memory_manager = LocalMemoryManager(persist_dir)
        logger.info(f"🧠 Memory Manager initialized: {_memory_manager}")
    
    return _memory_manager


def reset_memory_manager():
    """Reset the global memory manager instance"""
    global _memory_manager
    _memory_manager = None
    logger.info("🔄 Memory Manager reset")


# ==================== EXAMPLE USAGE ====================

if __name__ == "__main__":
    # Initialize memory manager
    memory = get_memory_manager()
    
    # Show health
    print("\n" + "="*60)
    print("MEMORY MANAGER HEALTH CHECK")
    print("="*60)
    health = memory.health_check()
    print(json.dumps(health, indent=2))
    
    # Example: Save conversation
    print("\n📝 Saving test conversation...")
    memory.save_conversation(
        session_id="test_session_001",
        agent_name="TestAgent",
        user_message="What is machine learning?",
        agent_response="Machine learning is a subset of AI..."
    )
    
    # Example: Save knowledge
    print("📚 Saving test knowledge...")
    memory.save_knowledge(
        knowledge_id="kb_001",
        title="Machine Learning Basics",
        content="ML is about learning patterns from data...",
        category="AI/ML",
        tags=["machine-learning", "basics"]
    )
    
    # Search knowledge
    print("\n🔍 Searching knowledge base...")
    results = memory.search_knowledge("machine learning")
    print(f"Found {len(results)} results")
    
    # Show stats
    print("\n" + "="*60)
    print("STATISTICS")
    print("="*60)
    stats = memory.get_stats()
    for collection, count in stats.items():
        print(f"  {collection}: {count}")
    
    print("\n✅ Test complete!")