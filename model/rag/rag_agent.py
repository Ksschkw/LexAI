from swarmauri.standard.agents.concrete.RagAgent import RagAgent
from swarmauri.standard.conversations.concrete.MaxSystemContextConversation import MaxSystemContextConversation
from swarmauri.standard.messages.concrete.SystemMessage import SystemMessage
from swarmauri.standard.messages.concrete.HumanMessage import HumanMessage
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Monkey-patch to add missing attribute
MaxSystemContextConversation.__class_name__ = "MaxSystemContextConversation"

class LEXAIRagAgent:
    """Custom RAG agent for LEXAI with reasoning in responses."""
    
    def __init__(self, llm, vector_store):
        """Initializes the RAG agent with system context and components."""
        self.system_context = """You are LEXAI, an AI legal assistant for Nigerian law.
                                 Answer queries based on the Nigerian Constitution.
                                 Be casual, clear, and always explain your reasoning.
                                 If unsure, say 'I need more data.'"""
        
        # Create the conversation properly
        self.conversation = MaxSystemContextConversation(
            system_context=SystemMessage(content=self.system_context),
            max_size=100
        )
        
        # Monkey-patch set_system_context to prevent errors
        def patched_set_system_context(system_context):
            logger.warning("Ignoring set_system_context call - system context already set")
        self.conversation.set_system_context = patched_set_system_context
        
        self.agent = RagAgent(
            llm=llm,
            conversation=self.conversation,
            vector_store=vector_store,
            system_context=self.system_context
        )
    
    def execute(self, query, context=None):
        """Executes a query using the provided context and adds reasoning to the response."""
        # Add context to the conversation if provided
        if context and context.strip():
            self.conversation.add_message(SystemMessage(content=f"Context: {context}"))
        
        # Add the user's query
        self.conversation.add_message(HumanMessage(content=query))
        
        # Use RagAgent's exec method
        try:
            response = self.agent.exec()
        except Exception as e:
            return f"Error processing query: {str(e)}\n\n**Reasoning**: Could not process due to an internal error."
        
        reasoning = "No relevant context was provided." if not context or not context.strip() else f"I used the context: '{context[:50]}...'."
        return f"{response}\n\n**Reasoning**: {reasoning}"