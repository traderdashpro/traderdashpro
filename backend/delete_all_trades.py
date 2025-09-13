#!/usr/bin/env python3
"""
Utility script to delete all trades for a user.
Usage: python delete_all_trades.py <username> <password>
"""

import requests
import sys
import json
from typing import Optional

# Backend URL - adjust if needed
BASE_URL = "http://localhost:5001"
# BASE_URL = "https://api.traderdashpro.com"

def authenticate(username: str, password: str) -> Optional[str]:
    """Authenticate user and return JWT token."""
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": username,
            "password": password
        })
        
        if response.status_code == 200:
            data = response.json()
            return data.get("token")
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")
        return None

def get_all_trades(token: str) -> list:
    """Get all trades for the authenticated user."""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/api/trades/", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            return data.get("trades", [])
        else:
            print(f"❌ Failed to get trades: {response.status_code}")
            print(f"Response: {response.text}")
            return []
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")
        return []

def get_all_positions(token: str) -> list:
    """Get all trades for the authenticated user."""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/api/trades/positions/", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            return data.get("positions", [])
        else:
            print(f"❌ Failed to get positions: {response.status_code}")
            print(f"Response: {response.text}")
            return []
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")
        return []


def delete_trade(token: str, trade_id: str) -> bool:
    """Delete a specific trade."""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        # First, try to clear the position_id reference by updating the trade
        update_data = {"position_id": None}
        update_response = requests.put(f"{BASE_URL}/api/trades/{trade_id}", 
                                     json=update_data, headers=headers)
        
        # Then delete the trade
        response = requests.delete(f"{BASE_URL}/api/trades/{trade_id}", headers=headers)
        
        if response.status_code == 200:
            return True
        else:
            print(f"❌ Failed to delete trade {trade_id}: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")
        return False

def delete_options_trades_direct():
    """Delete all options trades directly via database connection."""
    try:
        from database import db
        from flask import Flask
        from sqlalchemy import text
        
        app = Flask(__name__)
        app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:password@localhost:5432/trading_insights'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        db.init_app(app)
        
        with app.app_context():
            # Check if options_trades table exists
            result = db.session.execute(text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'options_trades')"))
            exists = result.fetchone()[0]
            
            if exists:
                # Get count of options trades
                result = db.session.execute(text('SELECT COUNT(*) FROM options_trades'))
                count = result.fetchone()[0]
                print(f"Found {count} options trades")
                
                if count > 0:
                    # Delete all options trades
                    db.session.execute(text('DELETE FROM options_trades'))
                    db.session.commit()
                    print("✅ All options trades deleted")
                    return True
                else:
                    print("ℹ️  No options trades to delete")
                    return True
            else:
                print("ℹ️  No options_trades table found")
                return True
                
    except Exception as e:
        print(f"❌ Error deleting options trades: {e}")
        return False

def delete_position(token: str, position_id: str) -> bool:
    """Delete a specific position."""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.delete(f"{BASE_URL}/api/trades/positions/{position_id}", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"    ✅ {data.get('message', 'Deleted successfully')}")
                return True
            else:
                print(f"    ❌ API returned error: {data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ Failed to delete position {position_id}: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")
        return False

def main():
    if len(sys.argv) != 3:
        print("Usage: python delete_all_trades.py <username> <password>")
        sys.exit(1)
    
    username = sys.argv[1]
    password = sys.argv[2]
    
    print(f"🔐 Authenticating user: {username}")
    
    # Step 1: Authenticate
    token = authenticate(username, password)
    if not token:
        print("❌ Authentication failed. Exiting.")
        sys.exit(1)
    
    print("✅ Authentication successful!")
    
    # Step 1.5: Delete options trades first (to avoid foreign key constraints)
    print("🗑️  Deleting options trades...")
    if delete_options_trades_direct():
        print("✅ Options trades cleared")
    else:
        print("❌ Failed to clear options trades")
    
    # Step 2: Get all trades
    print("📊 Fetching all trades...")
    trades = get_all_trades(token)
    
    if not trades:
        print("ℹ️  No trades found. Nothing to delete.")
    else:
        print(f"📋 Found {len(trades)} trades to delete")
        
        # Step 3: Delete all trades
        print("🗑️  Deleting trades...")
        deleted_count = 0
        failed_count = 0
        
        for i, trade in enumerate(trades, 1):
            trade_id = trade.get("id")
            symbol = trade.get("ticker_symbol", "Unknown")
            print(f"  [{i}/{len(trades)}] Deleting {symbol} trade ({trade_id})...")
            
            if delete_trade(token, trade_id):
                deleted_count += 1
                print(f"    ✅ Deleted")
            else:
                failed_count += 1
                print(f"    ❌ Failed")
        
        print(f"Trades deleted: {deleted_count}, Failed: {failed_count}")
    

    # Step 4: Get all positions
    print("📊 Fetching all positions...")
    positions = get_all_positions(token)
    
    if not positions:
        print("ℹ️  No positions found. Nothing to delete.")
        sys.exit(0)
    
    print(f"📋 Found {len(positions)} positions to delete")
    
    # Step 5: Delete all positions
    print("🗑️  Deleting positions...")
    deleted_count = 0
    failed_count = 0
    
    for i, position in enumerate(positions, 1):
        position_id = position.get("id")
        symbol = position.get("symbol", "Unknown")
        print(f"  [{i}/{len(positions)}] Deleting {symbol} position ({position_id})...")
        
        if delete_position(token, position_id):
            deleted_count += 1
            print(f"    ✅ Deleted")
        else:
            failed_count += 1
            print(f"    ❌ Failed")
    
    # Summary
    print("\n" + "="*50)
    print("📊 DELETION SUMMARY")
    print("="*50)
    # print(f"Total trades found: {len(trades)}")
    # print(f"Successfully deleted: {deleted_count}")
    # print(f"Failed to delete: {failed_count}")
    print(f"Total positions found: {len(positions)}")
    print(f"Successfully deleted: {deleted_count}")
    print(f"Failed to delete: {failed_count}")
    
    if failed_count == 0:
        print("🎉 All positions deleted successfully!")
    else:
        print(f"⚠️  {failed_count} positions failed to delete")

if __name__ == "__main__":
    main()
