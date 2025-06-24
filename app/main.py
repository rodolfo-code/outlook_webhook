import logging
from fastapi import FastAPI
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


from api.subscription import router as webhook_router
from api.notification import router as notification_router
from api.planner import router as planner_router
from config import EXTERNAL_API_URL, WEBHOOK_NOTIFICATION_ENDPOINT 

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

app = FastAPI(
    title="Microsoft Graph Webhook API",
    description="API para receber notificações de novos e-mails via Microsoft Graph API",
    version="1.0.0"
)

app.include_router(webhook_router, prefix="/webhook")
app.include_router(notification_router, prefix="/webhook")
app.include_router(planner_router, prefix="/api")


@app.get("/webhook")
async def root():
    """Endpoint raiz para verificar se a API está funcionando."""

    print("API is running", WEBHOOK_NOTIFICATION_ENDPOINT)
    print("API is running", EXTERNAL_API_URL)

    return {
        "status": "API is running",
        "message": "Welcome to Microsoft Graph Webhook API"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=3000, reload=True)
