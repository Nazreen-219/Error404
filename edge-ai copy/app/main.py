from pathlib import Path
import sys

from fastapi import FastAPI

if __package__ in (None, ""):
    sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.router import router

app = FastAPI(
    title="CSC Edge AI Assistant",
    description="Edge AI module for CSC operator support",
    version="1.0"
)

app.include_router(router)

@app.get("/")
def root():
    return {"message": "CSC Edge AI running"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
