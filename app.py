"""Run with: uvicorn app:app --reload"""
import asyncio
import logging
from contextlib import asynccontextmanager
from pathlib import Path
from dotenv import load_dotenv

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from eonverse.cloud_ai import advise_once, enabled as cloud_ai_enabled
from eonverse.world import World
from eonverse.resource_catalog import MATERIAL_CATALOG
from eonverse.persistence import load_world, save_world

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / '.env', override=False)
SAVE_PATH = ROOT / 'data' / 'world.json'
try:
    world = load_world(SAVE_PATH) if SAVE_PATH.exists() else World()
except (OSError, ValueError, KeyError, TypeError) as exc:
    raise RuntimeError(f'Invalid world save {SAVE_PATH}: {exc}') from exc
clients: set[WebSocket] = set()
MAX_CLIENTS = 64
logger = logging.getLogger(__name__)
MAX_CLOUD_REQUESTS_PER_SESSION = 60


async def universe_loop():
    cloud_requests = 0
    while True:
        await asyncio.sleep(1)
        try:
            world.step()
            if (cloud_ai_enabled() and cloud_requests < MAX_CLOUD_REQUESTS_PER_SESSION
                    and world.tick % 120 == 0):
                cloud_requests += 1
                asyncio.create_task(advise_once(world))
            if world.tick % 30 == 0:
                save_world(world, SAVE_PATH)
            snapshot = world.snapshot()
        except Exception:
            logger.exception("World simulation tick failed")
            continue
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


@app.get("/api/resources/catalog")
async def resource_catalog():
    return {"count": len(MATERIAL_CATALOG), "materials": MATERIAL_CATALOG}


@app.get("/api/world")
async def state():
    return world.snapshot()


@app.websocket("/ws/world")
async def websocket_world(websocket: WebSocket):
    if len(clients) >= MAX_CLIENTS:
        await websocket.close(code=1013, reason="Too many observers")
        return
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
