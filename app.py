"""Run with: uvicorn app:app --reload"""
import asyncio
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from eonverse.world import World

ROOT = Path(__file__).resolve().parent
world = World()
clients: set[WebSocket] = set()


async def universe_loop():
    while True:
        await asyncio.sleep(1)
        world.step()
        snapshot = world.snapshot()
        for client in tuple(clients):
            try:
                await client.send_json(snapshot)
            except Exception:
                clients.discard(client)


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(universe_loop())
    try:
        yield
    finally:
        task.cancel()
        await asyncio.gather(task, return_exceptions=True)


app = FastAPI(title="EONVERSE", version="0.1.0", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=ROOT / "static"), name="static")


@app.get("/")
async def home():
    return FileResponse(ROOT / "static" / "index.html")


@app.get("/api/world")
async def state():
    return world.snapshot()


@app.websocket("/ws/world")
async def websocket_world(websocket: WebSocket):
    await websocket.accept()
    clients.add(websocket)
    try:
        await websocket.send_json(world.snapshot())
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        clients.discard(websocket)
