'''Purpose: Tracks all translation requests and provides analytics
What it does:

Stores translation history in SQLite database
Provides statistics (total translations, popular languages)
Retrieves historical logs
Manages database operations'''

import sqlite3
import logging
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class LoggingService:
    """Service for logging translation requests"""
    
    def __init__(self, db_path: str = "translation_logs.db", use_db: bool = True):
        self.db_path = db_path
        self.use_db = use_db
        
        self.memory_logs = []
        
        if use_db:
            self._initialize_database()
        
        logger.info(f"LoggingService initialized (Database: {use_db})")
    
    def _initialize_database(self):
        """Initialize SQLite database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            #Create translations table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS translations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    original_text TEXT NOT NULL,
                    translated_text TEXT NOT NULL,
                    source_lang VARCHAR(10),
                    target_lang VARCHAR(10) NOT NULL,
                    char_count INTEGER,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    ip_address VARCHAR(50),
                    user_agent TEXT
                )
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_timestamp 
                ON translations(timestamp DESC)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_target_lang 
                ON translations(target_lang)
            ''')
            
            conn.commit()
            conn.close()
            
            logger.info(f"Database initialized at {self.db_path}")
        except Exception as e:
            logger.error(f"Failed to initialize database: {str(e)}")
            logger.warning("Falling back to in-memory logging")
            self.use_db = False
    
    def log_translation(
        self,
        original_text: str,
        translated_text: str,
        source_lang: str,
        target_lang: str,
        char_count: int,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Dict:
        timestamp = datetime.utcnow()
        
        log_entry = {
            'original_text': original_text[:100],  # Truncate for storage
            'translated_text': translated_text[:100],
            'source_lang': source_lang,
            'target_lang': target_lang,
            'char_count': char_count,
            'timestamp': timestamp,
            'ip_address': ip_address,
            'user_agent': user_agent
        }
        
        if self.use_db:
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO translations 
                    (original_text, translated_text, source_lang, target_lang, 
                     char_count, timestamp, ip_address, user_agent)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    log_entry['original_text'],
                    log_entry['translated_text'],
                    log_entry['source_lang'],
                    log_entry['target_lang'],
                    log_entry['char_count'],
                    log_entry['timestamp'],
                    log_entry['ip_address'],
                    log_entry['user_agent']
                ))
                
                log_entry['id'] = cursor.lastrowid
                conn.commit()
                conn.close()
            except Exception as e:
                logger.error(f"Failed to log to database: {str(e)}")
                self.memory_logs.append(log_entry)
        else:
            log_entry['id'] = len(self.memory_logs) + 1
            self.memory_logs.append(log_entry)
        
        return log_entry
    
    def get_logs(self, limit: int = 50, offset: int = 0) -> List[Dict]:
        if self.use_db:
            try:
                conn = sqlite3.connect(self.db_path)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT id, original_text, translated_text, source_lang, 
                           target_lang, char_count, timestamp, ip_address
                    FROM translations
                    ORDER BY timestamp DESC
                    LIMIT ? OFFSET ?
                ''', (limit, offset))
                
                rows = cursor.fetchall()
                conn.close()
                
                return [dict(row) for row in rows]
            except Exception as e:
                logger.error(f"Failed to retrieve logs from database: {str(e)}")
                return self.memory_logs[-limit:] if self.memory_logs else []
        else:
            start = max(0, len(self.memory_logs) - offset - limit)
            end = len(self.memory_logs) - offset if offset > 0 else len(self.memory_logs)
            return self.memory_logs[start:end][::-1]
    
    def get_statistics(self) -> Dict:
        if self.use_db:
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute('SELECT COUNT(*) FROM translations')
                total = cursor.fetchone()[0]
                
                cursor.execute('SELECT SUM(char_count) FROM translations')
                total_chars = cursor.fetchone()[0] or 0
                
                cursor.execute('''
                    SELECT target_lang, COUNT(*) as count
                    FROM translations
                    GROUP BY target_lang
                    ORDER BY count DESC
                    LIMIT 5
                ''')
                popular_languages = [
                    {'language': row[0], 'count': row[1]}
                    for row in cursor.fetchall()
                ]
                
                cursor.execute('''
                    SELECT COUNT(*) FROM translations
                    WHERE datetime(timestamp) > datetime('now', '-1 day')
                ''')
                recent_count = cursor.fetchone()[0]
                
                conn.close()
                
                return {
                    'total_translations': total,
                    'total_characters': total_chars,
                    'popular_languages': popular_languages,
                    'translations_last_24h': recent_count
                }
            except Exception as e:
                logger.error(f"Failed to get statistics from database: {str(e)}")
        
        total = len(self.memory_logs)
        total_chars = sum(log['char_count'] for log in self.memory_logs)

        lang_counts = {}
        for log in self.memory_logs:
            lang = log['target_lang']
            lang_counts[lang] = lang_counts.get(lang, 0) + 1
        
        popular_languages = [
            {'language': lang, 'count': count}
            for lang, count in sorted(lang_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        ]
        
        return {
            'total_translations': total,
            'total_characters': total_chars,
            'popular_languages': popular_languages,
            'translations_last_24h': total  # Approximation for in-memory
        }
    
    def clear_logs(self):
        if self.use_db:
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute('DELETE FROM translations')
                conn.commit()
                conn.close()
                logger.info("Database logs cleared")
            except Exception as e:
                logger.error(f"Failed to clear database logs: {str(e)}")
        else:
            self.memory_logs.clear()
            logger.info("In-memory logs cleared")