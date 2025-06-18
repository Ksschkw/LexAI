# Purpose: Implements the RAG agent with reasoning for legal queries.
# Why: Combines retrieval and generation with explicit reasoning to stand out.

from swarmauri.standard.agents.concrete.RagAgent import RagAgent
from swarmauri.standard.conversations.concrete.MaxSystemContextConversation import MaxSystemContextConversation
from swarmauri.standard.messages.concrete.SystemMessage import SystemMessage

class LEXAIRagAgent:
    """Custom RAG agent for LEXAI with reasoning in responses."""
    
    def __init__(self, llm, vector_store):
        """Initializes the RAG agent with system context and components.
        
        Args:
            llm (GroqLLM): The LLM instance.
            vector_store (TfidfVectorStore): The vector store instance.
        """
        self.system_context = """You are LEXAI, an AI legal assistant for Nigerian law.
                                 Answer queries based on the Nigerian Constitution.
                                 Be casual, clear, and always explain your reasoning.
                                 If unsure, say 'I need more data.'"""
        self.conversation = MaxSystemContextConversation(
            system_context=SystemMessage(content=self.system_context),
            max_size=100  # Limits conversation size for memory efficiency
        )
        self.agent = RagAgent(
            llm=llm,
            conversation=self.conversation,
            system_context=self.system_context,
            vector_store=vector_store
        )
    
    def exec(self, query):
        """Executes a query and adds reasoning to the response.
        
        Args:
            query (str): The user’s legal question.
        Returns:
            str: Response with reasoning.
        """
        # Get retrieved documents for context
        retrieved_docs = self.agent.vector_store.retrieve(query, top_k=1)
        if not retrieved_docs:
            response = "I need more data to answer this accurately."
            reasoning = "No relevant sections found in the Constitution."
        else:
            context = retrieved_docs[0].content
            chunk_id = retrieved_docs[0].metadata["chunk_id"]
            prompt = f"{self.system_context}\nContext: {context}\nQuery: {query}"
            response = self.agent.llm.predict(prompt)
            reasoning = f"I found this in chunk {chunk_id} of the Constitution: '{context[:50]}...'."
        
        return f"{response}\n\n**Reasoning**: {reasoning}"