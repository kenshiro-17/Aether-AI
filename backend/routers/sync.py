from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sync_manager import sync_manager
from database import get_db
from sqlalchemy.orm import Session
import json

router = APIRouter()

@router.websocket("/ws/sync/{device_id}")
async def websocket_endpoint(websocket: WebSocket, device_id: str, db: Session = Depends(get_db)):
    await sync_manager.connect(websocket, device_id)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            await sync_manager.handle_sync_message(websocket, message, db)
    except WebSocketDisconnect:
        sync_manager.disconnect(websocket)
        print(f"Device disconnected: {device_id}")
