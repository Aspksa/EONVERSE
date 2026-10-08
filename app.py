"""Run with: uvicorn app:app --reload"""
import asyncio
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from eonverse.world import World
from eonverse.persistence import load_world, save_world

ROOT = Path(__file__).resolve().parent
SAVE_PATH = ROOT / 'data' / 'world.json'
try:
    world = load_world(SAVE_PATH) if SAVE_PATH.exists() else World()
except (OSError, ValueError, KeyError, TypeError) as exc:
    raise RuntimeError(f'Invalid world save {SAVE_PATH}: {exc}') from exc
clients: set[WebSocket] = set()


async def universe_loop():
    while True:
        await asyncio.sleep(1)
        world.step()
        if world.tick % 30 == 0:
            save_world(world, SAVE_PATH)
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
        save_world(world, SAVE_PATH)
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
