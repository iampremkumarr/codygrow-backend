from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routes import dataset, generate
from app.routes import auth as auth_router
from app.routes import user as user_router

app = FastAPI(
    title="CodyGrow Backend",
    version="2.0",
    description="FastAPI + PostgreSQL backend (Supabase-free)",
)

# -------- CORS Middleware --------
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------- Routers --------
app.include_router(dataset.router, prefix="/api")
app.include_router(generate.router, prefix="/api")
app.include_router(auth_router.router, prefix="/api")
app.include_router(user_router.router, prefix="/api")

# -------- Static Files Serving --------
from fastapi.staticfiles import StaticFiles
import os

# Ensure the output directory exists
os.makedirs("generated/outputs", exist_ok=True)
# Mount only the outputs directory securely under the exact nested route expected by frontend
app.mount("/api/outputs/generated/outputs", StaticFiles(directory="generated/outputs"), name="outputs")


@app.get("/")
def root():
    return {"message": "🚀 CodyGrow Backend is running (PostgreSQL mode)!"}


@app.get("/health")
def health():
    return {"status": "ok"}
