import logging
from fastapi import Depends, FastAPI, HTTPException, Response
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
async def create_subscription(graph_api: GraphAPI = Depends(GraphAPI)):
    """Endpoint para criar uma nova subscription."""
    
    try:
        subscription = await graph_api.create_subscription()
        if subscription:
            print("Subscription created successfully", subscription)
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=3000, reload=True)
