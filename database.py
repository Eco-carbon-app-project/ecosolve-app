import sqlite3
import pandas as pd
import json

DB_NAME = "ecosolve.db"

# ==========================================
# 🛠️ DATABASE SETUP & CONNECTION
# ==========================================
def get_connection():
    """Establishes a connection to the SQLite database."""
    # check_same_thread=False allows Streamlit to interact with SQLite smoothly
    return sqlite3.connect(DB_NAME, check_same_thread=False)

def init_db():
    """Creates the necessary tables if they don't exist yet."""
    conn = get_connection()
    c = conn.cursor()
    
    # Table 1: Users Account Information
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            block TEXT NOT NULL,
            sec_q TEXT NOT NULL,
            sec_a TEXT NOT NULL
        )
    ''')
    
    # Table 2: Action Logs (Records every time a user hits Calculate)
    c.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            date TEXT NOT NULL,
            used_json TEXT NOT NULL,
            avoided_json TEXT NOT NULL,
            net_saved REAL NOT NULL,
            points INTEGER NOT NULL,
            FOREIGN KEY(username) REFERENCES users(username)
        )
    ''')
    
    conn.commit()
    conn.close()

# ==========================================
# 👤 AUTH & PROFILE HELPER FUNCTIONS
# ==========================================
def get_user(identifier):
    """Fetches user details by Username OR Email for flexible login."""
    conn = get_connection()
    # Row factory lets us access columns like a dictionary
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ? OR email = ?", (identifier, identifier))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None

def create_user(username, email, password, block, sec_q, sec_a):
    """Inserts a new user into the database securely."""
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, email, password, block, sec_q, sec_a) VALUES (?, ?, ?, ?, ?, ?)",
                  (username, email, password, block, sec_q, sec_a))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        # This triggers if the username or email already exists
        conn.close()
        return False

def update_password(identifier, new_password):
    """Resets the user's password."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE users SET password = ? WHERE username = ? OR email = ?", (new_password, identifier, identifier))
    conn.commit()
    conn.close()

def get_user_profile(username):
    """Fetches specific user details for the Edit Profile page."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT email, block FROM users WHERE username = ?", (username,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None

def update_profile(username, new_email, new_block):
    """Updates the user's email and campus block."""
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("UPDATE users SET email = ?, block = ? WHERE username = ?", (new_email, new_block, username))
        conn.commit()
        conn.close()
        return True, "Profile updated successfully!"
    except sqlite3.IntegrityError:
        conn.close()
        return False, "Error: That email is already registered to another account."

# ==========================================
# 📝 ACTION LOGGING
# ==========================================
def save_log(username, date, used_json, avoided_json, net_saved, points):
    """Saves a user's calculated footprint log."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO logs (username, date, used_json, avoided_json, net_saved, points) VALUES (?, ?, ?, ?, ?, ?)",
              (username, date, used_json, avoided_json, net_saved, points))
    conn.commit()
    conn.close()

# ==========================================
# 🏆 LEADERBOARD QUERIES (Pandas Integration)
# ==========================================
def get_leaderboard():
    """
    Returns a Pandas DataFrame of the Top Users, summing their total points 
    and total carbon saved across all their logs.
    """
    conn = get_connection()
    # We use Pandas to run the SQL query and instantly get a DataFrame back for Streamlit
    query = '''
        SELECT 
            u.username as Username,
            u.block as Block,
            SUM(l.points) as 'Total Points',
            SUM(l.net_saved) as 'Total CO2 Saved (kg)'
        FROM users u
        JOIN logs l ON u.username = l.username
        GROUP BY u.username
        ORDER BY 'Total Points' DESC
    '''
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    # Clean up the format before sending it to the UI
    if not df.empty:
        df = df.sort_values(by="Total Points", ascending=False)
        df['Total CO2 Saved (kg)'] = df['Total CO2 Saved (kg)'].round(3)
        # Shift the index to start at 1 instead of 0 for leaderboard rankings
        df.index = df.index + 1
    return df

def get_block_leaderboard():
    """
    Returns a Pandas DataFrame of the Top Campus Blocks to plot a chart.
    """
    conn = get_connection()
    query = '''
        SELECT 
            u.block as Block,
            SUM(l.points) as 'Points'
        FROM users u
        JOIN logs l ON u.username = l.username
        GROUP BY u.block
        ORDER BY 'Points' DESC
    '''
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df