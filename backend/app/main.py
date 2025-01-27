from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api import chat, ingest
from app.core.settings import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=getattr(settings, 'VERSION', '1.0.0'),  # Default to 1.0.0 if not set
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers with API version prefix
app.include_router(chat.router, prefix=settings.API_V1_STR, tags=["chat"])
app.include_router(ingest.router, prefix=settings.API_V1_STR, tags=["ingest"])

@app.get("/")
async def root():
    return {"message": "Welcome to RAG Chatbot API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}