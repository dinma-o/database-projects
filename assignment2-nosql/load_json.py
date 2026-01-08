#!/usr/bin/env python3
"""
CMPUT 291 - Mini Project 2
load-json.py - MongoDB Data Loader

This program loads JSON data from a file into MongoDB using batch insertion.
Usage: python load-json.py <json_file> <port>

Authors: Chidinma Obi-Okoye (obiokoye)
Date: November 2025
"""

import sys
import json
import os
import time
from pymongo import MongoClient


def parse_arguments():
    """
    Parse and validate command-line arguments
    Returns: (json_file, port)
    """
    # Check argument count
    if len(sys.argv) != 3:
        print("Usage: python load-json.py <json_file> <port>")
        print("Example: python load-json.py articles.json 27017")
        sys.exit(1)

    json_file = sys.argv[1]
    port_str = sys.argv[2]

    # Validate file exists
    if not os.path.exists(json_file):
        print(f"Error: File '{json_file}' not found")
        sys.exit(1)

    # Validate port is a number
    try:
        port = int(port_str)
        if port < 1024 or port > 65535:
            print("Error: Port must be between 1024 and 65535")
            sys.exit(1)
    except ValueError:
        print(f"Error: Port must be a number, got '{port_str}'")
        sys.exit(1)

    return json_file, port


def connect_to_mongodb(port):
    """
    Connect to MongoDB server on specified port

    Args:
        port (int): MongoDB port number

    Returns:
        MongoClient: Connected MongoDB client

    Raises:
        SystemExit: If connection fails
    """
    try:
        print(f"Connecting to MongoDB on port {port}...")

        # Create client with timeout
        client = MongoClient(
            f"mongodb://localhost:{port}/",
            serverSelectionTimeoutMS=5000,  # 5 second timeout
        )

        # Test connection by getting server info
        client.server_info()

        print("✓ Connected successfully")
        return client

    except Exception as e:
        print(f"✗ Error connecting to MongoDB: {e}")
        print("\nTroubleshooting:")
        print("1. Ensure MongoDB is running:")
        print(f"   mongod --dbpath ~/mongodb_data --port {port} &")
        print("2. Check if port is already in use:")
        print(f"   lsof -i :{port}")
        sys.exit(1)


def setup_database(client):
    """
    Create/access 291db database and setup articles collection

    Args:
        client (MongoClient): Connected MongoDB client

    Returns:
        Collection: MongoDB collection object
    """
    print("\nSetting up database and collection...")

    # Access (or create) database
    db = client["291db"]

    # Drop existing collection if it exists
    if "articles" in db.list_collection_names():
        db.articles.drop()
        print("✓ Dropped existing 'articles' collection")

    # Create new collection (happens automatically on first insert)
    collection = db["articles"]
    print("✓ Created new 'articles' collection")

    return collection


def read_json_in_batches(filename, batch_size=5000):
    """
    Generator that yields batches of documents from JSON file

    This function reads the file line-by-line to handle files
    larger than available memory.

    Args:
        filename (str): Path to JSON file
        batch_size (int): Number of documents per batch

    Yields:
        list: Batch of document dictionaries
    """
    batch = []
    line_num = 0
    errors = 0

    with open(filename, "r", encoding="utf-8") as file:
        for line in file:
            line_num += 1

            clean_line = line.strip()
            # Skip empty lines, start brackets, or end brackets
            if not clean_line or clean_line in ["[", "]"]:
                continue

            # Remove trailing comma if it exists (common in JSON arrays)
            if clean_line.endswith(","):
                clean_line = clean_line[:-1]

            try:
                # Parse JSON from this line
                document = json.loads(clean_line)
                batch.append(document)

                # Yield batch when it reaches size limit
                if len(batch) >= batch_size:
                    yield batch
                    batch = []

            except json.JSONDecodeError as e:
                errors += 1
                print(f"Warning: Skipping invalid JSON on line {line_num}: {e}")
                # Continue processing instead of failing
                continue

            except Exception as e:
                errors += 1
                print(f"Warning: Error on line {line_num}: {e}")
                continue

        # Yield any remaining documents
        if batch:
            yield batch

        if errors > 0:
            print(f"\n⚠ Warning: Skipped {errors} invalid lines")


def insert_batches(collection, json_file, batch_size=5000):
    """
    Insert documents in batches from JSON file

    Args:
        collection (Collection): MongoDB collection
        json_file (str): Path to JSON file
        batch_size (int): Documents per batch

    Returns:
        int: Total number of documents inserted
    """
    total_inserted = 0
    batch_count = 0
    start_time = time.time()

    print(f"\nLoading data from {json_file}...")
    print(f"Batch size: {batch_size} documents")
    print("-" * 50)

    for batch in read_json_in_batches(json_file, batch_size):
        try:
            # Insert batch into MongoDB
            # ordered=False continues even if some documents fail
            result = collection.insert_many(batch, ordered=False)

            inserted = len(result.inserted_ids)
            total_inserted += inserted
            batch_count += 1

            # Progress indicator
            elapsed = time.time() - start_time
            rate = total_inserted / elapsed if elapsed > 0 else 0

            print(
                f"Batch {batch_count:3d}: {inserted:5d} docs "
                f"(Total: {total_inserted:7d}, "
                f"Rate: {rate:6.0f} docs/sec)"
            )

        except Exception as e:
            print(f"✗ Error inserting batch {batch_count}: {e}")
            # Continue with next batch instead of failing completely
            continue

    return total_inserted


def create_indexes(collection):
    """
    Create indexes to optimize Phase 2 queries
    """
    print("\nCreating indexes for Phase 2 optimization...")
    start_idx = time.time()

    # 1. For Query 1 (Media Type) & Query 2 (Article Diff)
    # Allows fast counting by media type and date range
    collection.create_index([("media-type", 1)])
    collection.create_index([("published", 1)])

    # 2. For Query 3 (Top Sources)
    collection.create_index([("source", 1)])

    # 3. For Query 4 (Recent Articles by Source)
    # Compound index allows finding a source AND sorting by date instantly
    collection.create_index([("source", 1), ("published", -1)])

    elapsed = time.time() - start_idx
    print(f"✓ Indexes created in {elapsed:.2f} seconds")


def main():
    """Main program execution"""
    print("=" * 60)
    print("  CMPUT 291 - MongoDB Data Loader")
    print("=" * 60)

    # Parse arguments
    json_file, port = parse_arguments()

    # Connect to MongoDB
    client = connect_to_mongodb(port)

    # Setup database and collection
    collection = setup_database(client)

    # Record start time
    start_time = time.time()

    # Load data in batches
    total = insert_batches(collection, json_file, batch_size=5000)

    # Create Indexes (CRITICAL FOR PHASE 2)
    create_indexes(collection)

    # Calculate and display summary
    elapsed = time.time() - start_time

    print("\n" + "=" * 60)
    print("  LOAD COMPLETE")
    print("=" * 60)
    print(f"Total documents inserted: {total:,}")
    print(f"Time taken: {elapsed:.2f} seconds ({elapsed/60:.2f} minutes)")
    print(f"Average rate: {total/elapsed:.0f} documents/second")
    print("=" * 60)

    # Clean up
    client.close()

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
