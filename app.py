# 12/10/2025
# Eric Chhun
""" 
    app.py main entry point for Chess and Checkers web app
    
This script initializes the flask application, configures the SQLAlchemy database,
sets up Flask-SocketIO for real-time communication, and registers all routes:
    - authentication
    - lobby
    - game

It also connects to the SQLLite database to verify that the schema loads correctly
for testing and development purposes.

Files linked:
    backend/
    - config.py -> Loads app configuration settings ( DB, URI, SECRET_KEY)
    - utils/db_handlers.py -> Initializes SQLALchemy
    - utils/socket_handlers.py -> Registers SocketIO event handlers
    - routes/auth_routes.py -> User authentication routes
        - login, logout, register
    - routes/lobby_routes.py  → Lobby routes (player match & list)
    - routes/game_routes.py   → Game logic routes
    - templates/*.html        → Frontend pages
    - static/js/*.js          → SocketIO communication & UI scripts
"""



from flask import Flask, render_template
from flask_socketio import SocketIO
from utils.db_handler import db, init_db
from utils.socket_handlers import register_socket_events
from routes.auth_routes import auth_bp
from routes.lobby_routes import lobby_bp
from routes.game_routes import game_bp
from config import Config
import os
import socket

# initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)



# initialize SQLAlchemy and SocketIO
init_db(app)
socketio = SocketIO(app, cors_allowed_origins="*")


# register blueprints for routes
app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(lobby_bp, url_prefix="/lobby")
app.register_blueprint(game_bp, url_prefix="/game")


# Home route for login page
@app.route('/')
# Function to render home page
def home():
    """" render home page (login screen) """
    return render_template("index.html")
    


# register socket event handlers
register_socket_events(socketio)


with app.app_context():
    db.create_all()
    print("Tables created successfully!")

# Test socket route to verify SocketIO is working
@app.route("/socket-test")
# Function to test socket connection to server
def socket_test():
    """ 
        Render socket test page to verify SocketIO connection
    """
    # return socket test html page
    return render_template("socket_test.html")


if __name__ == '__main__':
    # defult port 5000.
    port = int(os.environ.get("PORT", 5000))
    host = os.environ.get("HOST", "0.0.0.0")
    # Avoid double-binding and select a free port if the default is taken.
    original_port = port
    max_tries = 20
    for _ in range(max_tries):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.5)
            if sock.connect_ex(("127.0.0.1", port)) != 0:
                break
        port += 1
    else:
        print(
            f"Ports {original_port}..{original_port + max_tries - 1} are in use. "
            "Stop the existing server or set PORT to a free port."
        )
        raise SystemExit(1)
    if port != original_port:
        print(f"Port {original_port} is in use; starting on {port} instead.")
    # print a message indicating server has started
    print(f"Starting Flask-SocketIO server on http://127.0.0.1:{port}")
    # get the host to be accessible externally and set debug mode to True
    socketio.run(app, host=host, port=port, debug=True, use_reloader=False)
