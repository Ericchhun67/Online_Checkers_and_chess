"""
Simple test script for SocketIO lobby routes.
tests:
    - connect
    - create_room
    - join_room
    - get_rooms
    - leave_room
"""

import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, socketio
import utils.socket_handlers as socket_handlers


def find_event(events, name):
    for event in events:
        if event.get("name") == name:
            return event
    return None


socket_handlers.lobby_rooms.clear()

client = socketio.test_client(app)
assert client.is_connected()

events = client.get_received()
print("connect events", events)
assert find_event(events, "server_message") is not None

client.emit("create_room", {"room_name": "room1", "game_type": "checkers"})
events = client.get_received()
print("create_room events", events)
assert find_event(events, "room_created") is not None

client.emit("join_room", {"username": "alice", "room_name": "room1"})
events = client.get_received()
print("join_room events", events)
assert find_event(events, "room_joined") is not None

client.emit("get_rooms")
events = client.get_received()
print("get_rooms events", events)
assert find_event(events, "rooms_list") is not None

client.emit("leave_room", {"username": "alice", "room_name": "room1"})
events = client.get_received()
print("leave_room events", events)
assert find_event(events, "room_left") is not None

client.disconnect()
print("socket tests passed!")
