if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:http_server", host="0.0.0.0", port=8000, reload=True)

# Import at module level for uvicorn
from src.app_module import http_server


