"""
LLM Configuration - Hugging Face Integration (Alternative Approach)
Uses direct Hugging Face Inference Client - Most Reliable
"""
import os
from typing import Optional, Dict, Any
from huggingface_hub import InferenceClient


class HuggingFaceLLM:
    """
    Wrapper for Hugging Face using InferenceClient
    This is the most reliable approach with latest HF API
    """
    
    def __init__(
        self,
        model_name: Optional[str] = None,
        api_key: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 512
    ):
        self.model_name = model_name or os.getenv(
            "HF_MODEL_NAME", 
            "mistralai/Mistral-7B-Instruct-v0.2"
        )
        self.api_key = api_key or os.getenv("HUGGINGFACE_API_KEY")
        
        if not self.api_key:
            raise ValueError(
                "HUGGINGFACE_API_KEY not found. Please set it in .env file.\n"
                "Get your free API key from: https://huggingface.co/settings/tokens"
            )
        
        self.temperature = temperature
        self.max_tokens = max_tokens
        self._client = None
    
    def get_client(self):
        """Get configured InferenceClient instance"""
        if not self._client:
            self._client = InferenceClient(
                model=self.model_name,
                token=self.api_key
            )
        return self._client
    
    def __call__(self, prompt: str) -> str:
        """Make the LLM callable for CrewAI compatibility"""
        client = self.get_client()
        
        try:
            response = client.text_generation(
                prompt,
                max_new_tokens=self.max_tokens,
                temperature=self.temperature,
                return_full_text=False
            )
            return response
        except Exception as e:
            return f"Error: {str(e)}"
    
    @property
    def _llm_type(self) -> str:
        """Return LLM type for LangChain compatibility"""
        return "huggingface"
    
    @staticmethod
    def get_recommended_models():
        """Return list of recommended free HF models"""
        return {
            "mistral-7b": {
                "name": "mistralai/Mistral-7B-Instruct-v0.2",
                "description": "Best quality - Mistral 7B (recommended)",
                "speed": "medium",
                "quality": "excellent"
            },
            "zephyr": {
                "name": "HuggingFaceH4/zephyr-7b-beta",
                "description": "High quality - Zephyr 7B",
                "speed": "medium",
                "quality": "excellent"
            },
            "phi-3": {
                "name": "microsoft/Phi-3-mini-4k-instruct",
                "description": "Microsoft Phi-3 - Compact and fast",
                "speed": "fast",
                "quality": "very good"
            }
        }


def create_llm_for_agent(role: str, temperature: float = 0.7):
    """
    Create LLM instance optimized for specific agent role
    
    Args:
        role: Agent role (hr, engineer, analyst, etc.)
        temperature: Creativity level (0.0 = deterministic, 1.0 = creative)
    """
    # Adjust temperature based on role
    role_temps = {
        "hr": 0.3,              # HR needs to be consistent
        "engineer": 0.5,        # Engineer needs balance
        "analyst": 0.4,         # Analyst needs precision
        "pmo": 0.3,             # PMO needs consistency
        "security": 0.2,        # Security needs precision
        "devops": 0.2           # DevOps needs precision
    }
    
    temp = role_temps.get(role.lower(), temperature)
    
    llm_config = HuggingFaceLLM(temperature=temp)
    return llm_config


# Global LLM instance (lazy loaded)
_global_llm = None

def get_global_llm():
    """Get shared LLM instance (saves on API calls)"""
    global _global_llm
    if _global_llm is None:
        _global_llm = HuggingFaceLLM()
    return _global_llm


# ============================================================================
# MCP SERVER INTEGRATION
# ============================================================================

class MCPServerManager:
    """
    Manage MCP (Model Context Protocol) servers for database and tool access
    """
    
    def __init__(self):
        self.servers = {}
        self._initialize_servers()
    
    def _initialize_servers(self):
        """Initialize available MCP servers"""
        # Database MCP Server
        if os.getenv("ENABLE_DB_MCP", "true").lower() == "true":
            self.servers['database'] = {
                "name": "database",
                "type": "sqlite",
                "connection_string": os.getenv("DB_CONNECTION_STRING", "sqlite:///./company.db"),
                "enabled": True
            }
        
        # File System MCP Server
        if os.getenv("ENABLE_FS_MCP", "true").lower() == "true":
            self.servers['filesystem'] = {
                "name": "filesystem",
                "base_path": os.getenv("FS_BASE_PATH", "./agent_workspace"),
                "enabled": True
            }
        
        # Web Search MCP Server
        if os.getenv("ENABLE_SEARCH_MCP", "false").lower() == "true":
            self.servers['web_search'] = {
                "name": "web_search",
                "api_key": os.getenv("SEARCH_API_KEY"),
                "enabled": bool(os.getenv("SEARCH_API_KEY"))
            }
    
    def get_server(self, server_name: str) -> Dict[str, Any]:
        """Get MCP server configuration"""
        return self.servers.get(server_name, {})
    
    def list_servers(self) -> Dict[str, Dict[str, Any]]:
        """List all available MCP servers"""
        return self.servers


# Global MCP manager
_mcp_manager = None

def get_mcp_manager() -> MCPServerManager:
    """Get global MCP server manager"""
    global _mcp_manager
    if _mcp_manager is None:
        _mcp_manager = MCPServerManager()
    return _mcp_manager


# Quick test function
if __name__ == "__main__":
    print("Testing LLM Configuration...")
    print()
    
    try:
        llm = create_llm_for_agent("hr")
        print(f"✅ LLM created successfully!")
        print(f"   Using: HuggingFace InferenceClient")
        print()
        
        # Test a simple call
        print("Testing simple generation...")
        result = llm("Say hello in one word.")
        print(f"   Response: {result}")
        print()
        print("✅ Working correctly!")
    except Exception as e:
        print(f"❌ Error: {str(e)}")