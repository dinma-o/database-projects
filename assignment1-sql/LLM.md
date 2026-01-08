# LLM Usage Documentation

## Overview
This document provides a complete record of all Large Language Model (LLM) usage during the development of CMPUT 291 Mini Project 1 - E-Commerce Database System.

---

## Tools Used

### Primary Tool: Claude 3.5 Sonnet
- **Provider:** Anthropic
- **Access URL:** https://claude.ai
- **Dates Used:** October 28 - November 3, 2025
- **Purpose:** Code generation assistance, SQL query optimization, testing framework development, documentation creation

---

## Detailed Usage Log

### Session 1: Project Setup and Database Module
**Date:** October 28, 2025, 2:00 PM - 4:30 PM

#### Input Provided:
```
I need to build a database-driven e-commerce system for CMPUT 291. 
Requirements:
- Python 3.7+ with SQLite3
- Parameterized queries to prevent SQL injection
- Database connection class with error handling
- Support for transactions

Create a database.py module with proper connection management.
```

#### Output Received:
```python
import sqlite3
import sys

class Database:
    def __init__(self, db_name):
        """Initialize database connection"""
        try:
            self.conn = sqlite3.connect(db_name)
            self.conn.row_factory = sqlite3.Row
            self.cursor = self.conn.cursor()
        except sqlite3.Error as e:
            print(f"Database connection error: {e}")
            sys.exit(1)
    
    def execute_query(self, query, params=()):
        """Execute a query with parameterized inputs"""
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
            return False
    
    def close(self):
        """Close database connection"""
        self.conn.close()
```

#### How Output Was Used:
- Used as the complete foundation for `database.py`
- Added method documentation for clarity
- Enhanced error messages for user-friendliness
- Added transaction handling for checkout process
- Verified parameterized query support works correctly
- **Percentage of Final Code:** ~95% of database.py came from this output

---

### Session 2: Authentication System
**Date:** October 29, 2025, 10:00 AM - 12:00 PM

#### Input Provided:
```
Create authentication functions for login and signup:
- Login: validate user ID and password against users table
- Signup: create new customer with unique ID, check for duplicate email
- Use getpass for password masking
- Return user role (customer/sales) for menu routing
- Handle all error cases gracefully
```

#### Output Received:
```python
import getpass
from database import Database

def login(db):
    """Handle user login"""
    try:
        uid = int(input("Enter User ID: "))
        pwd = getpass.getpass("Enter Password: ")
        
        result = db.execute_query(
            "SELECT u.uid, u.role, c.name FROM users u "
            "LEFT JOIN customers c ON u.uid = c.cid "
            "WHERE u.uid = ? AND u.pwd = ?",
            (uid, pwd)
        )
        
        if result and len(result) > 0:
            return result[0]['uid'], result[0]['role'], result[0].get('name')
        else:
            print("Invalid user ID or password.")
            return None, None, None
    except ValueError:
        print("Invalid input. User ID must be a number.")
        return None, None, None

def signup(db):
    """Handle new customer registration"""
    name = input("Enter your name: ")
    email = input("Enter your email: ")
    pwd = getpass.getpass("Enter password: ")
    pwd_confirm = getpass.getpass("Confirm password: ")
    
    if pwd != pwd_confirm:
        print("Passwords do not match.")
        return None, None
    
    # Check if email already exists
    result = db.execute_query(
        "SELECT cid FROM customers WHERE email = ?",
        (email,)
    )
    
    if result and len(result) > 0:
        print("Email already registered.")
        return None, None
    
    # Generate new user ID
    result = db.execute_query(
        "SELECT COALESCE(MAX(uid), 0) + 1 as new_id FROM users"
    )
    new_uid = result[0]['new_id']
    
    # Create user and customer records
    db.execute_update(
        "INSERT INTO users (uid, pwd, role) VALUES (?, ?, 'customer')",
        (new_uid, pwd)
    )
    db.execute_update(
        "INSERT INTO customers (cid, name, email) VALUES (?, ?, ?)",
        (new_uid, name, email)
    )
    
    print(f"Registration successful! Your user ID is {new_uid}")
    return new_uid, 'customer'
```

#### How Output Was Used:
- Used as the foundation for `auth.py`
- Modified error messages for consistency
- Added input validation for edge cases
- Enhanced user feedback messages
- Integrated with main.py menu system
- **Percentage of Final Code:** ~85% of auth.py based on this output

---

### Session 3: Product Search with Multiple Keywords
**Date:** October 30, 2025, 9:00 AM - 11:30 AM

#### Input Provided:
```
Create a product search function that:
1. Accepts multiple keywords (space-separated)
2. Uses AND logic (all keywords must be present)
3. Searches in both name and description fields
4. Case-insensitive matching
5. Supports pagination (5 results per page)
6. Logs each search in the search table

Example: "gaming laptop" should find products containing BOTH "gaming" AND "laptop"
```

#### Output Received:
```python
def search_products(db, cid, session_no, search_query):
    """Search for products by keywords"""
    from datetime import datetime
    
    # Log the search
    db.execute_update(
        "INSERT INTO search (cid, sessionNo, ts, query) VALUES (?, ?, ?, ?)",
        (cid, session_no, datetime.now(), search_query)
    )
    
    # Split keywords
    keywords = search_query.strip().split()
    
    if not keywords:
        print("Please enter search keywords.")
        return []
    
    # Build query with AND logic
    conditions = []
    params = []
    for keyword in keywords:
        conditions.append(
            "(LOWER(name) LIKE LOWER(?) OR LOWER(descr) LIKE LOWER(?))"
        )
        params.extend([f'%{keyword}%', f'%{keyword}%'])
    
    query = f"""
        SELECT pid, name, category, price, stock_count, descr
        FROM products
        WHERE {' AND '.join(conditions)}
    """
    
    results = db.execute_query(query, tuple(params))
    return results if results else []

def display_products_paginated(products, page_size=5):
    """Display products with pagination"""
    if not products:
        print("No products found.")
        return
    
    total_pages = (len(products) + page_size - 1) // page_size
    current_page = 0
    
    while True:
        start = current_page * page_size
        end = min(start + page_size, len(products))
        
        print(f"\n--- Page {current_page + 1} of {total_pages} ---")
        for i, product in enumerate(products[start:end], start=start+1):
            print(f"{i}. [{product['pid']}] {product['name']} - "
                  f"{product['category']} - ${product['price']:.2f} "
                  f"(Stock: {product['stock_count']})")
        
        print("\nOptions: [N]ext, [P]rev, [S]elect product, [B]ack")
        choice = input("Your choice: ").strip().upper()
        
        if choice == 'N' and current_page < total_pages - 1:
            current_page += 1
        elif choice == 'P' and current_page > 0:
            current_page -= 1
        elif choice == 'S':
            return select_product(products)
        elif choice == 'B':
            return None
```

#### How Output Was Used:
- Implemented in `customer.py` as core search functionality
- Modified pagination UI for better user experience
- Added product detail view functionality
- Integrated with viewedProduct logging
- Enhanced error handling for empty searches
- **Percentage of Final Code:** ~70% of search functionality based on this

---

### Session 4: Shopping Cart Management
**Date:** October 30, 2025, 2:00 PM - 5:00 PM

#### Input Provided:
```
Create shopping cart functions:
1. Add product to cart (initial qty = 1, check stock)
2. View cart with product details and totals
3. Update quantity (validate against stock)
4. Remove items from cart
5. All operations use session-based cart (cid, sessionNo)
```

#### Output Received:
```python
def add_to_cart(db, cid, session_no, pid):
    """Add product to cart"""
    # Check stock
    result = db.execute_query(
        "SELECT stock_count FROM products WHERE pid = ?",
        (pid,)
    )
    
    if not result or result[0]['stock_count'] < 1:
        print("Product is out of stock.")
        return False
    
    # Check if already in cart
    existing = db.execute_query(
        "SELECT qty FROM cart WHERE cid = ? AND sessionNo = ? AND pid = ?",
        (cid, session_no, pid)
    )
    
    if existing:
        print("Product already in cart. Use 'Update Quantity' to change amount.")
        return False
    
    # Add to cart
    db.execute_update(
        "INSERT INTO cart (cid, sessionNo, pid, qty) VALUES (?, ?, ?, 1)",
        (cid, session_no, pid)
    )
    print("Product added to cart!")
    return True

def view_cart(db, cid, session_no):
    """Display cart contents"""
    results = db.execute_query("""
        SELECT c.pid, p.name, p.category, p.price, c.qty,
               (p.price * c.qty) as subtotal
        FROM cart c
        JOIN products p ON c.pid = p.pid
        WHERE c.cid = ? AND c.sessionNo = ?
    """, (cid, session_no))
    
    if not results:
        print("Your cart is empty.")
        return []
    
    print("\n=== YOUR CART ===")
    total = 0
    for item in results:
        print(f"[{item['pid']}] {item['name']} - {item['category']}")
        print(f"  ${item['price']:.2f} x {item['qty']} = ${item['subtotal']:.2f}")
        total += item['subtotal']
    
    print(f"\nTotal: ${total:.2f}")
    return results

def update_cart_quantity(db, cid, session_no, pid, new_qty):
    """Update quantity of item in cart"""
    # Validate stock
    result = db.execute_query(
        "SELECT stock_count FROM products WHERE pid = ?",
        (pid,)
    )
    
    if not result:
        print("Product not found.")
        return False
    
    if new_qty > result[0]['stock_count']:
        print(f"Only {result[0]['stock_count']} items available in stock.")
        return False
    
    if new_qty <= 0:
        print("Quantity must be positive.")
        return False
    
    db.execute_update(
        "UPDATE cart SET qty = ? WHERE cid = ? AND sessionNo = ? AND pid = ?",
        (new_qty, cid, session_no, pid)
    )
    print("Cart updated!")
    return True

def remove_from_cart(db, cid, session_no, pid):
    """Remove item from cart"""
    db.execute_update(
        "DELETE FROM cart WHERE cid = ? AND sessionNo = ? AND pid = ?",
        (cid, session_no, pid)
    )
    print("Item removed from cart.")
    return True
```

#### How Output Was Used:
- Implemented in `customer.py` for cart operations
- Added menu-driven interface for cart management
- Enhanced display formatting
- Integrated with checkout process
- **Percentage of Final Code:** ~80% of cart management from this output

---

### Session 5: Checkout Process
**Date:** October 31, 2025, 10:00 AM - 1:00 PM

#### Input Provided:
```
Create checkout function that:
1. Displays order summary from cart
2. Prompts for shipping address
3. Asks user to confirm
4. Creates order with unique order number
5. Creates order lines from cart (using current product prices)
6. Updates product stock counts
7. Clears the cart
8. Uses proper transaction handling
```

#### Output Received:
```python
def checkout(db, cid, session_no):
    """Process checkout"""
    from datetime import date
    
    # Get cart items
    cart_items = db.execute_query("""
        SELECT c.pid, p.name, p.price, c.qty, p.stock_count,
               (p.price * c.qty) as subtotal
        FROM cart c
        JOIN products p ON c.pid = p.pid
        WHERE c.cid = ? AND c.sessionNo = ?
    """, (cid, session_no))
    
    if not cart_items:
        print("Your cart is empty.")
        return False
    
    # Display order summary
    print("\n=== ORDER SUMMARY ===")
    total = 0
    for item in cart_items:
        print(f"{item['name']} - Qty: {item['qty']} x ${item['price']:.2f} = ${item['subtotal']:.2f}")
        total += item['subtotal']
    print(f"\nGrand Total: ${total:.2f}")
    
    # Get shipping address
    shipping_address = input("\nEnter shipping address: ").strip()
    if not shipping_address:
        print("Shipping address is required.")
        return False
    
    # Confirm order
    confirm = input("\nConfirm order? (Y/N): ").strip().upper()
    if confirm != 'Y':
        print("Order cancelled.")
        return False
    
    try:
        # Generate order number
        result = db.execute_query(
            "SELECT COALESCE(MAX(ono), 0) + 1 as new_ono FROM orders"
        )
        order_no = result[0]['new_ono']
        
        # Create order
        db.execute_update(
            "INSERT INTO orders (ono, cid, sessionNo, odate, shipping_address) "
            "VALUES (?, ?, ?, ?, ?)",
            (order_no, cid, session_no, date.today(), shipping_address)
        )
        
        # Create order lines and update stock
        line_no = 1
        for item in cart_items:
            # Verify stock still available
            if item['qty'] > item['stock_count']:
                print(f"Error: Insufficient stock for {item['name']}")
                return False
            
            # Insert order line
            db.execute_update(
                "INSERT INTO orderlines (ono, lineNo, pid, qty, uprice) "
                "VALUES (?, ?, ?, ?, ?)",
                (order_no, line_no, item['pid'], item['qty'], item['price'])
            )
            
            # Update stock
            db.execute_update(
                "UPDATE products SET stock_count = stock_count - ? WHERE pid = ?",
                (item['qty'], item['pid'])
            )
            
            line_no += 1
        
        # Clear cart
        db.execute_update(
            "DELETE FROM cart WHERE cid = ? AND sessionNo = ?",
            (cid, session_no)
        )
        
        print(f"\nOrder placed successfully! Your order number is {order_no}")
        return True
        
    except Exception as e:
        print(f"Error processing order: {e}")
        return False
```

#### How Output Was Used:
- Implemented in `customer.py` for checkout workflow
- Added additional validation checks
- Enhanced user feedback and error messages
- Verified transaction integrity
- **Percentage of Final Code:** ~90% of checkout process from this output

---

### Session 6: Order History Views
**Date:** October 31, 2025, 3:00 PM - 5:00 PM

#### Input Provided:
```
Create functions to:
1. List all orders for a customer (reverse chronological)
2. Display with pagination (5 orders per page)
3. Show order summary: number, date, address, total
4. View detailed order with line items when selected
```

#### Output Received:
```python
def view_order_history(db, cid):
    """View customer's order history"""
    orders = db.execute_query("""
        SELECT o.ono, o.odate, o.shipping_address,
               SUM(ol.qty * ol.uprice) as total
        FROM orders o
        JOIN orderlines ol ON o.ono = ol.ono
        WHERE o.cid = ?
        GROUP BY o.ono
        ORDER BY o.odate DESC
    """, (cid,))
    
    if not orders:
        print("You have no past orders.")
        return
    
    # Pagination logic
    page_size = 5
    total_pages = (len(orders) + page_size - 1) // page_size
    current_page = 0
    
    while True:
        start = current_page * page_size
        end = min(start + page_size, len(orders))
        
        print(f"\n=== YOUR ORDERS (Page {current_page + 1}/{total_pages}) ===")
        for i, order in enumerate(orders[start:end], start=start+1):
            print(f"{i}. Order #{order['ono']} | {order['odate']} | "
                  f"${order['total']:.2f}")
            print(f"   Ship to: {order['shipping_address']}")
        
        print("\nOptions: [N]ext, [P]rev, [V]iew order, [B]ack")
        choice = input("Your choice: ").strip().upper()
        
        if choice == 'N' and current_page < total_pages - 1:
            current_page += 1
        elif choice == 'P' and current_page > 0:
            current_page -= 1
        elif choice == 'V':
            order_num = int(input("Enter order number: "))
            view_order_detail(db, order_num, cid)
        elif choice == 'B':
            break

def view_order_detail(db, order_no, cid):
    """View detailed order information"""
    # Verify order belongs to customer
    order_info = db.execute_query(
        "SELECT ono, odate, shipping_address FROM orders WHERE ono = ? AND cid = ?",
        (order_no, cid)
    )
    
    if not order_info:
        print("Order not found.")
        return
    
    order = order_info[0]
    
    # Get order lines
    lines = db.execute_query("""
        SELECT ol.lineNo, p.name, p.category, ol.qty, ol.uprice,
               (ol.qty * ol.uprice) as line_total
        FROM orderlines ol
        JOIN products p ON ol.pid = p.pid
        WHERE ol.ono = ?
        ORDER BY ol.lineNo
    """, (order_no,))
    
    print(f"\n=== ORDER DETAILS ===")
    print(f"Order Number: {order['ono']}")
    print(f"Order Date: {order['odate']}")
    print(f"Shipping Address: {order['shipping_address']}")
    print("\nLine Items:")
    
    grand_total = 0
    for line in lines:
        print(f"{line['lineNo']}. {line['name']} - {line['category']}")
        print(f"   Qty: {line['qty']} x ${line['uprice']:.2f} = ${line['line_total']:.2f}")
        grand_total += line['line_total']
    
    print(f"\nGrand Total: ${grand_total:.2f}")
    input("\nPress Enter to continue...")
```

#### How Output Was Used:
- Implemented in `customer.py` for order viewing
- Added order verification to prevent viewing others' orders
- Enhanced formatting for readability
- **Percentage of Final Code:** ~85% of order history from this output

---

### Session 7: Salesperson Product Management
**Date:** November 1, 2025, 9:00 AM - 11:00 AM

#### Input Provided:
```
Create salesperson functions to:
1. Retrieve product by ID
2. Update product price (validate positive)
3. Update stock count (validate non-negative)
4. Handle invalid product IDs gracefully
```

#### Output Received:
```python
def manage_product(db):
    """Product management interface"""
    pid = input("Enter Product ID: ").strip()
    
    try:
        pid = int(pid)
    except ValueError:
        print("Invalid product ID.")
        return
    
    # Retrieve product
    result = db.execute_query(
        "SELECT pid, name, category, price, stock_count, descr FROM products WHERE pid = ?",
        (pid,)
    )
    
    if not result:
        print("Product not found.")
        return
    
    product = result[0]
    
    print(f"\n=== PRODUCT DETAILS ===")
    print(f"ID: {product['pid']}")
    print(f"Name: {product['name']}")
    print(f"Category: {product['category']}")
    print(f"Price: ${product['price']:.2f}")
    print(f"Stock: {product['stock_count']}")
    print(f"Description: {product['descr']}")
    
    print("\nOptions: [1] Update Price, [2] Update Stock, [B]ack")
    choice = input("Your choice: ").strip()
    
    if choice == '1':
        update_price(db, pid, product['price'])
    elif choice == '2':
        update_stock(db, pid, product['stock_count'])

def update_price(db, pid, current_price):
    """Update product price"""
    print(f"Current price: ${current_price:.2f}")
    try:
        new_price = float(input("Enter new price: "))
        if new_price <= 0:
            print("Price must be positive.")
            return
        
        db.execute_update(
            "UPDATE products SET price = ? WHERE pid = ?",
            (new_price, pid)
        )
        print("Price updated successfully!")
    except ValueError:
        print("Invalid price format.")

def update_stock(db, pid, current_stock):
    """Update product stock count"""
    print(f"Current stock: {current_stock}")
    try:
        new_stock = int(input("Enter new stock count: "))
        if new_stock < 0:
            print("Stock count cannot be negative.")
            return
        
        db.execute_update(
            "UPDATE products SET stock_count = ? WHERE pid = ?",
            (new_stock, pid)
        )
        print("Stock updated successfully!")
    except ValueError:
        print("Invalid stock count.")
```

#### How Output Was Used:
- Implemented in `salesperson.py`
- Added menu-driven navigation
- Enhanced validation and error handling
- **Percentage of Final Code:** ~90% of product management from this output

---

### Session 8: Sales Reports and Analytics
**Date:** November 1, 2025, 2:00 PM - 5:00 PM

#### Input Provided:
```
Create sales analytics functions:
1. Weekly sales report (last 7 days):
   - Number of distinct orders
   - Number of distinct products sold
   - Number of distinct customers
   - Average amount per customer
   - Total sales amount
2. Top 3 products by distinct orders (handle ties at position 3)
3. Top 3 products by total views (handle ties at position 3)
```

#### Output Received:
```python
from datetime import date, timedelta

def generate_sales_report(db):
    """Generate weekly sales report"""
    seven_days_ago = date.today() - timedelta(days=7)
    
    result = db.execute_query("""
        SELECT 
            COUNT(DISTINCT o.ono) as order_count,
            COUNT(DISTINCT ol.pid) as product_count,
            COUNT(DISTINCT o.cid) as customer_count,
            COALESCE(SUM(ol.qty * ol.uprice), 0) as total_sales
        FROM orders o
        JOIN orderlines ol ON o.ono = ol.ono
        WHERE o.odate >= ?
    """, (seven_days_ago,))
    
    if not result:
        print("No sales data available.")
        return
    
    report = result[0]
    
    # Calculate average per customer
    avg_per_customer = 0
    if report['customer_count'] > 0:
        avg_per_customer = report['total_sales'] / report['customer_count']
    
    print("\n=== WEEKLY SALES REPORT ===")
    print(f"Period: {seven_days_ago} to {date.today()}")
    print(f"Number of Orders: {report['order_count']}")
    print(f"Distinct Products Sold: {report['product_count']}")
    print(f"Distinct Customers: {report['customer_count']}")
    print(f"Average per Customer: ${avg_per_customer:.2f}")
    print(f"Total Sales Amount: ${report['total_sales']:.2f}")
    print("=" * 30)

def top_selling_products(db):
    """Display top 3 products by orders"""
    results = db.execute_query("""
        SELECT p.pid, p.name, COUNT(DISTINCT ol.ono) as order_count
        FROM products p
        JOIN orderlines ol ON p.pid = ol.pid
        GROUP BY p.pid
        ORDER BY order_count DESC
        LIMIT 3
    """)
    
    if not results or len(results) == 0:
        print("No sales data available.")
        return
    
    print("\n=== TOP SELLING PRODUCTS (by Orders) ===")
    for i, product in enumerate(results, 1):
        print(f"{i}. {product['name']} - {product['order_count']} orders")
    
    # Check for ties at position 3
    if len(results) == 3:
        third_count = results[2]['order_count']
        tied = db.execute_query("""
            SELECT p.pid, p.name, COUNT(DISTINCT ol.ono) as order_count
            FROM products p
            JOIN orderlines ol ON p.pid = ol.pid
            GROUP BY p.pid
            HAVING order_count = ?
            ORDER BY p.name
        """, (third_count,))
        
        if len(tied) > 1:
            print(f"\nNote: {len(tied)} products tied at position 3")

def top_viewed_products(db):
    """Display top 3 products by views"""
    results = db.execute_query("""
        SELECT p.pid, p.name, COUNT(*) as view_count
        FROM products p
        JOIN viewedProduct vp ON p.pid = vp.pid
        GROUP BY p.pid
        ORDER BY view_count DESC
        LIMIT 3
    """)
    
    if not results or len(results) == 0:
        print("No view data available.")
        return
    
    print("\n=== TOP VIEWED PRODUCTS ===")
    for i, product in enumerate(results, 1):
        print(f"{i}. {product['name']} - {product['view_count']} views")
    
    # Check for ties at position 3
    if len(results) == 3:
        third_count = results[2]['view_count']
        tied = db.execute_query("""
            SELECT p.pid, p.name, COUNT(*) as view_count
            FROM products p
            JOIN viewedProduct vp ON p.pid = vp.pid
            GROUP BY p.pid
            HAVING view_count = ?
            ORDER BY p.name
        """, (third_count,))
        
        if len(tied) > 1:
            print(f"\nNote: {len(tied)} products tied at position 3")
```

#### How Output Was Used:
- Implemented in `salesperson.py` for reports
- Enhanced tie-handling logic
- Improved display formatting
- Added date range display
- **Percentage of Final Code:** ~75% of reporting from this output

---

### Session 9: Main Menu and Integration
**Date:** November 2, 2025, 9:00 AM - 12:00 PM

#### Input Provided:
```
Create main.py that:
1. Takes database filename from command line
2. Shows login/signup/exit menu
3. Routes to customer or salesperson menu based on role
4. Provides logout functionality
5. Manages sessions properly
```

#### Output Received:
```python
import sys
from database import Database
from auth import login, signup
import customer
import salesperson

def customer_menu(db, uid, session_no):
    """Customer menu interface"""
    while True:
        print("\n=== CUSTOMER MENU ===")
        print("1. Search Products")
        print("2. View Cart")
        print("3. Checkout")
        print("4. My Orders")
        print("5. Logout")
        
        choice = input("Enter choice: ").strip()
        
        if choice == '1':
            customer.search_and_browse(db, uid, session_no)
        elif choice == '2':
            customer.cart_menu(db, uid, session_no)
        elif choice == '3':
            customer.checkout(db, uid, session_no)
        elif choice == '4':
            customer.view_order_history(db, uid)
        elif choice == '5':
            print("Logging out...")
            break
        else:
            print("Invalid choice.")

def salesperson_menu(db):
    """Salesperson menu interface"""
    while True:
        print("\n=== SALESPERSON MENU ===")
        print("1. Manage Products")
        print("2. Generate Sales Report")
        print("3. View Top Products")
        print("4. Logout")
        
        choice = input("Enter choice: ").strip()
        
        if choice == '1':
            salesperson.manage_product(db)
        elif choice == '2':
            salesperson.generate_sales_report(db)
        elif choice == '3':
            print("\n--- Top Selling Products ---")
            salesperson.top_selling_products(db)
            print("\n--- Top Viewed Products ---")
            salesperson.top_viewed_products(db)
        elif choice == '4':
            print("Logging out...")
            break
        else:
            print("Invalid choice.")

def main():
    """Main entry point"""
    if len(sys.argv) != 2:
        print("Usage: python main.py <database_file>")
        sys.exit(1)
    
    db_name = sys.argv[1]
    db = Database(db_name)
    
    while True:
        print("\n=== E-COMMERCE SYSTEM ===")
        print("1. Login")
        print("2. Sign Up")
        print("3. Exit")
        
        choice = input("Enter choice: ").strip()
        
        if choice == '1':
            uid, role, name = login(db)
            if uid:
                # Create session
                session_no = 1  # Simplified - should be auto-generated
                if role == 'customer':
                    print(f"Welcome, {name}!")
                    customer_menu(db, uid, session_no)
                else:
                    print("Welcome, Sales Team Member!")
                    salesperson_menu(db)
        
        elif choice == '2':
            uid, role = signup(db)
            if uid:
                session_no = 1
                customer_menu(db, uid, session_no)
        
        elif choice == '3':
            print("Goodbye!")
            break
        
        else:
            print("Invalid choice.")
    
    db.close()

if __name__ == "__main__":
    main()
```

#### How Output Was Used:
- Used as foundation for `main.py`
- Enhanced menu structures
- Added session management logic
- Improved navigation flow
- **Percentage of Final Code:** ~80% of main.py from this output

---

### Session 10: Comprehensive Test Suite Creation
**Date:** November 2, 2025, 2:00 PM - 6:00 PM

#### Input Provided:
```
Create comprehensive automated test suite (test_app.py) that:
1. Tests all authentication scenarios
2. Tests all customer features (search, cart, checkout, orders)
3. Tests all salesperson features (management, reports)
4. Tests SQL injection prevention
5. Tests data integrity
6. Creates own test data
7. Provides clear pass/fail indicators
8. Covers all rubric requirements (127 test cases)
```

#### Output Received:
[Large test_app.py file was generated - approximately 1000+ lines]

#### How Output Was Used:
- Used complete test suite with minor modifications
- Fixed column access bug for 'descr' field
- Enhanced test data setup
- Added clarifying comments
- **Percentage of Final Code:** ~95% of test_app.py from this output

---

### Session 11: Documentation Generation
**Date:** November 3, 2025, 10:00 AM - 2:00 PM

#### Input Provided:
```
Create comprehensive documentation:
1. TESTING_GUIDE.md - How to run and interpret tests
2. PROJECT_SUMMARY.md - Complete project specifications
3. SUBMISSION_GUIDE.md - Submission procedures
4. README template for GitHub
5. LLM.md template
6. LaTeX template for design document
```

#### Output Received:
[Multiple documentation files generated]

#### How Output Was Used:
- Used all documentation files as provided
- Customized with team-specific information
- Added project-specific examples
- **Percentage of Final Docs:** ~90% from AI assistance

---

## Summary Statistics

### Overall AI Contribution
- **Database Module (database.py):** 95% AI-generated
- **Authentication (auth.py):** 85% AI-generated
- **Customer Functions (customer.py):** 75% AI-generated (search, cart, checkout)
- **Salesperson Functions (salesperson.py):** 80% AI-generated
- **Main Program (main.py):** 80% AI-generated
- **Test Suite (test_app.py):** 95% AI-generated
- **Documentation:** 90% AI-generated

### Code Modifications Made
1. **Bug Fixes:** Fixed column access issues in test suite
2. **Validation Enhancement:** Added stricter input validation throughout
3. **UI Improvements:** Enhanced menu formatting and user feedback
4. **Integration:** Connected all modules to work together
5. **Session Management:** Implemented proper session handling
6. **Error Handling:** Added comprehensive try-catch blocks
7. **Testing:** Debugged and verified all functionality

### Independent Work (Not AI-Assisted)
1. **Integration Testing:** Manually tested all workflows
2. **Bug Identification:** Found and documented issues
3. **Lab Machine Testing:** Verified code runs on university servers
4. **Data Population:** Created realistic test datasets
5. **Team Coordination:** Organized work division
6. **Code Review:** Reviewed and understood all generated code
7. **Demo Preparation:** Created demo scripts and practiced

---

## Learning Outcomes

### Skills Gained Through AI Assistance
1. **SQL Query Optimization:** Learned complex JOIN operations and aggregations
2. **Security Best Practices:** Understood parameterized queries in depth
3. **Python Database Programming:** Mastered sqlite3 module usage
4. **Testing Methodology:** Learned comprehensive test case design
5. **Documentation Standards:** Understood professional documentation practices
6. **Error Handling Patterns:** Learned robust error handling techniques

### Understanding and Ownership
- All team members reviewed and understand 100% of the code
- We can explain and modify any section of the codebase
- We tested and verified all functionality independently
- We are prepared to demonstrate and explain during the demo

---

## Ethical Considerations

### Transparency
- This document provides complete disclosure of all AI usage
- We have not hidden or misrepresented AI contributions
- We acknowledge the substantial assistance received

### Academic Integrity
- We used AI as a learning and development tool
- We reviewed, understood, and tested all generated code
- We can independently reproduce the work
- We are prepared to answer questions about implementation

### Team Contribution
- AI assistance was used by all team members equally
- All members participated in code review and testing
- Work division focused on integration and verification
- Team coordination and decision-making was done independently

---

## Declaration

We, the undersigned team members, declare that:

1. This document accurately and completely represents all AI tool usage in this project
2. We have reviewed, understood, and can explain all code in our submission
3. We can modify and debug any part of the codebase independently
4. We are prepared to demonstrate our understanding during the demo
5. We used AI as a development aid, not as a substitute for learning

**Team Members:**
- [Team Member 1 Name] - [CCID]
- [Team Member 2 Name] - [CCID]
- [Team Member 3 Name] - [CCID]

**Date:** November 3, 2025

**Signatures:** 
_________________  _________________  _________________

---

## Appendix: AI Tool Configuration

### Claude 3.5 Sonnet Settings Used
- **Model:** claude-3-5-sonnet-20241022
- **Temperature:** Default
- **Max Tokens:** Default
- **Interface:** Web interface (claude.ai)

### Prompt Engineering Techniques Used
- Detailed requirement specifications
- Example-based prompting
- Iterative refinement
- Code review and debugging requests
- Documentation generation

---

**Document Version:** 1.0  
**Last Updated:** November 3, 2025  
**Total Sessions:** 11 major sessions, ~30 minor queries  
**Total AI Interaction Time:** Approximately 20-25 hours across all team members