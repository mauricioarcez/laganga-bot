import sqlite3
import os

DB_PATH = "state/bot_history.db"

def inspect_db():
    """Shows the contents of the database."""
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get table info
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print(f"Tables in database: {tables}")
    
    # Check posted_deals table
    cursor.execute("SELECT COUNT(*) FROM posted_deals")
    count = cursor.fetchone()[0]
    print(f"\nTotal posted deals: {count}")
    
    if count > 0:
        cursor.execute("SELECT * FROM posted_deals LIMIT 10")
        rows = cursor.fetchall()
        print(f"\nFirst 10 entries:")
        for row in rows:
            print(f"  - ID: {row[0]}, Posted at: {row[1]}")
    
    conn.close()

def clear_db():
    """Clears all posted deals from the database."""
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM posted_deals")
    conn.commit()
    conn.close()
    print("✅ Database cleared successfully!")

if __name__ == "__main__":
    print("=== Database Inspector ===\n")
    inspect_db()
    
    print("\n" + "="*40)
    choice = input("\nDo you want to clear the database? (y/N): ").strip().lower()
    
    if choice == "y":
        clear_db()
        print("\nInspecting after clear:")
        inspect_db()
    else:
        print("Database not cleared.")
