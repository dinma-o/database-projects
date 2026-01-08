#!/bin/bash

echo "=========================================="
echo "  Quick E-Commerce System Test"
echo "=========================================="

# 1. Setup fresh database
echo -e "\n[1/4] Setting up test database..."
rm -f prj-test.db
sqlite3 prj-test.db < prj-tables.sql

# 2. Populate with test data
echo "[2/4] Populating test data..."
python3 insert_products_fixed.py

# 3. Run automated tests
echo -e "\n[3/4] Running automated tests..."
python3 test_app.py

# 4. Summary
echo -e "\n[4/4] Test complete!"
echo "Database: prj-test.db is ready for manual testing"
echo "Run: python3 main.py prj-test.db"