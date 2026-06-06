import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .database import init_db
from .routes import alerts, governance, pipelines, reliability
from .simulation.metrics_engine import MetricsEngine

engine = MetricsEngine()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    task = asyncio.create_task(engine.run_loop())
    yield
    engine.stop()
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(reliability.router)
app.include_router(pipelines.router)
app.include_router(governance.router)
app.include_router(alerts.router)


@app.get("/api/health")
async def health():
    return {"status": "ok", "app": settings.app_name}
