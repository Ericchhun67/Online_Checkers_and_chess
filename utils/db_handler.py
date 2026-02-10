""" 
db_handler.py monitors and manages database connections for the Chess and Checkers 
web application. It initializes the SQLAlchemy instance and provides utility
functions for connecting to and disconnecting from the database.
This file is imported by app.py to set up the database for the application.

Linked files:
    - config.py -> Loads app configuration settings ( DB, URI, SECRET_KEY)
    - monels/user_model.py -> Defines User model for authentication
    - models/game_model.py    → Game table model
    - models/ranking_model.py → Ranking/Leaderboard table model
"""

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError



db = SQLAlchemy()




def init_db(app):
    """ Initialize and this create all database tables """
    db.init_app(app)
    with app.app_context():
        try:
            db.create_all()
            print("Database tables created successfully.")
        except SQLAlchemyError as e:
            print(f"Error creating database tables: {e}")



def add_record(record):
    """ 
        Add a record to the database session and commit the transaction.
        Args:
            record: An instance of a SQLAlchemy model to be added to the database.
        Returns:
            bool: True if the record was added successfully, False otherwise.
    
    """
    # handle exceptions to check if the record was added successfully
    try:
        # add record from the database session and commit the transaction
        db.session.add(record)
        db.session.commit() 
        # print success message that the record was added
        print(f"Record {record} added successfully.")
        # then return True
        return True
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Error adding record {e}")
        return False


def update_record():
    """Commit all staged updates to the database."""
    try:
        db.session.commit()
        print("[DB] Record(s) updated successfully.")
        return True
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"[DB ERROR] {e}")
        return False


def get_all(model):
    """Retrieve all records for a given model (e.g., User, Game)."""
    try:
        records = model.query.all()
        print(f"[DB] Retrieved {len(records)} records from {model.__tablename__}")
        return records
    except SQLAlchemyError as e:
        print(f"[ DB ERROR] {e}")
        return []


def get_by_id(model, record_id):
    """Retrieve a record by ID."""
    try:
        record = model.query.get(record_id)
        if record:
            print(f"[DB] Found record {record_id} in {model.__tablename__}")
        else:
            print(f"[DB] No record with ID {record_id} found in {model.__tablename__}")
        return record
    except SQLAlchemyError as e:
        print(f"[ DB ERROR] {e}")
        return None
        
def close_db(e=None):
    """Safely close the database session."""
    try:
        db.session.remove()
        print("[DB] Session closed successfully.")
    except SQLAlchemyError as e:
        print(f"[DB ERROR] Failed to close session: {e}")
            
        