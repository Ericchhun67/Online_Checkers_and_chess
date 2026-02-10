"""
test_db_handler.py — standalone database test for Chess and Checkers web app.

This script ensures db_handler.py works correctly with the User model.
It:
  1. Initializes Flask + SQLAlchemy
  2. Creates all tables
  3. Adds a sample user
  4. Retrieves all users and prints them

Run:  python -m utils.test_db_handler
"""

from flask import Flask
from utils.db_handler import db, init_db, add_record, get_all
from models.user_model import User
from config import Config


def run_test():
    """Run database test for user creation and retrieval."""
    app = Flask(__name__)
    app.config.from_object(Config)

    with app.app_context():
        print("[TEST] Initializing database...")
        init_db(app)

        # Check if user already exists
        existing_users = User.query.filter_by(email="test@example.com").all()
        if existing_users:
            print("[TEST] User already exists, skipping add.")
        else:
            # Create and add new user
            test_user = User(username="EricTest", email="test@example.com")
            test_user.set_password("123456")
            add_record(test_user)

        # Retrieve all users
        users = get_all(User)
        print(f"[TEST] Total users in DB: {len(users)}")

        # Print user details
        for u in users:
            print(f"  → Username: {u.username} | Email: {u.email}")

        print("[TEST] DB handler test completed successfully.")


if __name__ == "__main__":
    run_test()