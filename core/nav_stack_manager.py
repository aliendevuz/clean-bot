"""Navigation stack manager (Python).

This implementation uses string page identifiers so the library does not
require a fixed enum of possible pages. Pages are simple dict-serializable
objects and the stack can be serialized/deserialized for storage.
"""
import time
from typing import List, Optional, Dict, Any

from .types import Page, NavigationState


class NavigationStack:
    def __init__(self, initial_page: Optional[Page] = None) -> None:
        self.stack: List[Page] = []
        if initial_page:
            self.stack.append(initial_page)

    def push(self, page_type: str, state: Optional[Dict[str, Any]] = None) -> Page:
        page = Page(type=page_type, state=state or {}, timestamp=int(time.time() * 1000))
        self.stack.append(page)
        return page

    def pop(self) -> Optional[Page]:
        if len(self.stack) <= 1:
            return None
        return self.stack.pop()

    def replace(self, page_type: str, state: Optional[Dict[str, Any]] = None) -> Page:
        page = Page(type=page_type, state=state or {}, timestamp=int(time.time() * 1000))
        if not self.stack:
            self.stack.append(page)
        else:
            self.stack[-1] = page
        return page

    def reset(self, page_type: str, state: Optional[Dict[str, Any]] = None) -> Page:
        page = Page(type=page_type, state=state or {}, timestamp=int(time.time() * 1000))
        self.stack = [page]
        return page

    def can_go_back(self) -> bool:
        return len(self.stack) > 1

    def get_current_page(self) -> Optional[Page]:
        return self.stack[-1] if self.stack else None

    def get_stack(self) -> List[Page]:
        return list(self.stack)

    def get_depth(self) -> int:
        return len(self.stack)

    def has_page_in_stack(self, page_type: str) -> bool:
        return any(p.type == page_type for p in self.stack)

    def serialize(self) -> NavigationState:
        return {"stack": [p.to_dict() for p in self.stack], "current_index": len(self.stack) - 1}

    @staticmethod
    def deserialize(state: NavigationState) -> "NavigationStack":
        nav = NavigationStack()
        nav.stack = [Page.from_dict(p) for p in state.get("stack", [])]
        return nav

    def pop_to(self, page_type: str) -> bool:
        index = next((i for i, p in enumerate(self.stack) if p.type == page_type), -1)
        if index == -1 or index == len(self.stack) - 1:
            return False
        self.stack = self.stack[: index + 1]
        return True

    def update_current_page_state(self, new_state: Dict[str, Any]) -> bool:
        if not self.stack:
            return False
        current = self.stack[-1]
        current.state = {**(current.state or {}), **new_state}
        return True
