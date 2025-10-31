"""
Starts the FastAPI application and mounts API routers.

Responsibilities:
- Create and configure the FastAPI app
- Include API routes (versioned)
- Provide a uvicorn entrypoint for local development
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from dotenv import load_dotenv
load_dotenv()


# import router after app creation to avoid circular imports in larger projects
from src.app.api.v1.scene import router as scene_router

def create_app() -> FastAPI:
    app = FastAPI(
        title="Scene Builder Agent",
        description="Generates validated Scene JSON from natural language prompts",
        version="0.1.0",
    )

    # simple logging config
    logging.basicConfig(level=logging.INFO)
    app.logger = logging.getLogger("scene_builder")

    # CORS (adjust origins in production)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # include API routers
    app.include_router(scene_router, prefix="/v1/agent")
    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="127.0.0.1", port=8000, reload=True)
