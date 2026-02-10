""" 
    Simple test script for authentication routes
    tests:
        - Register user
        - Login user 
        - Logout user
"""



import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app



client = app.test_client()

response = client.post('/auth/register', json={
    "username": "TestUser",
    "email": "test@example.com",
    "password": "password123"
})


print("Register", response.status_code, response.json)


response = client.post('/auth/login', json={
    "email": "test@example.com",
    "password": "password123"
})

print("Login", response.status_code, response.json)



response = client.post('/auth/logout')
print("logout", response.status_code, response.json)

