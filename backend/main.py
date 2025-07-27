from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import chat, agent, storage, article
from app.core.database import check_mongodb_health
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    await check_mongodb_health()
    yield

app = FastAPI(lifespan=lifespan)

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
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
app.include_router(agent.router, prefix="/api/agent", tags=["Agent"])
app.include_router(article.router, prefix="/api/article", tags=["Article"])
app.include_router(storage.router, prefix="/api/storage", tags=["Storage"])

@app.get("/api/ping")
def ping():
    return {"message": "Pong from Aiven!"}
