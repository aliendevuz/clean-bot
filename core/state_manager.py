"""State manager using the Python `NavigationStack`.

This module provides a lightweight in-memory state manager suitable for
applications that need per-user state with a navigation stack. Page types
are strings so the library is agnostic about available pages.
"""
import time
from dataclasses import dataclass, field
from typing import Dict, Any, Optional

from .nav_stack_manager import NavigationStack
from .types import Page


@dataclass
class UserStateData:
    user_id: str
    navigation: NavigationStack
    working_copy: Dict[str, Any] = field(default_factory=dict)
    applied_copy: Dict[str, Any] = field(default_factory=dict)
    dirty_fields: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    message_id: Optional[int] = None
    chat_id: Optional[int] = None
    updated_at: int = field(default_factory=lambda: int(time.time() * 1000))


class StateManager:
    def __init__(self) -> None:
        self.states: Dict[str, UserStateData] = {}

    def create_user_state(self, user_id: str, chat_id: Optional[int] = None) -> UserStateData:
        root = Page(type="HOME", state={}, timestamp=int(time.time() * 1000))
        state = UserStateData(user_id=user_id, navigation=NavigationStack(initial_page=root), chat_id=chat_id, updated_at=int(time.time() * 1000))
        self.states[user_id] = state
        return state

    def get_user_state(self, user_id: str) -> Optional[UserStateData]:
        return self.states.get(user_id)

    def update_user_state(self, user_id: str, updates: Dict[str, Any]) -> bool:
        state = self.states.get(user_id)
        if not state:
            return False
        for key, value in updates.items():
            if key == "navigation" and isinstance(value, dict):
                state.navigation = NavigationStack.deserialize(value)
            else:
                setattr(state, key, value)
        state.updated_at = int(time.time() * 1000)
        return True

    def delete_user_state(self, user_id: str) -> bool:
        return self.states.pop(user_id, None) is not None

    def update_working_copy(self, user_id: str, config_key: str, new_value: Any) -> bool:
        state = self.states.get(user_id)
        if not state:
            return False
        old_value = state.applied_copy.get(config_key)
        state.working_copy[config_key] = new_value
        if old_value != new_value:
            state.dirty_fields[config_key] = {"old": old_value, "new": new_value}
        else:
            state.dirty_fields.pop(config_key, None)
        state.updated_at = int(time.time() * 1000)
        return True

    def discard_changes(self, user_id: str) -> bool:
        state = self.states.get(user_id)
        if not state:
            return False
        state.working_copy = dict(state.applied_copy)
        state.dirty_fields = {}
        state.updated_at = int(time.time() * 1000)
        return True

    def apply_changes(self, user_id: str) -> bool:
        state = self.states.get(user_id)
        if not state:
            return False
        state.applied_copy = dict(state.working_copy)
        state.dirty_fields = {}
        state.updated_at = int(time.time() * 1000)
        return True

    def has_unsaved_changes(self, user_id: str) -> bool:
        state = self.states.get(user_id)
        return bool(state and state.dirty_fields)

    def serialize_all(self) -> Dict[str, Any]:
        serialized: Dict[str, Any] = {}
        for uid, s in self.states.items():
            serialized[uid] = {
                "user_id": s.user_id,
                "navigation": s.navigation.serialize(),
                "working_copy": s.working_copy,
                "applied_copy": s.applied_copy,
                "dirty_fields": s.dirty_fields,
                "message_id": s.message_id,
                "chat_id": s.chat_id,
                "updated_at": s.updated_at,
            }
        return serialized

    def deserialize(self, user_id: str, data: Dict[str, Any]) -> UserStateData:
        nav = NavigationStack.deserialize(data.get("navigation", {"stack": [], "current_index": -1}))
        state = UserStateData(
            user_id=user_id,
            navigation=nav,
            working_copy=data.get("working_copy", {}),
            applied_copy=data.get("applied_copy", {}),
            dirty_fields=data.get("dirty_fields", {}),
            message_id=data.get("message_id"),
            chat_id=data.get("chat_id"),
            updated_at=data.get("updated_at", int(time.time() * 1000)),
        )
        self.states[user_id] = state
        return state