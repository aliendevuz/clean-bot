"""DynamoDB-based persistence for StateManager and NavigationStack.

This module provides production-ready persistence using AWS DynamoDB or LocalStack.
It stores user states with their complete navigation stacks and configurations.

Supports:
- LocalStack (testing at localhost:4566)
- AWS DynamoDB (production)
- Automatic table creation and migration

Example:
    persistence = DynamoDBPersistenceManager()
    persistence.save_state(state_manager, "user_123")
    persistence.load_state(state_manager, "user_123")
"""
import json
import os
from typing import Dict, Any, Optional, List

import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

from .state_manager import StateManager, UserStateData
from .types import Page


class DynamoDBPersistenceManager:
    """Manages persistence of StateManager data to DynamoDB.
    
    Tables created:
    - user_states: Stores user navigation stacks and configurations
    - config_models: Stores configuration schema definitions
    """

    def __init__(self, config: Optional[Dict[str, str]] = None, auto_create_tables: bool = True):
        """Initialize DynamoDB persistence manager.
        
        Args:
            config: Optional configuration dict with keys:
                - region: AWS region (default: us-east-1)
                - endpoint: DynamoDB endpoint (default: http://localhost:4566)
                - access_key: AWS access key (default: test)
                - secret_key: AWS secret key (default: test)
                - user_states_table: Table name (default: user_states)
                - config_models_table: Table name (default: config_models)
            auto_create_tables: Whether to auto-create tables on init (default: True)
        """
        load_dotenv()
        
        if config is None:
            config = self._load_config_from_env()
        
        self.region = config.get("region", "us-east-1")
        self.endpoint = config.get("endpoint", "http://localhost:4566")
        self.access_key = config.get("access_key", "test")
        self.secret_key = config.get("secret_key", "test")
        self.user_states_table = config.get("user_states_table", "user_states")
        self.config_models_table = config.get("config_models_table", "config_models")
        
        # Initialize DynamoDB client
        self.client = self._create_client()
        
        # Auto-create tables if needed
        if auto_create_tables:
            self._ensure_tables_exist()

    @staticmethod
    def _load_config_from_env() -> Dict[str, str]:
        """Load configuration from environment variables."""
        return {
            "region": os.getenv("AWS_REGION", "us-east-1"),
            "endpoint": os.getenv("DYNAMODB_ENDPOINT", "http://localhost:4566"),
            "access_key": os.getenv("AWS_ACCESS_KEY_ID", "test"),
            "secret_key": os.getenv("AWS_SECRET_ACCESS_KEY", "test"),
            "user_states_table": os.getenv("USER_STATES_TABLE", "user_states"),
            "config_models_table": os.getenv("CONFIG_MODELS_TABLE", "config_models"),
        }

    def _create_client(self):
        """Create boto3 DynamoDB client."""
        return boto3.client(
            "dynamodb",
            region_name=self.region,
            endpoint_url=self.endpoint,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
        )

    def _table_exists(self, table_name: str) -> bool:
        """Check if a table exists."""
        try:
            self.client.describe_table(TableName=table_name)
            return True
        except ClientError as e:
            if e.response["Error"]["Code"] == "ResourceNotFoundException":
                return False
            raise

    def _create_user_states_table(self) -> None:
        """Create user_states table if it doesn't exist."""
        if self._table_exists(self.user_states_table):
            return
        
        try:
            self.client.create_table(
                TableName=self.user_states_table,
                KeySchema=[
                    {"AttributeName": "PK", "KeyType": "HASH"},
                    {"AttributeName": "SK", "KeyType": "RANGE"},
                ],
                AttributeDefinitions=[
                    {"AttributeName": "PK", "AttributeType": "S"},
                    {"AttributeName": "SK", "AttributeType": "S"},
                ],
                BillingMode="PAY_PER_REQUEST",
            )
        except ClientError as e:
            if e.response["Error"]["Code"] != "ResourceInUseException":
                raise

    def _create_config_models_table(self) -> None:
        """Create config_models table if it doesn't exist."""
        if self._table_exists(self.config_models_table):
            return
        
        try:
            self.client.create_table(
                TableName=self.config_models_table,
                KeySchema=[
                    {"AttributeName": "PK", "KeyType": "HASH"},
                    {"AttributeName": "SK", "KeyType": "RANGE"},
                ],
                AttributeDefinitions=[
                    {"AttributeName": "PK", "AttributeType": "S"},
                    {"AttributeName": "SK", "AttributeType": "S"},
                ],
                BillingMode="PAY_PER_REQUEST",
            )
        except ClientError as e:
            if e.response["Error"]["Code"] != "ResourceInUseException":
                raise

    def _ensure_tables_exist(self) -> None:
        """Create tables if they don't exist (auto-migration)."""
        try:
            self._create_user_states_table()
            self._create_config_models_table()
        except Exception as e:
            # Non-fatal: tables might already exist or be in creation
            pass


    def _serialize_state(self, state: UserStateData) -> Dict[str, Any]:
        """Convert UserStateData to DynamoDB item format."""
        nav_data = state.navigation.serialize()
        
        return {
            "PK": {"S": f"USER#{state.user_id}"},
            "SK": {"S": "STATE"},
            "user_id": {"S": state.user_id},
            "chat_id": {"N": str(state.chat_id or 0)},
            "message_id": {"N": str(state.message_id or 0)} if state.message_id else {"NULL": True},
            "navigation": {"S": json.dumps(nav_data)},
            "working_copy": {"S": json.dumps(state.working_copy)},
            "applied_copy": {"S": json.dumps(state.applied_copy)},
            "dirty_fields": {"S": json.dumps(state.dirty_fields)},
            "updated_at": {"N": str(state.updated_at)},
        }

    def _deserialize_state(self, item: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Convert DynamoDB item to state dict format."""
        nav_str = item.get("navigation", {}).get("S", "{}")
        working_str = item.get("working_copy", {}).get("S", "{}")
        applied_str = item.get("applied_copy", {}).get("S", "{}")
        dirty_str = item.get("dirty_fields", {}).get("S", "{}")
        
        return {
            "user_id": user_id,
            "navigation": json.loads(nav_str),
            "working_copy": json.loads(working_str),
            "applied_copy": json.loads(applied_str),
            "dirty_fields": json.loads(dirty_str),
            "chat_id": int(item.get("chat_id", {}).get("N", 0)),
            "message_id": int(item.get("message_id", {}).get("N", 0)) if item.get("message_id", {}).get("N") else None,
            "updated_at": int(item.get("updated_at", {}).get("N", 0)),
        }

    def save_state(self, state_manager: StateManager, user_id: str) -> bool:
        """Save a user's state to DynamoDB.
        
        Args:
            state_manager: The StateManager instance
            user_id: The user ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            state = state_manager.get_user_state(user_id)
            if not state:
                return False
            
            item = self._serialize_state(state)
            
            self.client.put_item(
                TableName=self.user_states_table,
                Item=item,
            )
            
            return True
        except ClientError as e:
            print(f"❌ Error saving state for user {user_id}: {e}")
            return False

    def load_state(self, state_manager: StateManager, user_id: str) -> bool:
        """Load a user's state from DynamoDB.
        
        Args:
            state_manager: The StateManager instance
            user_id: The user ID
            
        Returns:
            True if state loaded, False if not found or error
        """
        try:
            response = self.client.get_item(
                TableName=self.user_states_table,
                Key={
                    "PK": {"S": f"USER#{user_id}"},
                    "SK": {"S": "STATE"},
                },
            )
            
            if "Item" not in response:
                return False
            
            item = response["Item"]
            state_data = self._deserialize_state(item, user_id)
            
            state_manager.deserialize(user_id, state_data)
            return True
            
        except ClientError as e:
            if e.response["Error"]["Code"] != "ResourceNotFoundException":
                print(f"❌ Error loading state for user {user_id}: {e}")
            return False

    def delete_state(self, user_id: str) -> bool:
        """Delete a user's state from DynamoDB.
        
        Args:
            user_id: The user ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.client.delete_item(
                TableName=self.user_states_table,
                Key={
                    "PK": {"S": f"USER#{user_id}"},
                    "SK": {"S": "STATE"},
                },
            )
            return True
        except ClientError as e:
            print(f"❌ Error deleting state for user {user_id}: {e}")
            return False

    def list_users(self) -> List[str]:
        """List all users with saved states.
        
        Returns:
            List of user IDs
        """
        try:
            users = []
            response = self.client.scan(
                TableName=self.user_states_table,
                ProjectionExpression="PK",
            )
            
            for item in response.get("Items", []):
                pk = item.get("PK", {}).get("S", "")
                if pk.startswith("USER#"):
                    user_id = pk.replace("USER#", "")
                    users.append(user_id)
            
            # Handle pagination
            while "LastEvaluatedKey" in response:
                response = self.client.scan(
                    TableName=self.user_states_table,
                    ProjectionExpression="PK",
                    ExclusiveStartKey=response["LastEvaluatedKey"],
                )
                for item in response.get("Items", []):
                    pk = item.get("PK", {}).get("S", "")
                    if pk.startswith("USER#"):
                        user_id = pk.replace("USER#", "")
                        users.append(user_id)
            
            return users
        except ClientError as e:
            print(f"❌ Error listing users: {e}")
            return []

    def table_exists(self, table_name: str) -> bool:
        """Check if a table exists."""
        try:
            self.client.describe_table(TableName=table_name)
            return True
        except ClientError as e:
            if e.response["Error"]["Code"] == "ResourceNotFoundException":
                return False
            raise

    def save_config_model(self, config_key: str, config_type: str, 
                         description: str = "", schema: Optional[Dict] = None) -> bool:
        """Save a configuration model schema to DynamoDB.
        
        Args:
            config_key: The configuration key
            config_type: The configuration type (e.g., 'string', 'number', 'object')
            description: Optional description
            schema: Optional JSON schema for validation
            
        Returns:
            True if successful, False otherwise
        """
        try:
            item = {
                "PK": {"S": "CONFIGS"},
                "SK": {"S": f"CONFIG#{config_key}"},
                "config_key": {"S": config_key},
                "config_type": {"S": config_type},
                "description": {"S": description},
                "schema": {"S": json.dumps(schema or {})},
                "created_at": {"N": str(int(__import__('time').time() * 1000))},
                "updated_at": {"N": str(int(__import__('time').time() * 1000))},
            }
            
            self.client.put_item(
                TableName=self.config_models_table,
                Item=item,
            )
            return True
        except ClientError as e:
            print(f"❌ Error saving config model: {e}")
            return False

    def get_config_model(self, config_key: str) -> Optional[Dict[str, Any]]:
        """Get a configuration model schema.
        
        Args:
            config_key: The configuration key
            
        Returns:
            Configuration model dict or None if not found
        """
        try:
            response = self.client.get_item(
                TableName=self.config_models_table,
                Key={
                    "PK": {"S": "CONFIGS"},
                    "SK": {"S": f"CONFIG#{config_key}"},
                },
            )
            
            if "Item" not in response:
                return None
            
            item = response["Item"]
            return {
                "config_key": item.get("config_key", {}).get("S", ""),
                "config_type": item.get("config_type", {}).get("S", ""),
                "description": item.get("description", {}).get("S", ""),
                "schema": json.loads(item.get("schema", {}).get("S", "{}")),
            }
        except ClientError as e:
            print(f"❌ Error loading config model: {e}")
            return None

    def list_config_models(self) -> List[Dict[str, Any]]:
        """List all configuration models.
        
        Returns:
            List of configuration model dicts
        """
        try:
            models = []
            response = self.client.query(
                TableName=self.config_models_table,
                KeyConditionExpression="PK = :pk",
                ExpressionAttributeValues={":pk": {"S": "CONFIGS"}},
            )
            
            for item in response.get("Items", []):
                models.append({
                    "config_key": item.get("config_key", {}).get("S", ""),
                    "config_type": item.get("config_type", {}).get("S", ""),
                    "description": item.get("description", {}).get("S", ""),
                })
            
            # Handle pagination
            while "LastEvaluatedKey" in response:
                response = self.client.query(
                    TableName=self.config_models_table,
                    KeyConditionExpression="PK = :pk",
                    ExpressionAttributeValues={":pk": {"S": "CONFIGS"}},
                    ExclusiveStartKey=response["LastEvaluatedKey"],
                )
                for item in response.get("Items", []):
                    models.append({
                        "config_key": item.get("config_key", {}).get("S", ""),
                        "config_type": item.get("config_type", {}).get("S", ""),
                        "description": item.get("description", {}).get("S", ""),
                    })
            
            return models
        except ClientError as e:
            print(f"❌ Error listing config models: {e}")
            return []
