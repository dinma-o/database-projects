#!/usr/bin/env python3
import sqlite3

conn = sqlite3.connect('prj-test.db')
cursor = conn.cursor()

# Clear existing products first (optional)
print("Clearing existing products...")
cursor.execute("DELETE FROM products")
conn.commit()

print("Inserting products...")

products = [
    (1, 'Luxury Hand Soap', 'Bath & Body', 5.99, 100, 'Premium hand soap with moisturizing cream'),
    (2, 'Face Cream Moisturizer', 'Beauty', 24.99, 50, 'Anti-aging face cream for all skin types'),
    (3, 'Organic Food Basket', 'Groceries', 49.99, 25, 'Fresh organic food items delivered daily'),
    (4, 'Gift Cards Pack', 'Gift Items', 50.00, 200, 'Assorted gift cards for various stores'),
    (5, 'Credit Card Holder', 'Accessories', 15.99, 75, 'Leather wallet for cards and cash'),
    (6, 'Playing Cards Set', 'Games', 8.99, 150, 'Professional quality playing cards deck'),
    (7, 'Greeting Cards Bundle', 'Stationery', 12.99, 100, 'Assorted greeting cards for all occasions'),
    (8, 'Body Cream Lotion', 'Bath & Body', 18.99, 60, 'Nourishing body cream with natural ingredients'),
    (9, 'Shaving Cream', 'Men Grooming', 9.99, 80, 'Smooth shaving cream for sensitive skin'),
    (10, 'Ice Cream Maker', 'Appliances', 79.99, 15, 'Make homemade ice cream and frozen treats'),
    (11, 'Dish Soap', 'Cleaning', 3.99, 200, 'Effective dish soap that cuts through grease'),
    (12, 'Sunscreen Cream', 'Health', 16.99, 45, 'SPF 50 sunscreen cream for outdoor protection'),
    (13, 'Pet Food Premium', 'Pet Supplies', 34.99, 40, 'High-quality pet food with natural ingredients'),
    (14, 'Business Cards Box', 'Office', 19.99, 90, 'Professional business cards printing service'),
    (15, 'Baby Cream', 'Baby Care', 12.99, 70, 'Gentle baby cream for sensitive skin')
]

for p in products:
    cursor.execute(
        'INSERT INTO products (pid, name, category, price, stock_count, descr) VALUES (?, ?, ?, ?, ?, ?)',
        p
    )
    print(f"  ✓ {p[1]}")

# THIS IS CRITICAL - COMMIT THE TRANSACTION
conn.commit()
print(f"\n✓ Committed {len(products)} products to database")

# Verify
cursor.execute("SELECT COUNT(*) FROM products")
count = cursor.fetchone()[0]
print(f"✓ Verification: {count} products now in database")

# Show samples
cursor.execute("SELECT pid, name FROM products LIMIT 5")
print("\nFirst 5 products:")
for row in cursor.fetchall():
    print(f"  [{row[0]}] {row[1]}")

# Add salesperson
cursor.execute("DELETE FROM users WHERE uid = 100")
cursor.execute("INSERT INTO users (uid, pwd, role) VALUES (100, 'sales123', 'sales')")
conn.commit()
print("\n✓ Added salesperson (ID: 100, Password: sales123)")

conn.close()
print("\n✓ Database closed. Ready to use!")