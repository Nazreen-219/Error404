from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

try:
    from app.router import router
except ModuleNotFoundError:
    # Allows running this file directly: `python app/main.py`
    from router import router

app = FastAPI(
    title="CSC Edge AI Assistant",
    description="Edge AI module for CSC operator support",
    version="1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.get("/")
def root():
    return {"message": "CSC Edge AI running"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
