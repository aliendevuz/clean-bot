import time
from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, Any, List, TypedDict


@dataclass
class Page:
    """A single navigation page.

    The `type` is a string so the library does not need to know a fixed
    enum of page types — users of the library can use any string identifiers.
    """
    type: str
    state: Optional[Dict[str, Any]] = field(default_factory=dict)
    timestamp: int = field(default_factory=lambda: int(time.time() * 1000))

    def to_dict(self) -> Dict[str, Any]:
        return {"type": self.type, "state": self.state or {}, "timestamp": self.timestamp}

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Page":
        return Page(type=data["type"], state=data.get("state") or {}, timestamp=data.get("timestamp", int(time.time() * 1000)))


class NavigationState(TypedDict):
    stack: List[Dict[str, Any]]
    current_index: int
