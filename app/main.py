import logging
from typing import Optional
import asyncio
from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.responses import PlainTextResponse
from app.graph import GraphAPI
from app.webhook import router as webhook_router

# Configuração de logging
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

@app.get("/webhook/")
async def root():
    """Endpoint raiz para verificar se a API está funcionando."""

    return {"status": "API is running", "message": "Welcome to Microsoft Graph Webhook API"}

@app.post("/webhook/create-subscription")
async def create_subscription(request: Request, graph_api: GraphAPI = Depends(GraphAPI)):
    """Endpoint para criar uma nova subscription."""

    resource = await request.json()
    
    try:
        subscription = await graph_api.create_subscription(resource=f"{resource.get('resource')}")
        if subscription:
            return {
                "status": "success",
                "message": "Subscription created successfully",
                "subscription": subscription
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to create subscription")
        
    except Exception as e:
        logging.error(f"Error creating subscription: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/webhook/subscriptions/{subscription_id}")
async def delete_subscription(subscription_id: str, graph_api: GraphAPI = Depends(GraphAPI)):
    """Endpoint para deletar uma subscription específica."""
    try:
        await graph_api.delete_subscription(subscription_id)
        return {
            "status": "success",
            "message": f"Subscription {subscription_id} deletada com sucesso"
        }
    except Exception as e:
        logging.error(f"Erro ao deletar subscription: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=3000, reload=True)
