import logging
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from services.subscription_service import SubscriptionService

router = APIRouter()

logger = logging.getLogger(__name__)

@router.post("/create-subscription")
async def create_subscription(request: Request, graph_api: SubscriptionService = Depends(SubscriptionService)):
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


@router.delete("/subscriptions/{subscription_id}")
async def delete_subscription(subscription_id: str, graph_api: SubscriptionService = Depends(SubscriptionService)):
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


@router.get("/subscriptions")
async def list_subscriptions(graph_api: SubscriptionService = Depends(SubscriptionService)):
    """Endpoint para listar todas as subscriptions."""
    try:
        subscriptions = await graph_api.list_subscriptions()
        return {
            "status": "success",
            "message": "Subscriptions listed successfully",
            "subscriptions": subscriptions
        }
    except Exception as e:
        logging.error(f"Erro ao listar subscriptions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

