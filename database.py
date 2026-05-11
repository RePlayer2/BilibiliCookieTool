
import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional

DATABASE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'db', 'meme_data.db')

class DatabaseManager:
    def __init__(self, db_path: str = DATABASE_PATH):
        self.db_path = db_path
        self._ensure_db_dir()
        self._init_tables()

    def _ensure_db_dir(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _init_tables(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS videos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    platform TEXT NOT NULL,
                    video_id TEXT NOT NULL,
                    title TEXT,
                    author TEXT,
                    url TEXT,
                    collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(platform, video_id)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS comments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    video_id INTEGER NOT NULL,
                    comment_id TEXT NOT NULL,
                    content TEXT NOT NULL,
                    author TEXT,
                    like_count INTEGER DEFAULT 0,
                    is_hot BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP,
                    collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(video_id) REFERENCES videos(id),
                    UNIQUE(video_id, comment_id)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS images (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    comment_id INTEGER,
                    video_id INTEGER,
                    image_path TEXT NOT NULL,
                    image_url TEXT,
                    is_meme BOOLEAN DEFAULT 0,
                    collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(comment_id) REFERENCES comments(id),
                    FOREIGN KEY(video_id) REFERENCES videos(id)
                )
            ''')
            
            conn.commit()

    def add_video(self, platform: str, video_id: str, title: str, author: str, url: str) -&gt; int:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('''
                    INSERT OR IGNORE INTO videos (platform, video_id, title, author, url)
                    VALUES (?, ?, ?, ?, ?)
                ''', (platform, video_id, title, author, url))
                conn.commit()
                
                cursor.execute('SELECT id FROM videos WHERE platform = ? AND video_id = ?', (platform, video_id))
                result = cursor.fetchone()
                return result[0] if result else -1
            except Exception as e:
                print(f"Error adding video: {e}")
                return -1

    def add_comment(self, video_db_id: int, comment_id: str, content: str, author: str, 
                    like_count: int, is_hot: bool, created_at: Optional[str] = None) -&gt; int:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('''
                    INSERT OR IGNORE INTO comments 
                    (video_id, comment_id, content, author, like_count, is_hot, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (video_db_id, comment_id, content, author, like_count, 1 if is_hot else 0, created_at))
                conn.commit()
                
                cursor.execute('SELECT id FROM comments WHERE video_id = ? AND comment_id = ?', (video_db_id, comment_id))
                result = cursor.fetchone()
                return result[0] if result else -1
            except Exception as e:
                print(f"Error adding comment: {e}")
                return -1

    def add_image(self, image_path: str, image_url: Optional[str] = None, 
                  comment_db_id: Optional[int] = None, video_db_id: Optional[int] = None, 
                  is_meme: bool = False) -&gt; int:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('''
                    INSERT INTO images (comment_id, video_id, image_path, image_url, is_meme)
                    VALUES (?, ?, ?, ?, ?)
                ''', (comment_db_id, video_db_id, image_path, image_url, 1 if is_meme else 0))
                conn.commit()
                return cursor.lastrowid
            except Exception as e:
                print(f"Error adding image: {e}")
                return -1

    def get_hot_comments(self, platform: Optional[str] = None, limit: int = 100) -&gt; List[Dict]:
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = '''
                SELECT c.*, v.platform, v.title as video_title, v.url as video_url
                FROM comments c
                JOIN videos v ON c.video_id = v.id
                WHERE c.is_hot = 1
            '''
            params = []
            
            if platform:
                query += ' AND v.platform = ?'
                params.append(platform)
            
            query += ' ORDER BY c.like_count DESC LIMIT ?'
            params.append(limit)
            
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def get_meme_images(self, limit: int = 100) -&gt; List[Dict]:
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT i.*, v.platform, v.title as video_title
                FROM images i
                LEFT JOIN videos v ON i.video_id = v.id
                WHERE i.is_meme = 1
                ORDER BY i.collected_at DESC
                LIMIT ?
            ''', (limit,))
            return [dict(row) for row in cursor.fetchall()]
