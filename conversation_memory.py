import sqlite3
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional

class ConversationMemory:
    def __init__(self, db_path: str = "conversation_memory.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the SQLite database for conversation memory"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                channel_id TEXT NOT NULL,
                message TEXT NOT NULL,
                response TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                search_query TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_conversation(self, user_id: str, channel_id: str, message: str, 
                        response: str = None, search_query: str = None):
        """Add a conversation entry to memory"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO conversations (user_id, channel_id, message, response, search_query)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, channel_id, message, response, search_query))
        
        conn.commit()
        conn.close()
    
    def get_recent_context(self, user_id: str, channel_id: str, 
                          hours: int = 24, limit: int = 10) -> List[Dict]:
        """Get recent conversation context for a user in a channel"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get conversations from the last N hours
        since_time = datetime.now() - timedelta(hours=hours)
        
        cursor.execute('''
            SELECT message, response, search_query, timestamp
            FROM conversations
            WHERE user_id = ? AND channel_id = ? AND timestamp > ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (user_id, channel_id, since_time.isoformat(), limit))
        
        results = cursor.fetchall()
        conn.close()
        
        # Convert to list of dictionaries, reverse to get chronological order
        context = []
        for row in reversed(results):
            context.append({
                'message': row[0],
                'response': row[1],
                'search_query': row[2],
                'timestamp': row[3]
            })
        
        return context
    
    def get_channel_context(self, channel_id: str, hours: int = 2, 
                           limit: int = 20) -> List[Dict]:
        """Get recent channel conversation context"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        since_time = datetime.now() - timedelta(hours=hours)
        
        cursor.execute('''
            SELECT user_id, message, response, search_query, timestamp
            FROM conversations
            WHERE channel_id = ? AND timestamp > ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (channel_id, since_time.isoformat(), limit))
        
        results = cursor.fetchall()
        conn.close()
        
        context = []
        for row in reversed(results):
            context.append({
                'user_id': row[0],
                'message': row[1],
                'response': row[2],
                'search_query': row[3],
                'timestamp': row[4]
            })
        
        return context
    
    def get_logs_by_date_range(self, channel_id: str, start_date: datetime, 
                              end_date: datetime) -> List[Dict]:
        """Get conversation logs for a specific date range"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT user_id, message, response, search_query, timestamp
            FROM conversations
            WHERE channel_id = ? AND timestamp BETWEEN ? AND ?
            ORDER BY timestamp ASC
        ''', (channel_id, start_date.isoformat(), end_date.isoformat()))
        
        results = cursor.fetchall()
        conn.close()
        
        logs = []
        for row in results:
            logs.append({
                'user_id': row[0],
                'message': row[1],
                'response': row[2],
                'search_query': row[3],
                'timestamp': row[4]
            })
        
        return logs
    
    def cleanup_old_conversations(self, days_to_keep: int = 30):
        """Clean up old conversation data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        cursor.execute('''
            DELETE FROM conversations
            WHERE timestamp < ?
        ''', (cutoff_date.isoformat(),))
        
        conn.commit()
        conn.close()