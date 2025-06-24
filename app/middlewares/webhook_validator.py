from fastapi import Request, HTTPException
import logging

from fastapi.responses import PlainTextResponse
from config import CLIENT_SECRET_STATE
from models.webhook import NotificationPayload

logger = logging.getLogger(__name__)

async def validate_graph_request(request: Request):
    """
    Dependencia que valida webhook do Microsoft Graph
    """
    # 1. Validação da subscription (usada quando esta criando a subscription apenas)
    validation_token = request.query_params.get("validationToken")

    if validation_token:
        return PlainTextResponse(content=validation_token, status_code=200)
    
    # 2. Validação do payload para notificações reais
    try:
        payload = await request.json()

        logger.info("Recebida notificação do webhook")
        
        notification = NotificationPayload(**payload)
        
        # Valida clientState, o mesmo passado no momento da criaçao da subscription
        for item in notification.value:
            if item.clientState != CLIENT_SECRET_STATE:
                raise HTTPException(status_code=400, detail="ClientState inválido")
            
        
        return {
            "payload": payload
        }
        
    except Exception as e:
        logger.error(f"Erro ao validar webhook: {e}")
        raise HTTPException(status_code=400, detail="Payload inválido")
