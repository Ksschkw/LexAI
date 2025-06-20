import logging

logger = logging.getLogger("LEXAI")

class LEXAIRagAgent:
    """Custom RAG agent implementation."""
    
    def __init__(self, llm, vector_store):
        self.llm = llm
        self.vector_store = vector_store
        self.conversation = []
        self.system_context = """You are LEXAI, an AI legal assistant for Nigerian law.
                                 Answer queries based on the Nigerian Constitution.
                                 Be casual, clear, and always explain your reasoning.
                                 If unsure, say 'I need more data.'"""
        
        # Initialize with system message
        self.add_message({"role": "system", "content": self.system_context})
    
    def add_message(self, message):
        """Adds a message to the conversation."""
        self.conversation.append(message)
        
        # Keep conversation manageable
        if len(self.conversation) > 10:
            self.conversation = self.conversation[-10:]
    
    def execute(self, query, context=None):
        """Executes a query using the provided context."""
        try:
            # Add context if provided
            if context and context.strip():
                self.add_message({
                    "role": "system", 
                    "content": f"Relevant context from Nigerian Constitution:\n{context}"
                })
            
            # Add user query
            self.add_message({"role": "user", "content": query})
            
            # Generate response
            response = self.llm.predict(self.conversation)
            
            # Add assistant response to conversation
            self.add_message({"role": "assistant", "content": response})
            
            reasoning = "No relevant context was provided." if not context or not context.strip() else f"I used the context: '{context[:50]}...'."
            return (
                f"RESPONSE:\n{response}"
                # f"REASONING:\n{reasoning}"
            )
            
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            return (
                f"ERROR:\n{str(e)}\n\n"
                f"REASONING:\nCould not process due to an internal error."
            )