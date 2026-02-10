♟️ Online Checkers & Chess

A full-stack, real-time multiplayer web application where players can compete in Checkers and Chess online. Built with Flask, Socket.IO, and SQLite — featuring matchmaking, ELO rankings, AI opponents, and game history.

🚀 Tech Stack
LayerTechnologyBackendPython, Flask, Flask-SocketIOFrontendJavaScript, HTML, CSSDatabaseSQLiteReal-TimeSocket.IO (WebSockets)

✨ Features
Core Gameplay

Real-time multiplayer — play Checkers or Chess against other players with live board updates via WebSockets
Move validation & rule enforcement — all moves are validated server-side to prevent illegal plays
AI bot opponent — practice offline against a built-in AI when no human opponent is available

User System

Authentication — secure user registration and login with session management
ELO rating system — competitive ranking that updates after every match
Game lobby & matchmaking — browse open games or get matched with an opponent automatically

History & Stats

Game history & replays — review past games move by move
Player profiles — track your win/loss record and rating over time


📦 Installation
Prerequisites

Python 3.8+
pip

Setup
bash# Clone the repository
git clone https://github.com/yourusername/online_Checkers.git
cd online_Checkers

# Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate        # Linux/macOS
venv\Scripts\activate           # Windows

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
The app will be available at http://localhost:5000 by default.
🎮 How to Play

Create an account or log in
Join the lobby and create a new game or join an existing one
Play — make your moves on the interactive board; the game enforces all rules automatically
Review — check your match history and watch replays of past games


🛠️ Built With

Flask — lightweight Python web framework
Flask-SocketIO — WebSocket support for real-time communication
SQLite — embedded relational database
Socket.IO — event-driven client-server communication
