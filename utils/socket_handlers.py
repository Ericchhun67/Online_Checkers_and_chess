from flask_socketio import emit, join_room, leave_room
from utils.game_logic import GameLogic

# Active games and lobby data
active_games = {}
lobby_rooms = {}

def register_socket_events(socketio):
    """Register socket event handlers."""

    # contection to server
    @socketio.on("connect")
    def handle_connect():
        """ 
            Handle a new client connection.
            Notify the client of successful connection.
        """
        # print the connection message to the server console
        print("A user connected to the server.")
        # send a welcome message to the connected client
        emit("server_message", {"message": "Connected to the Chess & Checkers lobby!"})
    # disconnection from server
    @socketio.on("disconnect")
    def handle_disconnect():
        """ 
            Handle client disconnection.
        """
        # print the disconnection message to the server console
        print("A user disconnected from the server.")
        # notify all clients about the disconnection
        emit("server_message", {"message": "A user disconnected."}, broadcast=True)

    #  Create a new room server
    @socketio.on("create_room")
    def handle_create_room(data):
        """" 
            Create a new game room in the lobby.
        """
        # extract room details from data
        room_name = data.get("room_name")
        # default to checkers if not specified
        game_type = data.get("game_type", "checkers")
        # check if room already exists in the lobby rooms
        if room_name in lobby_rooms:
            # room exists, send error message
            emit("error", {"message": "Room already exists."})
            # return none to exit the function
            return

        # Create the room
        lobby_rooms[room_name] = {
            # Initialize game logic for the room based on game type
            "game": GameLogic(game_type),
            "players": [] # list of players in the room store in a empty list
        }
        # print room creation message to server console
        print(f"🏠 Room created: {room_name} ({game_type})")
        # notify all clients about the new room
        emit("room_created", {
            "room_name": room_name,
            "game_type": game_type
        }, broadcast=True)  # broadcast to all users

    # Join an existing room
    @socketio.on("join_room")
    # Function to handle joining a room
    def handle_join_room(data):
        """"
            Handle a user joining an existing game room.
        """
        # extract username and room name from data
        username = data.get("username")
        room_name = data.get("room_name")
        # check if room is not found in the lobby rooms
        if room_name not in lobby_rooms:
            # send error message if room not found
            emit("error", {"message": "Room not found."})
            return

        # Add user and join room
        lobby_rooms[room_name]["players"].append(username)
        join_room(room_name)
        # print join room message to server console
        print(f"{username} joined {room_name}")
        # send confirmation of joining the room
        emit("room_joined", {
            "username": username,
            "room_name": room_name,
            "players": lobby_rooms[room_name]["players"]
        }, to=room_name)

        # Notify all users that a player joined
        emit("server_message", {
            "message": f"{username} joined {room_name}"
        }, broadcast=True)

    # Leave room
    @socketio.on("leave_room")
    def handle_leave_room(data):
        """" 
            Handle a user leaving a game room.
        """
        username = data.get("username")
        room_name = data.get("room_name")

        if room_name in lobby_rooms and username in lobby_rooms[room_name]["players"]:
            lobby_rooms[room_name]["players"].remove(username)
            leave_room(room_name)
            print(f"🚪 {username} left {room_name}")
            emit("room_left", {
                "username": username,
                "room_name": room_name
            }, to=room_name)

    # Sync room list to all connected users
    @socketio.on("get_rooms")
    def handle_get_rooms():
        emit("rooms_list", {"rooms": list(lobby_rooms.keys())})
    
    
    
        
        
        
