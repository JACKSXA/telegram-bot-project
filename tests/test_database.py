import os
import sqlite3
import pytest

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'user_data.db')

def test_conversations_table_exists():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='conversations'")
    assert cur.fetchone() is not None
    conn.close()


def test_insert_and_read_conversation():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("INSERT INTO conversations (user_id, role, content) VALUES (?, ?, ?)", (999999999, 'user', 'pytest message'))
    conn.commit()
    rows = cur.execute("SELECT role, content FROM conversations WHERE user_id=? ORDER BY timestamp DESC LIMIT 1", (999999999,)).fetchall()
    conn.close()
    assert rows and rows[0][0] == 'user' and rows[0][1] == 'pytest message'
