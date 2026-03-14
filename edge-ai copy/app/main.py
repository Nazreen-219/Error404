from fastapi import FastAPI

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

app.include_router(router)

@app.get("/")
def root():
    return {"message": "CSC Edge AI running"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
