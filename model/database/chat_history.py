# Purpose: Stores and retrieves chat history using SQLite.
# Why: Persisting conversations adds value and is hackathon-friendly.

import sqlite3
from utils.logger import logger

class ChatHistoryDB:
    """Manages chat history storage in SQLite."""
    
    def __init__(self, db_path="lexai_chat_history.db"):
        """Initializes the SQLite database connection.
        
        Args:
            db_path (str): Path to the SQLite database file.
        """
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.create_table()
    
    def create_table(self):
        """Creates the chat history table if it doesn’t exist."""
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_history (
                session_id TEXT NOT NULL,
                query TEXT NOT NULL,
                response TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.commit()
    
    def save_chat(self, session_id, query, response):
        """Saves a query-response pair to the database.
        
        Args:
            session_id (str): Unique session identifier.
            query (str): User’s query.
            response (str): Agent’s response.
        """
        self.cursor.execute("""
            INSERT INTO chat_history (session_id, query, response)
            VALUES (?, ?, ?)
        """, (session_id, query, response))
        self.conn.commit()
        logger.info(f"Saved chat for session {session_id}")
    
    def get_history(self, session_id):
        """Retrieves chat history for a session.
        
        Args:
            session_id (str): Unique session identifier.
        Returns:
            list: List of (query, response, timestamp) tuples.
        """
        self.cursor.execute("""
            SELECT query, response, timestamp 
            FROM chat_history 
            WHERE session_id = ? 
            ORDER BY timestamp ASC
        """, (session_id,))
        return self.cursor.fetchall()