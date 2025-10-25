from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import chat_api, agent_api, storage_api, article_api, health_api, tool_api, plant_api, image_api, user_api
from app.core.database import check_mongodb_health
from contextlib import asynccontextmanager
from app.core.config import settings
import os

@asynccontextmanager
async def lifespan(app: FastAPI):
    await check_mongodb_health()
    yield

app = FastAPI(
    title="Aiven API",
    description="API for Aiven application",
    version="1.0.0",
    lifespan=lifespan
)

# Allow React frontend access (adjust this in production!)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Controllers
app.include_router(health_api.router, prefix="/api", tags=["Health"])
app.include_router(user_api.router, prefix="/api/user", tags=["User"])
app.include_router(chat_api.router, prefix="/api/chat", tags=["Chat"])
app.include_router(agent_api.router, prefix="/api/agent", tags=["Agent"])
app.include_router(article_api.router, prefix="/api/article", tags=["Article"])
app.include_router(storage_api.router, prefix="/api/storage", tags=["Storage"])
app.include_router(tool_api.router, prefix="/api/tool", tags=["Tool"])
app.include_router(plant_api.router, prefix="/api/plant", tags=["Plant"])
app.include_router(image_api.router, prefix="/api/image", tags=["Image"])

# Configure LangSmith tracing
if settings.langsmith_tracing == "true":
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_API_KEY"] = settings.langchain_api_key
    os.environ["LANGCHAIN_PROJECT"] = settings.langchain_project

