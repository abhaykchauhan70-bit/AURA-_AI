from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import Base, engine
from . import routes

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AURA API")

# CORS FIX - Final working version
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all API routes
app.include_router(routes.router)

@app.get("/")
def read_root():
    return {"status": "AURA Backend Running"}

@app.get("/health")
def health():
    return {"status": "ok", "port": 8000}
