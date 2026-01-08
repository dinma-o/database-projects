# Database Systems Projects

This repository contains a collection of database-driven applications developed as part of a Database Management Systems course. These projects demonstrate proficiency in both Relational (SQL) and Document-oriented (NoSQL) database architectures, as well as high-performance data processing in Python.

## Project 1: E-Commerce Database System (SQLite)
A robust command-line interface (CLI) e-commerce system designed to manage complex relational data and user sessions.

### Features
* **Role-Based Access Control:** Separate interfaces for Customers (searching products, managing carts, and viewing order history) and Salespersons (inventory management and sales analytics).
* **Security:** Implements parameterized queries to prevent SQL injection and uses secure password masking for user authentication.
* **Transactional Integrity:** Features an atomic checkout process that validates stock levels and ensures data consistency across tables.
* **Advanced Reporting:** Automated generation of weekly sales metrics and product performance rankings with tie-handling logic.

### Technologies
* **Language:** Python 3
* **Database:** SQLite3

---

## Project 2: Document Store Analytics Engine (MongoDB)
A high-performance system designed to ingest, index, and analyze large-scale datasets of news and blog articles.

### Features
* **Optimized Data Loader:** A streaming batch processor capable of ingesting large JSON datasets with high efficiency and real-time progress indicators.
* **Complex Aggregations:** An interactive query engine supporting alphanumeric word frequency analysis and article volume comparisons.
* **Performance Tuning:** Automated creation of compound indexes (e.g., source and publication date) to ensure efficient query execution without full collection scans.
* **Robust Text Processing:** Utilizes Regex-based whitelisting to accurately identify words including hyphens and underscores while ignoring punctuation.

### Technologies
* **Language:** Python
* **Database:** MongoDB

---

## Development & Contributions
These projects were developed within a collaborative team environment utilizing Git for version control and architectural planning.

* **Project 1 Focus:** Responsible for the central database handler, authentication modules, session management, and overall SQL security.
* **Project 2 Focus:** Led the development of the high-performance data loader (load-json.py), implemented batch insertion logic, and managed database performance optimization.
