from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

from api.routes import router as api_router

# Load the .env file from the root directory
load_dotenv(dotenv_path="../.env")

app = FastAPI(title="Multi-Agent SaaS API")

# Setup CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React frontend origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Router
app.include_router(api_router, prefix="")

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Multi-Agent SaaS API is running!"}
