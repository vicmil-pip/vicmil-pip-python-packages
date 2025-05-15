import json
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import pathlib

def get_directory_path(__file__in, up_directories=0):
    return str(pathlib.Path(__file__in).parents[up_directories].resolve()).replace("\\", "/")

class UserManager:
    def __init__(self, users_file: str = get_directory_path(__file__) + "/users.json"):
        self.users_file = users_file
        self.users = self.load_users()

    def load_users(self) -> dict:
        try:
            with open(self.users_file, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def save_users(self):
        with open(self.users_file, "w") as f:
            json.dump(self.users, f, indent=4)

    def add_user(self, username: str, password: str, permissions=None, role: str = "user") -> bool:
        if permissions is None:
            permissions = []
        if username in self.users:
            return False  # User already exists

        self.users[username] = {
            "role": role,
            "hashed_password": generate_password_hash(password),
            "password_version": 1,
            "permissions": list(set(permissions + ["user"])),
            "created_at": datetime.utcnow().isoformat(),
            "data": {}
        }
        return True
    
    def remove_user(self, username: str) -> bool:
        """Removes a user from the system."""
        if username in self.users:
            del self.users[username]
            return True
        return False
    
    def list_users(self):
        return self.users.keys()

    def change_password(self, username: str, new_password: str) -> bool:
        user = self.users.get(username)
        if not user:
            return False

        user["hashed_password"] = generate_password_hash(new_password)
        user["password_version"] += 1
        return True

    def set_permissions(self, username: str, permissions: list) -> bool:
        user = self.users.get(username)
        if not user:
            return False

        user["permissions"] = permissions
        return True
    
    def set_role(self, username: str, role: str) -> bool:
        user = self.users.get(username)
        if not user:
            return False

        user["role"] = role
        return True

    def get_permissions(self, username: str) -> list:
        return self.users.get(username, {}).get("permissions", [])
    
    def get_role(self, username: str) -> str:
        return self.users.get(username, {}).get("role")

    def has_permissions(self, username: str, required: list) -> bool:
        if self.get_role(username=username) == "admin":
            return True # Admin has access to everything
        
        user_perms = set(self.get_permissions(username))
        return all(perm in user_perms for perm in required)

    def valid_password_version(self, username: str, version: int) -> bool:
        user = self.users.get(username)
        return user and user["password_version"] == version
    
    def verify_password(self, username: str, password: str):
        print("verify_password", username, password)

        user = self.users.get(username)
        if not user:
            print("User does not exist")
            return False
        
        if check_password_hash(user["hashed_password"], password):
            print("Correct credentials!")
            return True
        
        print("Invalid credentials")
        return False
        
    def get_password_version(self, username: str):
        user = self.users.get(username)
        if not user:
            return None
        
        return user["password_version"]

    def has_access(self, username: str, password_version: int, required_permissions: list) -> bool:
        return (
            username in self.users and
            self.valid_password_version(username, password_version) and
            self.has_permissions(username, required_permissions)
        )

    def set_user_data(self, username: str, data: dict) -> bool:
        user = self.users.get(username)
        if not user:
            return False
        user["data"] = data
        return True

    def get_user_data(self, username: str):
        return self.users.get(username, {}).get("data")