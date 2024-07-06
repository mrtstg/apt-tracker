import uvicorn
from .server import app
import logging

logging.basicConfig(level=logging.ERROR)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3000)
