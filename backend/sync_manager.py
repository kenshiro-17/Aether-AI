from typing import List, Dict, Any
from fastapi import WebSocket
import json
import time

class SyncManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        # Store pending sync items in memory for now, ideally in Redis or DB
        self.sync_queue: Dict[str, List[Any]] = {}

    async def connect(self, websocket: WebSocket, device_id: str):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"Device connected: {device_id}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                # Handle disconnected clients
                print(f"Failed to broadcast to client: {e}")
                pass

    async def handle_sync_message(self, websocket: WebSocket, data: dict, db):
        """
        Handle incoming sync data from a device.
        Data format:
        {
            "type": "delta_sync",
            "last_synced_at": "timestamp",
            "changes": [ ... ]
        }
        """
        msg_type = data.get("type")
        
        if msg_type == "delta_sync":
            changes = data.get("changes", [])
            # Process changes (upsert to DB)
            await self.process_incoming_changes(changes, db)
            
            # Send back server changes since last_synced_at
            last_synced = data.get("last_synced_at", 0)
            server_changes = await self.get_server_changes(last_synced, db)
            
            response = {
                "type": "sync_response",
                "timestamp": time.time(),
                "changes": server_changes
            }
            await websocket.send_text(json.dumps(response))

    async def process_incoming_changes(self, changes: List[dict], db):
        """
        Process incoming changes from client and update database.
        Each change should have: {id, type, data, timestamp}
        """
        print(f"Received {len(changes)} changes from client")
        try:
            from routers.chat import Conversation, Message
            import datetime
            
            for change in changes:
                change_type = change.get("type")
                data = change.get("data", {})
                
                if change_type == "conversation":
                    # Upsert conversation
                    conv_id = data.get("id")
                    existing = db.query(Conversation).filter(Conversation.id == conv_id).first()
                    if existing:
                        existing.title = data.get("title", existing.title)
                        existing.updated_at = datetime.datetime.now(datetime.timezone.utc)
                    else:
                        new_conv = Conversation(
                            id=conv_id,
                            title=data.get("title", "Untitled"),
                            created_at=datetime.datetime.fromisoformat(data.get("created_at")) if data.get("created_at") else datetime.datetime.now(datetime.timezone.utc),
                            updated_at=datetime.datetime.now(datetime.timezone.utc)
                        )
                        db.add(new_conv)
                        
                elif change_type == "message":
                    # Upsert message
                    msg_id = data.get("id")
                    existing = db.query(Message).filter(Message.id == msg_id).first()
                    if not existing:
                        new_msg = Message(
                            id=msg_id,
                            conversation_id=data.get("conversation_id"),
                            role=data.get("role"),
                            content=data.get("content"),
                            created_at=datetime.datetime.fromisoformat(data.get("created_at")) if data.get("created_at") else datetime.datetime.now(datetime.timezone.utc)
                        )
                        db.add(new_msg)
            
            db.commit()
            print(f"Successfully processed {len(changes)} changes")
        except Exception as e:
            print(f"Error processing changes: {e}")
            db.rollback()

    async def get_server_changes(self, last_synced: float, db):
        """
        Query DB for items updated after last_synced timestamp
        Returns list of changes in format: {type, data, timestamp}
        """
        try:
            from routers.chat import Conversation, Message
            import datetime
            
            changes = []
            last_sync_time = datetime.datetime.fromtimestamp(last_synced, tz=datetime.timezone.utc)
            
            # Get updated conversations
            conversations = db.query(Conversation).filter(
                Conversation.updated_at > last_sync_time
            ).all()
            
            for conv in conversations:
                changes.append({
                    "type": "conversation",
                    "data": {
                        "id": conv.id,
                        "title": conv.title,
                        "created_at": conv.created_at.isoformat(),
                        "updated_at": conv.updated_at.isoformat()
                    },
                    "timestamp": conv.updated_at.timestamp()
                })
            
            # Get new messages
            messages = db.query(Message).filter(
                Message.created_at > last_sync_time
            ).all()
            
            for msg in messages:
                changes.append({
                    "type": "message",
                    "data": {
                        "id": msg.id,
                        "conversation_id": msg.conversation_id,
                        "role": msg.role,
                        "content": msg.content,
                        "created_at": msg.created_at.isoformat()
                    },
                    "timestamp": msg.created_at.timestamp()
                })
            
            print(f"Returning {len(changes)} server changes since {last_synced}")
            return changes
        except Exception as e:
            print(f"Error getting server changes: {e}")
            return []

sync_manager = SyncManager()
