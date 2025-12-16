import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'self_analysis.db')

connection = sqlite3.connect(DB_PATH)
cursor = connection.cursor()

# --- 1. エピソードテーブル ---
cursor.execute(
    '''
    CREATE TABLE IF NOT EXISTS episodes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        feeling TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    '''
)

# --- 2. 分析テーブル (深堀り質問を追加) ---
cursor.execute(
    '''
    CREATE TABLE IF NOT EXISTS analyses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        episode_id INTEGER NOT NULL,
        star_summary TEXT,
        core_values TEXT,
        advice TEXT,
        next_question TEXT,  -- ★追加: AIからの深堀り質問
        FOREIGN KEY (episode_id) REFERENCES episodes (id)
    );
    '''
)

connection.commit()
connection.close()
print(f"Database initialized (Deep Dive version) at: {DB_PATH}")