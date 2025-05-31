import sqlite3
import datetime

DB_PATH = 'dgmd.db'

def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    return conn

def find_event_participant_by_query(conn, query_param):
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, user_id, event_id FROM event_participants WHERE query_parameters = ?",
        (query_param,)
    )
    return cursor.fetchone()

def get_last_entry_type(conn, user_id, event_id):
    cursor = conn.cursor()
    cursor.execute(
        "SELECT entry_type FROM entry_logs WHERE user_id=? AND event_id=? ORDER BY scanned_at DESC LIMIT 1",
        (user_id, event_id)
    )
    row = cursor.fetchone()
    return row[0] if row else None

def get_first_checked_in(conn, user_id, event_id):
    cursor = conn.cursor()
    cursor.execute(
        "SELECT checked_in FROM entry_logs WHERE user_id=? AND event_id=? AND entry_type='in' ORDER BY checked_in LIMIT 1",
        (user_id, event_id)
    )
    row = cursor.fetchone()
    return row[0] if row else None

def insert_entry_log(conn, user_id, event_id, entry_type, scanned_at, checked_in=None):
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO entry_logs (user_id, event_id, checked_in, entry_type, scanned_at) VALUES (?, ?, ?, ?, ?)",
        (user_id, event_id, checked_in, entry_type, scanned_at)
    )
    conn.commit()
