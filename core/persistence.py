"""Persistence layer for StateManager.

This module provides JSON-based serialization and deserialization
of user states. States are persisted to disk so they survive bot restarts.

Real-world use cases:
- Save to /tmp/ or local directory (RAM-backed on restart, lost on reboot)
- Save to database (persistent across restarts)
- Cloud storage (DynamoDB, Firestore, etc.)

In this example, we use local JSON files for simplicity.
"""
import json
import os
from typing import Dict, Any
from pathlib import Path

from .state_manager import StateManager, UserStateData


class PersistenceManager:
    """Handles serialization and deserialization of StateManager to disk."""

    def __init__(self, data_dir: str = ".data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

    def _get_user_file(self, user_id: str) -> Path:
        """Get the JSON file path for a user."""
        # Sanitize user_id to avoid path traversal
        safe_id = user_id.replace("/", "_").replace("\\", "_")
        return self.data_dir / f"{safe_id}.json"

    def save_state(self, state_manager: StateManager, user_id: str) -> bool:
        """Save a user's state to JSON file."""
        try:
            state = state_manager.get_user_state(user_id)
            if not state:
                return False
            
            # Serialize navigation stack
            nav_data = state.navigation.serialize()
            
            data = {
                "user_id": state.user_id,
                "navigation": nav_data,
                "working_copy": state.working_copy,
                "applied_copy": state.applied_copy,
                "dirty_fields": state.dirty_fields,
                "message_id": state.message_id,
                "chat_id": state.chat_id,
                "updated_at": state.updated_at,
            }
            
            file_path = self._get_user_file(user_id)
            with open(file_path, "w") as f:
                json.dump(data, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error saving state for user {user_id}: {e}")
            return False

    def load_state(self, state_manager: StateManager, user_id: str) -> bool:
        """Load a user's state from JSON file and populate StateManager."""
        try:
            file_path = self._get_user_file(user_id)
            if not file_path.exists():
                return False
            
            with open(file_path, "r") as f:
                data = json.load(f)
            
            state_manager.deserialize(user_id, data)
            return True
        except Exception as e:
            print(f"Error loading state for user {user_id}: {e}")
            return False

    def delete_state(self, user_id: str) -> bool:
        """Delete a user's saved state file."""
        try:
            file_path = self._get_user_file(user_id)
            if file_path.exists():
                file_path.unlink()
                return True
            return False
        except Exception as e:
            print(f"Error deleting state for user {user_id}: {e}")
            return False

    def list_users(self) -> list:
        """List all users with saved states."""
        try:
            users = []
            for file in self.data_dir.glob("*.json"):
                users.append(file.stem)
            return users
        except Exception:
            return []
