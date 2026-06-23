from fastapi import FastAPI
from dotenv import load_dotenv
import os

# Load the .env file from the root directory
load_dotenv(dotenv_path="../.env")

app = FastAPI(title="Multi-Agent SaaS API")

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Multi-Agent SaaS API is running!"}
