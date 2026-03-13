import sqlite3

conn = sqlite3.connect("classgenius.db", check_same_thread=False)
c = conn.cursor()

# Notes table
c.execute("""
CREATE TABLE IF NOT EXISTS notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT
)
""")

# Notification history table
c.execute("""
CREATE TABLE IF NOT EXISTS notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_name TEXT,
    note_name TEXT,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

conn.commit()
