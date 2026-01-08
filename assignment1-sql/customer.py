# Implements all customer functionalities
from datetime import datetime

class Customer:
    def __init__(self, db, auth):
        self.db = db
        self.auth = auth
    
    def menu(self):
        """Display customer menu"""
        while True:
            print("\n=== CUSTOMER MENU ===")
            print("1. Search for products")
            print("2. View cart")
            print("3. My orders")
            print("4. Logout")
            
            choice = input("\nEnter your choice: ").strip()
            
            if choice == '1':
                self.search_products()
            elif choice == '2':
                self.view_cart()
            elif choice == '3':
                self.view_orders()
            elif choice == '4':
                self.auth.logout()
                break
            else:
                print("Invalid choice. Please try again.")
    
    def search_products(self):
        """Search for products with keywords (AND semantics)"""
        print("\n=== SEARCH PRODUCTS ===")
        keywords = input("Enter search keywords (space-separated): ").strip()
        
        if not keywords:
            print("No keywords provided.")
            return
        
        # Record search in database
        ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        query = "INSERT INTO search (cid, sessionNo, ts, query) VALUES (?, ?, ?, ?)"
        self.db.execute_update(query, (self.auth.current_user, self.auth.session_no, ts, keywords))
        
        # Split keywords and build query with AND semantics
        keyword_list = keywords.lower().split()
        conditions = []
        params = []
        
        for keyword in keyword_list:
            conditions.append("(LOWER(name) LIKE ? OR LOWER(descr) LIKE ?)")
            params.extend([f'%{keyword}%', f'%{keyword}%'])
        
        query = f"SELECT * FROM products WHERE {' AND '.join(conditions)}"
        results = self.db.execute_query(query, tuple(params))
        
        if not results or len(results) == 0:
            print("No products found.")
            return
        
        # Paginate results (5 per page)
        self._paginate_products(results)
    
    def _paginate_products(self, products):
        """Display products with pagination"""
        page = 0
        per_page = 5
        total_pages = (len(products) - 1) // per_page + 1
        
        while True:
            start = page * per_page
            end = min(start + per_page, len(products))
            
            print(f"\n--- Page {page + 1} of {total_pages} ---")
            for i in range(start, end):
                p = products[i]
                print(f"{i + 1}. [{p['pid']}] {p['name']} - ${p['price']:.2f}")
                print(f"   Category: {p['category']} | Stock: {p['stock_count']}")
            
            print("\nOptions: [N]ext, [P]rev, [Select number], [B]ack to menu")
            choice = input("Enter choice: ").strip().lower()
            
            if choice == 'n' and page < total_pages - 1:
                page += 1
            elif choice == 'p' and page > 0:
                page -= 1
            elif choice == 'b':
                break
            elif choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(products):
                    self._view_product_detail(products[idx])
                else:
                    print("Invalid selection.")
            else:
                print("Invalid option.")
    
    def _view_product_detail(self, product):
        """View detailed product information"""
        print("\n=== PRODUCT DETAILS ===")
        print(f"ID: {product['pid']}")
        print(f"Name: {product['name']}")
        print(f"Category: {product['category']}")
        print(f"Price: ${product['price']:.2f}")
        print(f"Stock: {product['stock_count']}")
        print(f"Description: {product['descr']}")
        
        # Record view in viewedProduct table
        ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        query = "INSERT INTO viewedProduct (cid, sessionNo, ts, pid) VALUES (?, ?, ?, ?)"
        self.db.execute_update(query, (self.auth.current_user, self.auth.session_no, ts, product['pid']))
        
        # Option to add to cart
        if product['stock_count'] > 0:
            add = input("\nAdd to cart? (y/n): ").strip().lower()
            if add == 'y':
                self._add_to_cart(product['pid'])
        else:
            print("\nProduct out of stock.")
    
    def _add_to_cart(self, pid):
        """Add product to cart"""
        # Check if product already in cart
        query = "SELECT qty FROM cart WHERE cid = ? AND sessionNo = ? AND pid = ?"
        result = self.db.execute_query(query, (self.auth.current_user, self.auth.session_no, pid))
        
        if result and len(result) > 0:
            # Update quantity
            new_qty = result[0]['qty'] + 1
            query = "UPDATE cart SET qty = ? WHERE cid = ? AND sessionNo = ? AND pid = ?"
            self.db.execute_update(query, (new_qty, self.auth.current_user, self.auth.session_no, pid))
        else:
            # Insert new cart item
            query = "INSERT INTO cart (cid, sessionNo, pid, qty) VALUES (?, ?, ?, ?)"
            self.db.execute_update(query, (self.auth.current_user, self.auth.session_no, pid, 1))
        
        print("Product added to cart!")
    
    def view_cart(self):
        """View and manage shopping cart"""
        print("\n=== SHOPPING CART ===")
        
        query = """
            SELECT c.pid, p.name, p.price, p.stock_count, c.qty
            FROM cart c
            JOIN products p ON c.pid = p.pid
            WHERE c.cid = ? AND c.sessionNo = ?
        """
        cart_items = self.db.execute_query(query, (self.auth.current_user, self.auth.session_no))
        
        if not cart_items or len(cart_items) == 0:
            print("Your cart is empty.")
            return
        
        # Display cart
        total = 0
        for i, item in enumerate(cart_items, 1):
            subtotal = item['price'] * item['qty']
            total += subtotal
            print(f"{i}. {item['name']} - ${item['price']:.2f} x {item['qty']} = ${subtotal:.2f}")
            print(f"   (Stock available: {item['stock_count']})")
        
        print(f"\nTotal: ${total:.2f}")
        
        # Cart management options
        print("\nOptions: [U]pdate, [R]emove, [C]heckout, [B]ack")
        choice = input("Enter choice: ").strip().lower()
        
        if choice == 'u':
            self._update_cart_item(cart_items)
        elif choice == 'r':
            self._remove_cart_item(cart_items)
        elif choice == 'c':
            self._checkout(cart_items)
        elif choice == 'b':
            return
    
    def _update_cart_item(self, cart_items):
        """Update quantity of cart item"""
        try:
            idx = int(input("Enter item number to update: ")) - 1
            if 0 <= idx < len(cart_items):
                item = cart_items[idx]
                new_qty = int(input(f"Enter new quantity (max {item['stock_count']}): "))
                
                if new_qty <= 0:
                    print("Quantity must be positive.")
                elif new_qty > item['stock_count']:
                    print(f"Insufficient stock. Available: {item['stock_count']}")
                else:
                    query = "UPDATE cart SET qty = ? WHERE cid = ? AND sessionNo = ? AND pid = ?"
                    self.db.execute_update(query, (new_qty, self.auth.current_user, self.auth.session_no, item['pid']))
                    print("Cart updated successfully!")
            else:
                print("Invalid item number.")
        except ValueError:
            print("Invalid input.")
    
    def _remove_cart_item(self, cart_items):
        """Remove item from cart"""
        try:
            idx = int(input("Enter item number to remove: ")) - 1
            if 0 <= idx < len(cart_items):
                item = cart_items[idx]
                query = "DELETE FROM cart WHERE cid = ? AND sessionNo = ? AND pid = ?"
                self.db.execute_update(query, (self.auth.current_user, self.auth.session_no, item['pid']))
                print("Item removed from cart!")
            else:
                print("Invalid item number.")
        except ValueError:
            print("Invalid input.")
    
    def _checkout(self, cart_items):
        """Process checkout"""
        print("\n=== CHECKOUT ===")
        
        # Calculate total
        total = sum(item['price'] * item['qty'] for item in cart_items)
        print(f"Order total: ${total:.2f}")
        
        # Get shipping address
        address = input("Enter shipping address: ").strip()
        
        # Confirm order
        confirm = input("Confirm order? (y/n): ").strip().lower()
        if confirm != 'y':
            print("Order cancelled.")
            return
        
        # Create order
        ono = self.db.get_next_id('orders', 'ono')
        odate = datetime.now().strftime('%Y-%m-%d')
        
        query = "INSERT INTO orders (ono, cid, sessionNo, odate, shipping_address) VALUES (?, ?, ?, ?, ?)"
        if not self.db.execute_update(query, (ono, self.auth.current_user, self.auth.session_no, odate, address)):
            print("Error creating order.")
            return
        
        # Create order lines
        line_no = 1
        for item in cart_items:
            query = "INSERT INTO orderlines (ono, lineNo, pid, qty, uprice) VALUES (?, ?, ?, ?, ?)"
            self.db.execute_update(query, (ono, line_no, item['pid'], item['qty'], item['price']))
            line_no += 1
            
            # Update stock
            query = "UPDATE products SET stock_count = stock_count - ? WHERE pid = ?"
            self.db.execute_update(query, (item['qty'], item['pid']))
        
        # Clear cart
        query = "DELETE FROM cart WHERE cid = ? AND sessionNo = ?"
        self.db.execute_update(query, (self.auth.current_user, self.auth.session_no))
        
        print(f"\nOrder placed successfully! Order number: {ono}")
    
    def view_orders(self):
        """View past orders"""
        print("\n=== MY ORDERS ===")
        
        query = """
            SELECT o.ono, o.odate, o.shipping_address,
                   SUM(ol.qty * ol.uprice) as total
            FROM orders o
            JOIN orderlines ol ON o.ono = ol.ono
            WHERE o.cid = ?
            GROUP BY o.ono
            ORDER BY o.odate DESC
        """
        orders = self.db.execute_query(query, (self.auth.current_user,))
        
        if not orders or len(orders) == 0:
            print("No orders found.")
            return
        
        # Paginate orders
        self._paginate_orders(orders)
    
    def _paginate_orders(self, orders):
        """Display orders with pagination"""
        page = 0
        per_page = 5
        total_pages = (len(orders) - 1) // per_page + 1
        
        while True:
            start = page * per_page
            end = min(start + per_page, len(orders))
            
            print(f"\n--- Page {page + 1} of {total_pages} ---")
            for i in range(start, end):
                o = orders[i]
                print(f"{i + 1}. Order #{o['ono']} - {o['odate']}")
                print(f"   Address: {o['shipping_address']}")
                print(f"   Total: ${o['total']:.2f}")
            
            print("\nOptions: [N]ext, [P]rev, [Select number], [B]ack to menu")
            choice = input("Enter choice: ").strip().lower()
            
            if choice == 'n' and page < total_pages - 1:
                page += 1
            elif choice == 'p' and page > 0:
                page -= 1
            elif choice == 'b':
                break
            elif choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(orders):
                    self._view_order_detail(orders[idx]['ono'])
                else:
                    print("Invalid selection.")
            else:
                print("Invalid option.")
    
    def _view_order_detail(self, ono):
        """View detailed order information"""
        # Get order header
        query = "SELECT ono, odate, shipping_address FROM orders WHERE ono = ?"
        order = self.db.execute_query(query, (ono,))[0]
        
        print("\n=== ORDER DETAILS ===")
        print(f"Order Number: {order['ono']}")
        print(f"Order Date: {order['odate']}")
        print(f"Shipping Address: {order['shipping_address']}")
        print("\n--- Order Items ---")
        
        # Get order lines
        query = """
            SELECT p.name, p.category, ol.qty, ol.uprice,
                   (ol.qty * ol.uprice) as line_total
            FROM orderlines ol
            JOIN products p ON ol.pid = p.pid
            WHERE ol.ono = ?
        """
        lines = self.db.execute_query(query, (ono,))
        
        total = 0
        for line in lines:
            print(f"- {line['name']} ({line['category']})")
            print(f"  Qty: {line['qty']} x ${line['uprice']:.2f} = ${line['line_total']:.2f}")
            total += line['line_total']
        
        print(f"\n--- Grand Total: ${total:.2f} ---")
        input("\nPress Enter to continue...")
