import json
import os

USER_FILE = "users.json"

def load_users():
    if not os.path.exists(USER_FILE):
        return {}

    try:
        with open(USER_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f, indent=4)

def login():

    users = load_users()

    print("\n=== MEMORY MAZE LOGIN ===")
    username = input("Enter Username: ").strip()

    if username in users:
        print(f"Welcome Back {username}")
    else:
        print("New Player Registered!")
        users[username] = {
            "wins": 0,
            "losses": 0
        }
        save_users(users)
        print(f"Account Created for {username}")

    return username