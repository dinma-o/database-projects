[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/THJ5OpUp)

# CMPUT 291 Project 2 - Fall 2025

Group member names and ccids (2-3 members)  
 obiokoye, Chidinma Obi-Okoye <br>
diepreye, Diepreye Charles-Daniel<br>
akpulonu, Ugonna Noble Jr Akpulonu

## REQUIREMENTS

### Software

- Python 3.8 or higher
- MongoDB 4.4 or higher
- pymongo Python package

## INSTALLATION

### 1. Project Setup (Lab Machines & macOS/Linux)

```bash
# 1. Create project directory
mkdir ~/cmput291_project2
cd ~/cmput291_project2

# 2. Create virtual environment
python3 -m venv venv

# 3. Activate virtual environment
source venv/bin/activate

# 4. Install dependencies
pip install pymongo

# 5. Verify installation
python -c "import pymongo; print(f'pymongo version: {pymongo.__version__}')"
```

---

## INSTRUCTIONS

### Phase 1: Data Loading

This step builds the MongoDB database and **automatically creates the required indexes** for performance.

#### 1\. Start MongoDB Server

```bash
# Create data directory (if not exists)
mkdir -p ~/mongodb_data

# Start MongoDB on a specific port (e.g., 27017)
mongod --dbpath ~/mongodb_data --port 27017 &

# Verify it's running
ps aux | grep mongod
```

#### 2\. Run the Loader

The `load-json.py` script accepts the input JSON file and the port number.

```bash
# Usage: python load-json.py <filename> <port>
python load-json.py articles.json 27017
```

**Expected Output:**

```text
============================================================
  CMPUT 291 - MongoDB Data Loader
============================================================
Connecting to MongoDB on port 27017...
✓ Connected successfully

Setting up database and collection...
✓ Dropped existing 'articles' collection
✓ Created new 'articles' collection

Loading data from articles.json...
Batch size: 5000 documents
--------------------------------------------------
Batch   1:  5000 docs (Total:    5000, Rate:   2500 docs/sec)
...
Creating indexes for Phase 2 optimization...
✓ Indexes created in 0.45 seconds
============================================================
  LOAD COMPLETE
============================================================
```

### Phase 2: Operating on the Document Store

Once the data is loaded, run the query program to search the database.

```bash
# Usage: python phase2_query.py <port>
python phase2_query.py 27017
```

**Supported Operations:**

1.  **Search by Media Type:** Finds top 5 most common alphanumeric words (excluding stopwords/punctuation per Nov 21 spec).
2.  **Article Count Difference:** Compares News vs. Blog counts for a specific date (handles various date formats).
3.  **Top News Sources:** Lists the top 5 news sources for 2015.
4.  **Recent Articles:** Fetches the 5 most recent articles for a specific source.

---

## GROUP INFORMATION

We confirm that all group members have contributed to this project.

## COLLABORATION

We did not collaborate with anyone outside of our group for this project.

## SOURCES OF INFORMATION

- CMPUT 291 Course Lecture Notes
- MongoDB Official Documentation ([https://www.mongodb.com/docs/](https://www.mongodb.com/docs/))
- PyMongo Documentation ([https://pymongo.readthedocs.io/](https://pymongo.readthedocs.io/))
