#!/usr/bin/env python3
"""
CMPUT 291 - Mini Project 2
phase2_query.py - MongoDB Query Program for News Articles Database

Connects to 291db database and provides menu-driven interface for queries
Usage: python phase2_query.py <port_number>

Authors: Ugonna Noble Jr Akpulonu (akpulonu), Diepreye Charles-Daniel (diepreye)
Date: November 2025
"""

import re
import sys
from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError


def connect_to_mongodb(port):
    """
    Connect to MongoDB server on specified port

    Args:
        port: Port number where MongoDB is running

    Returns:
        Database object if successful, None otherwise
    """
    try:
        client = MongoClient(
            f"mongodb://localhost:{port}/", serverSelectionTimeoutMS=5000
        )
        # Test connection
        client.admin.command("ping")
        db = client["291db"]
        print(f"Successfully connected to MongoDB on port {port}")
        print(f"Database: 291db\n")
        return db
    except ConnectionFailure:
        print(f"Error: Could not connect to MongoDB on port {port}")
        return None
    except ServerSelectionTimeoutError:
        print(f"Error: MongoDB server not available on port {port}")
        return None
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        return None


def display_menu():
    """Display the main menu options"""
    print("=" * 60)
    print("MONGODB NEWS ARTICLES QUERY SYSTEM")
    print("=" * 60)
    print("1. Query Option 1")
    print("2. Query Option 2")
    print("3. Query Option 3")
    print("4. Query Option 4")
    print("5. Exit")
    print("=" * 60)


"""
Example:

id: "f7ca322d-c3e8-40d2-841f-9d7250ac72ca"
content: "VETERANS saluted Worcester's first ever breakfast club for ex-soldiers…"
title: "Worcester breakfast club for veterans gives hunger its marching orders"
media-type: "News"
source: "Redditch Advertiser"
published: "2015-09-07T10:16:14Z"
"""


def query_option_1(db):
    """
    Query 1: Most Common Words by Media Type
    Finds the top 5 most common words in articles of specified media type

    Args:
        db: MongoDB database object
    """
    print("\n" + "=" * 60)
    print("QUERY 1: MOST COMMON WORDS BY MEDIA TYPE")
    print("=" * 60)

    # Get media type from user
    while True:
        media_type = input("\nEnter media type (News/Blog): ").strip()
        if media_type.lower() in ["news", "blog"]:
            media_type = media_type.capitalize()
            break
        else:
            print("Error: Please enter 'News' or 'Blog'")

    print(f"\nAnalyzing word frequencies for media type: {media_type}")
    print("Please wait...\n")

    # Aggregation pipeline to find top 5 words
    try:
        # MongoDB aggregation pipeline
        pipeline = [
            # Match documents with specified media type
            {"$match": {"media-type": media_type}},
            # Project to split content into words
            {
                "$project": {
                    "words": {
                        "$split": [{"$toLower":"$content"}, " "]
                    }
                }
            },
            # Unwind the words array
            {"$unwind": "$words"},
            # Filter out empty strings and keep clean words
            {"$project": {"word": {"$trim": {"input": "$words"}}}},
            # Match all non-empty words
            {"$match": {
                "word": {
                    "$ne": "",
                    "$regex": r'^[a-zA-Z0-9_\-]+$'
                    }
                }
            },
            # Group by word and count
            {"$group": {"_id": "$word", "count": {"$sum": 1}}},
            # Sort by count descending
            {"$sort": {"count": -1}},
        ]

        # Execute aggregation
        all_results = list(db.articles.aggregate(pipeline))
        results = []
        if all_results:
            # Get at least 5 results
            results = all_results[:5]

            # If we have at least 5 results, check for ties at 5th position
            if len(all_results) >= 5:
                fifth_count = all_results[4]["count"]

                # Add all words tied with the 5th position
                for i in range(5, len(all_results)):
                    if all_results[i]["count"] == fifth_count:
                        results.append(all_results[i])
                    else:
                        break  # Stop when we hit a lower count

        # Display results
        if results:
            print(f"Top 5 Most Common Words in {media_type} Articles:")
            print("-" * 60)
            print(f"{'Rank':<6} {'Word':<30} {'Frequency':<15}")
            print("-" * 60)

            for idx, result in enumerate(results, 1):
                word = result["_id"]
                count = result["count"]
                print(f"{idx:<6} {word:<30} {count:<15,}")

            print("-" * 60)
        else:
            print(f"No results found for media type: {media_type}")

    except Exception as e:
        print(f"Error executing query: {e}")

    input("\nPress Enter to continue...")


def query_option_2(db):
    """
    Query 2: Article Count Difference by Date
    Compares news vs blog article counts for a specific date

    Args:
        db: MongoDB database object
    """

    print("\n" + "=" * 60)
    print("QUERY 2: ARTICLE COUNT DIFFERENCE BY DATE")
    print("=" * 60)

    # Get date from user
    date_str = input(
        "\nEnter a date (e.g., 'September 1, 2015' or '2015-09-01'): "
    ).strip()

    # Parse date with multiple format support
    date_obj = None
    date_formats = [
        "%B %d, %Y",  # September 1, 2015
        "%b %d, %Y",  # Sep 1, 2015
        "%Y-%m-%d",  # 2015-09-01
        "%m/%d/%Y",  # 09/01/2015
        "%d/%m/%Y",  # 01/09/2015
        "%Y/%m/%d",  # 2015/09/01
        "%B %d %Y",  # September 1 2015
        "%b %d %Y",  # Sep 1 2015
    ]

    for fmt in date_formats:
        try:
            date_obj = datetime.strptime(date_str, fmt)
            break
        except ValueError:
            continue

    if date_obj is None:
        print(f"\nError: Could not parse date '{date_str}'")
        print(
            "Please use formats like 'September 1, 2015' or '2015-09-01' and ensure it's a valid date."
        )
        input("\nPress Enter to continue...")
        return

    print(f"\nAnalyzing articles published on: {date_obj.strftime('%B %d, %Y')}")
    print("Please wait...\n")

    try:
        # Create date range for the entire day
        start_of_day = datetime(date_obj.year, date_obj.month, date_obj.day, 0, 0, 0)
        end_of_day = datetime(date_obj.year, date_obj.month, date_obj.day, 23, 59, 59)

        # Convert to ISO format strings for MongoDB query
        start_iso = start_of_day.strftime("%Y-%m-%dT%H:%M:%S") + "Z"
        end_iso = end_of_day.strftime("%Y-%m-%dT%H:%M:%S") + "Z"

        # Count News articles
        news_count = db.articles.count_documents(
            {"media-type": "News", "published": {"$gte": start_iso, "$lte": end_iso}}
        )

        # Count Blog articles
        blog_count = db.articles.count_documents(
            {"media-type": "Blog", "published": {"$gte": start_iso, "$lte": end_iso}}
        )

        total_count = news_count + blog_count

        # Display results
        print("-" * 60)
        print(f"Date: {date_obj.strftime('%B %d, %Y')}")
        print("-" * 60)

        if total_count == 0:
            print("No articles were published on this day.")
        else:
            print(f"News articles: {news_count:,}")
            print(f"Blog articles: {blog_count:,}")
            print("-" * 60)

            # Calculate and display difference
            if news_count > blog_count:
                difference = news_count - blog_count
                print(f"News had {difference:,} more article(s) than Blog")
            elif blog_count > news_count:
                difference = blog_count - news_count
                print(f"Blog had {difference:,} more article(s) than News")
            else:
                print("News and Blog had the same number of articles")

        print("-" * 60)

    except Exception as e:
        print(f"Error executing query: {e}")

    input("\nPress Enter to continue...")


def query_option_3(db):
    """
    Top 5 News Sources by Article Count (2015)
    The user should be able to see the top 5 news sources that published the most articles during the year 2015.
    The output should include the number of articles and the name of news source.

    Args:
            db: MongoDB database object
    """

    print("\n" + "=" * 60)
    print("QUERY 3: TOP 5 NEWS SOURCES BY ARTICLE COUNT (2015)")
    print("=" * 60)

    try:
        # Aggregation pipeline to find top 5 news sources in 2015
        pipeline = [
            # Match documents published in 2015
            {
                "$match": {
                    "published": {
                        "$gte": "2015-01-01T00:00:00Z",
                        "$lt": "2016-01-01T00:00:00Z",
                    },
                    "media-type": "News",
                }
            },
            # Group by source and count articles
            {"$group": {"_id": "$source", "article_count": {"$sum": 1}}},
            # Sort by article count descending
            {"$sort": {"article_count": -1}},
            # Instead of limiting to 5 here, we will handle ties later in the code
        ]

        # Execute aggregation
        results = list(db.articles.aggregate(pipeline))

        # Handle ties for the 5th position
        top_results = []

        if results:
            # Get at least 5 results
            top_results = results[:5]

            # If we have at least 5 results, check for ties at 5th position
            if len(results) >= 5:
                fifth_count = results[4]["article_count"]

                # Add all sources tied with the 5th position
                for i in range(5, len(results)):
                    if results[i]["article_count"] == fifth_count:
                        top_results.append(results[i])
                    else:
                        break  # Stop when we hit a lower count

        # Display results
        if top_results:
            print(f"Top 5 News Sources in 2015:")
            print("-" * 60)
            print(f"{'Rank':<6} {'News Source':<40} {'Article Count':<15}")
            print("-" * 60)

            for idx, result in enumerate(top_results, 1):
                source = result["_id"]
                count = result["article_count"]
                print(f"{idx:<6} {source:<40} {count:<15,}")

            print("-" * 60)
        else:
            print("No articles found for the year 2015.")

    except Exception as e:
        print(f"Error executing query: {e}")

    input("\nPress Enter to continue...")


def query_option_4(db):
    """
    Query 4: 5 Most Recent Articles by Source
    The user should be able to input a news source name and see the 5 most recent
    articles from that source. The output should include the article title and
    published date.

    Args:
        db: MongoDB database object
    """
    print("\n" + "=" * 60)
    print("QUERY 4: 5 MOST RECENT ARTICLES BY SOURCE")
    print("=" * 60)

    # Prompt user for source name
    source_name = input("\nEnter the news source name: ").strip()

    try:
        # Check if source exists (Case Insensitive for better UX)
        # Using regex ^Name$ ensures exact phrase match but case insensitive
        source_count = db.articles.count_documents(
            {"source": {"$regex": f"^{re.escape(source_name)}$", "$options": "i"}}
        )

        if source_count == 0:
            print(f"\nSource '{source_name}' not found.")
            input("\nPress Enter to continue...")
            return

        # Retrieve up to 5 most recent articles
        recent_articles = list(
            db.articles.find(
                {"source": {"$regex": f"^{re.escape(source_name)}$", "$options": "i"}}
            )
            .sort("published", -1)
            .limit(5)
        )

        print(f"\nMost Recent Articles from '{source_name}':")
        print(f"{'Title':<50} {'Published Date':<15}")
        print("-" * 60)

        for article in recent_articles:
            published_date = article["published"][:10]  # Extract YYYY-MM-DD
            title = (
                article["title"][:47] + "..."
                if len(article["title"]) > 50
                else article["title"]
            )
            print(f"{title:<50} {published_date:<15}")

        print("-" * 60)

    except Exception as e:
        print(f"Error executing query: {e}")

    input("\nPress Enter to continue...")


def main():
    """Main program loop"""
    # Check command-line arguments
    if len(sys.argv) != 2:
        print("Usage: python phase2_query.py <port_number>")
        print("Example: python phase2_query.py 27017")
        sys.exit(1)

    # Get port number
    try:
        port = int(sys.argv[1])
        if port < 1 or port > 65535:
            raise ValueError("Port must be between 1 and 65535")
    except ValueError as e:
        print(f"Error: Invalid port number - {e}")
        sys.exit(1)

    # Connect to MongoDB
    db = connect_to_mongodb(port)
    if db is None:
        sys.exit(1)

    # Main program loop
    while True:
        display_menu()

        try:
            choice = input("\nEnter your choice (1-5): ").strip()

            if choice == "1":
                query_option_1(db)
            elif choice == "2":
                query_option_2(db)
            elif choice == "3":
                query_option_3(db)
            elif choice == "4":
                query_option_4(db)
            elif choice == "5":
                print("\nThank you for using the MongoDB Query System!")
                print("Goodbye!\n")
                break
            else:
                print("\nError: Invalid choice. Please enter a number between 1 and 5.")
                input("Press Enter to continue...")

        except KeyboardInterrupt:
            print("\n\nProgram interrupted by user.")
            print("Goodbye!\n")
            break
        except Exception as e:
            print(f"\nAn unexpected error occurred: {e}")
            input("Press Enter to continue...")


if __name__ == "__main__":
    main()
