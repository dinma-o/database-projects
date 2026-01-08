# This file handles database connections and common utilities
import sqlite3
import sys
from datetime import datetime

class Database:
    def __init__(self, db_name):
        """Initialize database connection"""
        try:
            self.conn = sqlite3.connect(db_name)
            self.conn.row_factory = sqlite3.Row  # Access columns by name
            self.cursor = self.conn.cursor()
        except sqlite3.Error as e:
            print(f"Database connection error: {e}")
            sys.exit(1)
    
    def execute_query(self, query, params=()):
        """Execute a query with parameterized inputs (prevents SQL injection)"""
        try:
            self.cursor.execute(query, params)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Query execution error: {e}")
            return None
    
    def execute_update(self, query, params=()):
        """Execute INSERT, UPDATE, DELETE queries"""
        try:
            self.cursor.execute(query, params)
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Update error: {e}")
            self.conn.rollback()
            return False
    
    def get_next_id(self, table, id_column):
        """Generate next ID for a table"""
        query = f"SELECT MAX({id_column}) as max_id FROM {table}"
        result = self.execute_query(query)
        if result and result[0]['max_id']:
            return result[0]['max_id'] + 1
        return 1
    
    def close(self):
        """Close database connection"""
        self.conn.close()