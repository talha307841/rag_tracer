from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from prometheus_client import make_asgi_app
from .routers import traces
import json

app = FastAPI(title="RAG Tracing & Hallucination Detection API")

# Include routers
app.include_router(traces.router)

# Prometheus metrics endpoint
app.mount("/metrics", make_asgi_app())

# WebSocket endpoint for real-time trace updates
@app.websocket("/ws/traces")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            # Process trace data
            trace_data = json.loads(data)
            # Echo back processed data (in a real implementation, this would be stored)
            await websocket.send_text(f"Trace received: {trace_data.get('user_query', '')}")
    except WebSocketDisconnect:
        print("WebSocket client disconnected")
