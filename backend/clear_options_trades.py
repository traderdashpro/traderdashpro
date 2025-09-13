#!/usr/bin/env python3
"""
Simple script to clear options_trades table
"""

import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database connection parameters
DB_HOST = 'localhost'
DB_PORT = '5432'
DB_NAME = 'trading_dashboard'
DB_USER = 'postgres'
DB_PASSWORD = 'admin12#'

def clear_options_trades():
    """Clear all options trades from the database"""
    try:
        # Connect to database
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        
        cursor = conn.cursor()
        
        # Check if options_trades table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'options_trades'
            )
        """)
        
        exists = cursor.fetchone()[0]
        print(f"options_trades table exists: {exists}")
        
        if exists:
            # Get count of options trades
            cursor.execute("SELECT COUNT(*) FROM options_trades")
            count = cursor.fetchone()[0]
            print(f"Found {count} options trades")
            
            if count > 0:
                # Delete all options trades
                cursor.execute("DELETE FROM options_trades")
                conn.commit()
                print("✅ All options trades deleted")
            else:
                print("ℹ️  No options trades to delete")
        else:
            print("ℹ️  No options_trades table found")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    clear_options_trades()
