# Purpose: Manages queries and sessions, coordinating model components.
# Why: Explicitly separates control logic for modularity.

from model.rag.rag_agent import LEXAIRagAgent
from model.database.chat_history import ChatHistoryDB
from model.vector_store.tfidf_store import VectorStoreManager
from model.llm.groq_llm import GroqLLM
from utils.logger import logger

class QueryHandler:
    """Handles user queries and manages session state."""
    
    def __init__(self):
        """Initializes the handler with all necessary components."""
        # Initialize vector store (loads from constitution_chunks.json)
        self.vector_store_manager = VectorStoreManager()
        
        # Initialize LLM and session storage
        self.llm = GroqLLM()
        self.chat_db = ChatHistoryDB()
        self.sessions = {}  # Dictionary to store session agents
    
    def handle_query(self, session_id, query):
        """Processes a query for a given session.
        
        Args:
            session_id (str): Unique session identifier.
            query (str): User's legal question.
        Returns:
            str: Agent's response with reasoning.
        """
        # Create new session if it doesn't exist
        if session_id not in self.sessions:
            self.sessions[session_id] = LEXAIRagAgent(
                llm=self.llm.get_llm(),
                vector_store=self.vector_store_manager.get_vector_store()
            )
            logger.info(f"Created new session: {session_id}")
        
        agent = self.sessions[session_id]
        
        # Use hybrid retrieval
        results = self.vector_store_manager.hybrid_retrieve(query, top_k=5)
        context = "\n".join([doc.content for doc in results])
        
        # Pass context to agent
        response = agent.execute(query, context)
        self.chat_db.save_chat(session_id, query, response)
        return response