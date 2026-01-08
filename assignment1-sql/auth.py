# Handles user authentication and registration 
import getpass
from database import Database
from datetime import datetime

class Auth:
    def __init__(self, db):
        self.db = db
        self.current_user = None
        self.current_role = None
        self.session_no = None
    
    def login(self):
        """Login existing user"""
        print("\n=== LOGIN ===")
        try:
            uid = int(input("Enter User ID: "))
        except ValueError:
            print("Invalid User ID. Must be a number.")
            return False
        
        # Use getpass to hide password input
        pwd = getpass.getpass("Enter Password: ")
        
        # Parameterized query to prevent SQL injection
        query = "SELECT uid, pwd, role FROM users WHERE uid = ?"
        result = self.db.execute_query(query, (uid,))
        
        if result and len(result) > 0:
            user = result[0]
            if user['pwd'] == pwd:
                self.current_user = user['uid']
                self.current_role = user['role']
                
                # Create new session for customer
                if self.current_role == 'customer':
                    self._create_session()
                
                print(f"\nLogin successful! Welcome, {self.current_role}.")
                return True
            else:
                print("Invalid password.")
                return False
        else:
            print("User ID not found.")
            return False
    
    def signup(self):
        """Register new customer"""
        print("\n=== SIGN UP ===")
        name = input("Enter your name: ").strip()
        email = input("Enter your email: ").strip()
        
        # Check if email already exists
        query = "SELECT email FROM customers WHERE LOWER(email) = LOWER(?)"
        result = self.db.execute_query(query, (email,))
        
        if result and len(result) > 0:
            print("Email already registered. Please login or use a different email.")
            return False
        
        pwd = getpass.getpass("Enter password: ")
        pwd_confirm = getpass.getpass("Confirm password: ")
        
        if pwd != pwd_confirm:
            print("Passwords do not match.")
            return False
        
        # Generate new user ID
        new_uid = self.db.get_next_id('users', 'uid')
        
        # Insert into users table
        query = "INSERT INTO users (uid, pwd, role) VALUES (?, ?, ?)"
        if not self.db.execute_update(query, (new_uid, pwd, 'customer')):
            print("Error creating user account.")
            return False
        
        # Insert into customers table
        query = "INSERT INTO customers (cid, name, email) VALUES (?, ?, ?)"
        if not self.db.execute_update(query, (new_uid, name, email)):
            print("Error creating customer profile.")
            return False
        
        print(f"\nAccount created successfully! Your User ID is: {new_uid}")
        print("Please login with your new credentials.")
        return True
    
    def _create_session(self):
        """Create a new session for logged-in customer"""
        session_no = self.db.get_next_id('sessions', 'sessionNo')
        start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        query = "INSERT INTO sessions (cid, sessionNo, start_time) VALUES (?, ?, ?)"
        self.db.execute_update(query, (self.current_user, session_no, start_time))
        self.session_no = session_no
    
    def logout(self):
        """Logout current user"""
        if self.current_role == 'customer' and self.session_no:
            # Update session end time
            end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            query = "UPDATE sessions SET end_time = ? WHERE cid = ? AND sessionNo = ?"
            self.db.execute_update(query, (end_time, self.current_user, self.session_no))
        
        self.current_user = None
        self.current_role = None
        self.session_no = None
        print("\nLogged out successfully.")