import sqlite3

def init_db():
    conn = sqlite3.connect("goalsphere.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS subscribers (user_id INTEGER PRIMARY KEY)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS sent_news (url_hash TEXT PRIMARY KEY)''')
    conn.commit()
    conn.close()

def subscribe_user(user_id):
    conn = sqlite3.connect("goalsphere.db")
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO subscribers (user_id) VALUES (?)", (user_id,))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def unsubscribe_user(user_id):
    conn = sqlite3.connect("goalsphere.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM subscribers WHERE user_id = ?", (user_id,))
    success = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return success

def get_all_subscribers():
    conn = sqlite3.connect("goalsphere.db")
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM subscribers")
    users = [row[0] for row in cursor.fetchall()]
    conn.close()
    return users

def is_news_new(url_hash):
    conn = sqlite3.connect("goalsphere.db")
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM sent_news WHERE url_hash = ?", (url_hash,))
    exists = cursor.fetchone()
    if not exists:
        cursor.execute("INSERT INTO sent_news (url_hash) VALUES (?)", (url_hash,))
        conn.commit()
    conn.close()
    return not exists
