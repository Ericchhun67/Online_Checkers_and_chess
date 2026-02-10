from utils.db_handler import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


class User(db.Model):
    """
        User model for storing user information in the datebase
    
    """
    __tablename__ = 'users' # table name in the database to store user records
    
    id = db.Column(db.Integer, primary_key=True) # unique user ID
    # username field
    username = db.Column(db.String(50), unique=True, nullable=False) 
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    
    
    # Secure password handling
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username}>"