import json
import os

CONFIG_FILE = "db_config.json"

print("MySQL Configuration")

user = input("Enter your MySQL username: ").strip()
if not user:
    print("Username cannot be empty!")
    exit(1)

password = input("Enter your MySQL password: ").strip()
if not password:
    print("Password cannot be empty.")
    exit(1)

db_config = {
    "host": "localhost",
    "user": user,
    "password": password
}

with open(CONFIG_FILE, "w") as f:
    json.dump(db_config, f, indent=4)

print("✅ db_config.json created successfully.")
