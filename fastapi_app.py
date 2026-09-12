from google.adk.apps import App
from google.adk.cli.fast_api import get_fast_api_app
from agent import root_agent
from collections.abc import AsyncIterator
import contextlib
from google.adk.runners import Runner
from fastapi import FastAPI
from google.adk.sessions.in_memory_session_service import InMemorySessionService
import os 

adk_app = App(
    root_agent=root_agent,
    name="app",
)

AGENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

@contextlib.asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # Runner for the A2A path, sharing the same session/artifact services as the
    # adk_api and reasoning_engine paths (see services.py). Imported here so the
    # agent is built after env/telemetry setup.
    from agent import root_agent

    local_session_service = InMemorySessionService()

    runner = Runner(
        app=adk_app,
        session_service=local_session_service,
        auto_create_session=True,
    )
    # Shared by the A2A path and the reasoning_engine adapter routes.
    app.state.runner = runner
    app.state.agent_app_name = adk_app.name
    yield


app: FastAPI = get_fast_api_app(
    agents_dir=AGENT_DIR,
    web=True,
    lifespan=lifespan,
)

if __name__ == "__main__":
    import uvicorn

    # Pass the ASGI app instance (or module string) to uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)