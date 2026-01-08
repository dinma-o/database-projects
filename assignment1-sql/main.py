# Main entry point for the application
#!/usr/bin/env python3
import sys
from database import Database
from auth import Auth
from customer import Customer
from salesperson import Salesperson

def main():
    """Main application entry point"""
    
    # Check command line arguments
    if len(sys.argv) != 2:
        print("Usage: python main.py <database_file>")
        print("Example: python main.py prj-test.db")
        sys.exit(1)
    
    db_file = sys.argv[1]
    
    # Initialize database connection
    print(f"Connecting to database: {db_file}")
    db = Database(db_file)
    
    # Initialize authentication
    auth = Auth(db)
    
    print("\n" + "="*50)
    print("  WELCOME TO E-COMMERCE SYSTEM")
    print("="*50)
    
    # Main application loop
    while True:
        print("\n=== MAIN MENU ===")
        print("1. Login")
        print("2. Sign Up")
        print("3. Exit")
        
        choice = input("\nEnter your choice: ").strip()
        
        if choice == '1':
            if auth.login():
                # Route to appropriate menu based on role
                if auth.current_role == 'customer':
                    customer = Customer(db, auth)
                    customer.menu()
                elif auth.current_role == 'sales':
                    salesperson = Salesperson(db, auth)
                    salesperson.menu()
        
        elif choice == '2':
            auth.signup()
        
        elif choice == '3':
            print("\nThank you for using our system. Goodbye!")
            break
        
        else:
            print("Invalid choice. Please try again.")
    
    # Cleanup
    db.close()

if __name__ == "__main__":
    main()