#!/usr/bin/env python3
"""
Migration runner script for deployment
"""
import os
import sys
from flask import Flask
from flask_migrate import upgrade
from app import app, db

def run_migrations():
    """Run database migrations"""
    try:
        print("Running database migrations...")
        with app.app_context():
            upgrade()
        print("Migrations completed successfully!")
        return True
    except Exception as e:
        print(f"Migration failed: {e}")
        return False

if __name__ == "__main__":
    success = run_migrations()
    sys.exit(0 if success else 1) 