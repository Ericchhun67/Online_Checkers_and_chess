import os

# Get the absolute path to the project directory
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Configuration class 
    SECRET_KEY = "your-secret-key"
    # Ensure the instance folder always exists
    INSTANCE_DIR = os.path.join(BASE_DIR, "instance")
    os.makedirs(INSTANCE_DIR, exist_ok=True)

    # Use the correct, consistent path for SQLite
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(INSTANCE_DIR, 'app.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False