
import sqlite3
from datetime import datetime

DB_NAME = "members.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS members (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        first_name TEXT,
        last_active TEXT,
        message_count INTEGER DEFAULT 0
    )
    """)

    conn.commit()
    conn.close()

def save_activity(user):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    now = datetime.utcnow().isoformat()
    username = user.username or ""
    first_name = user.first_name or ""

    cur.execute("""
    INSERT INTO members (user_id, username, first_name, last_active, message_count)
    VALUES (?, ?, ?, ?, 1)
    ON CONFLICT(user_id) DO UPDATE SET
        username=excluded.username,
        first_name=excluded.first_name,
        last_active=excluded.last_active,
        message_count=members.message_count + 1
    """, (user.id, username, first_name, now))

    conn.commit()
    conn.close()

def get_stats():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM members")
    total = cur.fetchone()[0]

    cur.execute("""
    SELECT COUNT(*) FROM members
    WHERE date(last_active) = date('now')
    """)
    active_today = cur.fetchone()[0]

    cur.execute("""
    SELECT COUNT(*) FROM members
    WHERE datetime(last_active) >= datetime('now', '-7 days')
    """)
    active_7_days = cur.fetchone()[0]

    cur.execute("""
    SELECT COUNT(*) FROM members
    WHERE datetime(last_active) < datetime('now', '-30 days')
    """)
    inactive_30_days = cur.fetchone()[0]

    conn.close()

    return total, active_today, active_7_days, inactive_30_days
