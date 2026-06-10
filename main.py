import uvicorn
from fastapi import FastAPI

import requests

from structlog import get_logger

logger = get_logger()

app = FastAPI()

@app.get("/republishschema/{questionnaireVersionId}/cirversion/{cirVersion}")
async def root(questionnaireVersionId: int, cirVersion: int):
    url = "http://0.0.0.0:3030/status"
    response = requests.get(url, timeout=10000)
    if response.status_code == 200:
        logger.info("OK: status 200")
    return {"success": True}

if __name__ == "__main__":
 uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
