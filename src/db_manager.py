# src/db_manager.py
import sqlite3
import os

# Project root: one level above src/
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_DIR = os.path.join(BASE_DIR, "database")
# Make sure the database directory exists
os.makedirs(DB_DIR, exist_ok=True)
DB_PATH = os.path.join(DB_DIR, "visual_novel.db")

class DatabaseManager:
    """Manages database connection and basic operations"""

    def __init__(self, db_path=DB_PATH):
        """Initialize database connection"""
        self.db_path = db_path
        self.conn = None

    def connect(self):
        """Establish connection to database"""
        try:
            print(f"Connecting to database at: {self.db_path}")
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            print("Connected successfully")
            return self.conn
        except sqlite3.Error as e:
            print(f"Error connecting to database: {e}")
            self.conn = None
            return None

    def disconnect(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            print("Database connection closed")

    def execute_query(self, query, params=None):
        """Execute a SELECT query and return results"""
        if not self.conn:
            print("No active database connection in execute_query")
            return None
        try:
            cur = self.conn.cursor()
            if params:
                cur.execute(query, params)
            else:
                cur.execute(query)
            return cur.fetchall()
        except sqlite3.Error as e:
            print(f"Error executing query: {e}")
            return None

    def execute_update(self, query, params=None):
        """Execute INSERT, UPDATE, or DELETE query"""
        if not self.conn:
            print("No active database connection in execute_update")
            return None
        try:
            cur = self.conn.cursor()
            if params:
                cur.execute(query, params)
            else:
                cur.execute(query)
            self.conn.commit()
            return cur.lastrowid
        except sqlite3.Error as e:
            print(f"Error executing update: {e}")
            self.conn.rollback()
            return None

    def execute_script(self, script_path):
        """Execute SQL script file"""
        if not self.conn:
            print("No active database connection in execute_script")
            return False
        try:
            with open(script_path, "r") as f:
                script = f.read()
            cur = self.conn.cursor()
            cur.executescript(script)
            self.conn.commit()
            print(f"Script executed successfully: {script_path}")
            return True
        except FileNotFoundError:
            print(f"Script file not found: {script_path}")
            return False
        except sqlite3.Error as e:
            print(f"Error executing script: {e}")
            return False
