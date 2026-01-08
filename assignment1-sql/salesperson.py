# Implements salesperson functionalities
from datetime import datetime, timedelta

class Salesperson:
    def __init__(self, db, auth):
        self.db = db
        self.auth = auth
    
    def menu(self):
        """Display salesperson menu"""
        while True:
            print("\n=== SALESPERSON MENU ===")
            print("1. Check/Update products")
            print("2. Sales report")
            print("3. Top-selling products")
            print("4. Logout")
            
            choice = input("\nEnter your choice: ").strip()
            
            if choice == '1':
                self.manage_product()
            elif choice == '2':
                self.sales_report()
            elif choice == '3':
                self.top_selling()
            elif choice == '4':
                self.auth.logout()
                break
            else:
                print("Invalid choice. Please try again.")
    
    def manage_product(self):
        """Check and update product information"""
        print("\n=== PRODUCT MANAGEMENT ===")
        
        try:
            pid = int(input("Enter Product ID: "))
        except ValueError:
            print("Invalid Product ID.")
            return
        
        # Retrieve product
        query = "SELECT * FROM products WHERE pid = ?"
        result = self.db.execute_query(query, (pid,))
        
        if not result or len(result) == 0:
            print("Product not found.")
            return
        
        product = result[0]
        print(f"\nProduct ID: {product['pid']}")
        print(f"Name: {product['name']}")
        print(f"Category: {product['category']}")
        print(f"Price: ${product['price']:.2f}")
        print(f"Stock: {product['stock_count']}")
        print(f"Description: {product['descr']}")
        
        # Update options
        print("\nUpdate: [P]rice, [S]tock, [B]ack")
        choice = input("Enter choice: ").strip().lower()
        
        if choice == 'p':
            try:
                new_price = float(input("Enter new price: "))
                if new_price <= 0:
                    print("Price must be positive.")
                else:
                    query = "UPDATE products SET price = ? WHERE pid = ?"
                    self.db.execute_update(query, (new_price, pid))
                    print("Price updated successfully!")
            except ValueError:
                print("Invalid price.")
        
        elif choice == 's':
            try:
                new_stock = int(input("Enter new stock count: "))
                if new_stock < 0:
                    print("Stock count cannot be negative.")
                else:
                    query = "UPDATE products SET stock_count = ? WHERE pid = ?"
                    self.db.execute_update(query, (new_stock, pid))
                    print("Stock updated successfully!")
            except ValueError:
                print("Invalid stock count.")
    
    def sales_report(self):
        """Generate weekly sales report (last 7 days)"""
        print("\n=== WEEKLY SALES REPORT ===")
        
        # Calculate date 7 days ago
        seven_days_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        
        # Number of distinct orders
        query = "SELECT COUNT(DISTINCT ono) as order_count FROM orders WHERE odate >= ?"
        result = self.db.execute_query(query, (seven_days_ago,))
        order_count = result[0]['order_count'] if result else 0
        
        # Number of distinct products sold
        query = """
            SELECT COUNT(DISTINCT ol.pid) as product_count
            FROM orderlines ol
            JOIN orders o ON ol.ono = o.ono
            WHERE o.odate >= ?
        """
        result = self.db.execute_query(query, (seven_days_ago,))
        product_count = result[0]['product_count'] if result else 0
        
        # Number of distinct customers
        query = "SELECT COUNT(DISTINCT cid) as customer_count FROM orders WHERE odate >= ?"
        result = self.db.execute_query(query, (seven_days_ago,))
        customer_count = result[0]['customer_count'] if result else 0
        
        # Total sales and average per customer
        query = """
            SELECT SUM(ol.qty * ol.uprice) as total_sales
            FROM orderlines ol
            JOIN orders o ON ol.ono = o.ono
            WHERE o.odate >= ?
        """
        result = self.db.execute_query(query, (seven_days_ago,))
        total_sales = result[0]['total_sales'] if result and result[0]['total_sales'] else 0
        
        avg_per_customer = total_sales / customer_count if customer_count > 0 else 0
        
        print(f"\nReport Period: Last 7 days (from {seven_days_ago})")
        print(f"Total Orders: {order_count}")
        print(f"Distinct Products Sold: {product_count}")
        print(f"Distinct Customers: {customer_count}")
        print(f"Average per Customer: ${avg_per_customer:.2f}")
        print(f"Total Sales: ${total_sales:.2f}")
        
        input("\nPress Enter to continue...")
    
    def top_selling(self):
        """Display top 3 products by orders and by views"""
        print("\n=== TOP-SELLING PRODUCTS ===")
        
        # Top 3 by distinct orders (with ties at position 3)
        print("\n--- By Orders ---")
        query = """
            SELECT p.pid, p.name, COUNT(DISTINCT ol.ono) as order_count
            FROM products p
            JOIN orderlines ol ON p.pid = ol.pid
            GROUP BY p.pid
            ORDER BY order_count DESC
        """
        results = self.db.execute_query(query)
        
        if results and len(results) > 0:
            # Get top 3 with ties
            top_products = []
            for i, row in enumerate(results):
                if i < 3:
                    top_products.append(row)
                elif i == 3 and row['order_count'] == results[2]['order_count']:
                    # Handle ties at position 3
                    top_products.append(row)
                elif i > 3 and row['order_count'] == results[2]['order_count']:
                    top_products.append(row)
                else:
                    break
            
            for i, p in enumerate(top_products, 1):
                print(f"{i}. {p['name']} (PID: {p['pid']}) - {p['order_count']} orders")
        else:
            print("No order data available.")
        
        # Top 3 by views (with ties at position 3)
        print("\n--- By Views ---")
        query = """
            SELECT p.pid, p.name, COUNT(*) as view_count
            FROM products p
            JOIN viewedProduct vp ON p.pid = vp.pid
            GROUP BY p.pid
            ORDER BY view_count DESC
        """
        results = self.db.execute_query(query)
        
        if results and len(results) > 0:
            # Get top 3 with ties
            top_products = []
            for i, row in enumerate(results):
                if i < 3:
                    top_products.append(row)
                elif i == 3 and row['view_count'] == results[2]['view_count']:
                    # Handle ties at position 3
                    top_products.append(row)
                elif i > 3 and row['view_count'] == results[2]['view_count']:
                    top_products.append(row)
                else:
                    break
            
            for i, p in enumerate(top_products, 1):
                print(f"{i}. {p['name']} (PID: {p['pid']}) - {p['view_count']} views")
        else:
            print("No view data available.")
        
        input("\nPress Enter to continue...")