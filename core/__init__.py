"""Core state and navigation management library.

Provides:
- NavigationStack: User navigation history management
- StateManager: Per-user state with working/applied copy tracking
- Persistence layers:
  - PersistenceManager: Local JSON file storage
  - DynamoDBPersistenceManager: AWS DynamoDB storage (production)

Example:
    from core.state_manager import StateManager
    from core.persistence_dynamodb import DynamoDBPersistenceManager
    
    state_manager = StateManager()
    persistence = DynamoDBPersistenceManager()
    
    state_manager.create_user_state("user_123", chat_id=999)
    persistence.save_state(state_manager, "user_123")
"""

__version__ = "1.0.0"
__author__ = "Alien Dev"

# Export main classes
from .types import Page, NavigationState
from .nav_stack_manager import NavigationStack
from .state_manager import StateManager, UserStateData
from .persistence import PersistenceManager
from .persistence_dynamodb import DynamoDBPersistenceManager

__all__ = [
    "Page",
    "NavigationState",
    "NavigationStack",
    "StateManager",
    "UserStateData",
    "PersistenceManager",
    "DynamoDBPersistenceManager",
]
