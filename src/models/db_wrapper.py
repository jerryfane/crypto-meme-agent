import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Dict, List, Optional
import os
from dotenv import load_dotenv

class DBWrapper:
    def __init__(self):
        load_dotenv()
        self.conn_string = os.getenv('DATABASE_URL')
        self.conn = None
        self.connect()

    def connect(self):
        """Establish database connection"""
        self.conn = psycopg2.connect(self.conn_string)
        self.conn.autocommit = True

    def store_tweet(self, text: str, context: str) -> int:
        """Store a new tweet with context"""
        with self.conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO tweets (
                    text,
                    status,
                    text_adjusted,
                    version,
                    score,
                    created_at,
                    updated_at,
                    sent_at,
                    context
                )
                VALUES (
                    %s,                -- text
                    'review',          -- status
                    NULL,              -- text_adjusted
                    0,                 -- version
                    NULL,              -- score
                    CURRENT_TIMESTAMP, -- created_at
                    NULL,              -- updated_at
                    NULL,              -- sent_at
                    %s                 -- context
                )
                RETURNING id
                """,
                (text, context)
            )
            return cur.fetchone()[0]

    def get_tweets_for_review(self) -> List[Dict]:
        """Get all tweets pending review"""
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT * FROM tweets 
                WHERE status = 'review'
                ORDER BY created_at DESC
                """
            )
            return cur.fetchall()

    def update_tweet_status(self, tweet_id: int, status: str, 
                          text_adjusted: Optional[str] = None,
                          score: Optional[int] = None) -> bool:
        """Update tweet status and optional fields"""
        with self.conn.cursor() as cur:
            cur.execute(
                """
                UPDATE tweets 
                SET status = %s,
                    text_adjusted = COALESCE(%s, text_adjusted),
                    score = COALESCE(%s, score)
                WHERE id = %s
                """,
                (status, text_adjusted, score, tweet_id)
            )
            return cur.rowcount > 0

    def get_next_tweet_to_send(self) -> Optional[Dict]:
        """Get the next approved tweet to send"""
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT * FROM tweets 
                WHERE status = 'approved' 
                AND sent_at IS NULL
                ORDER BY score DESC, created_at ASC
                LIMIT 1
                """
            )
            return cur.fetchone()

    def mark_tweet_as_sent(self, tweet_id: int) -> bool:
        """Mark a tweet as sent"""
        with self.conn.cursor() as cur:
            cur.execute(
                """
                UPDATE tweets 
                SET status = 'sent',
                    sent_at = CURRENT_TIMESTAMP
                WHERE id = %s
                """,
                (tweet_id,)
            )
            return cur.rowcount > 0
    
    def get_best_tweets(self, min_score: int = 4) -> List[Dict]:
        """Get approved tweets with high scores grouped by context"""
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT 
                    context,
                    COALESCE(text_adjusted, text) as text,
                    score
                FROM tweets 
                WHERE status = 'approved' 
                AND score >= %s
                ORDER BY context, score DESC
                """,
                (min_score,)
            )
            return cur.fetchall()
    
    def get_tweets_stats(self) -> Dict:
        """Get tweet counts by status"""
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT status, COUNT(*) as count
                FROM tweets
                GROUP BY status
                """
            )
            return cur.fetchall()
    
    def get_tweets_filtered(self, status: Optional[str] = 'review', context: Optional[str] = None) -> List[Dict]:
        """Get tweets with optional status and context filters"""
        query = """
            SELECT * FROM tweets 
            WHERE 1=1
        """
        params = []
        
        if status:
            query += " AND status = %s"
            params.append(status)
            
        if context:
            query += " AND context = %s"
            params.append(context)
            
        query += " ORDER BY created_at DESC"
        
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, params)
            return cur.fetchall()
            
    def get_contexts(self) -> List[str]:
        """Get all unique contexts"""
        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT DISTINCT context 
                FROM tweets 
                ORDER BY context
                """
            )
            return [row[0] for row in cur.fetchall()]