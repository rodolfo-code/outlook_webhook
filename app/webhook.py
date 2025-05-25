import logging
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import PlainTextResponse
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from datetime import datetime
from app.config import CLIENT_SECRET_STATE
from app.graph import GraphAPI
from app.utils.functions import save_request_to_json
from app.models.webhook import NotificationPayload

router = APIRouter()

logger = logging.getLogger(__name__)

@router.post("/notification")
async def notification_webhook(request: Request, graph_api: GraphAPI = Depends(GraphAPI)):
    try:        
        # Validação da subscription (so usada quando esta criando a subscription)
        validation_token: Optional[str] = request.query_params.get("validationToken")
        if validation_token:
            logger.info(f"Recebida requisição de validação com token: {validation_token}")
            return PlainTextResponse(content=validation_token, status_code=200)

        # Log da notificação real
        logger.info("Recebida notificação do webhook")

        # Lê e valida o JSON recebido
        payload = await request.json()
        
        logger.debug("Payload recebido: %s", payload)

        # Salva os dados da requisição
        request_data = {
            "headers": dict(request.headers),
            "query_params": dict(request.query_params),
            "body": payload,
            "timestamp": datetime.now().isoformat()
        }

        save_request_to_json(request_data, "notification")

        email_data = await graph_api.get_email_data(payload)

        # Salva os dados do email em um arquivo JSON
        save_request_to_json(email_data, "email_data")

        notification = NotificationPayload(**payload)
        for item in notification.value:
            if item.clientState != CLIENT_SECRET_STATE:
                logger.warning("ClientState inválido: %s", item.clientState)
                raise HTTPException(status_code=400, detail="ClientState inválido")
            
        # Responde com 202 Accepted para notificações reais
        return Response(status_code=200)

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Erro ao processar notificação: %s", str(e))
        raise HTTPException(
            status_code=500,
            detail="Erro interno do servidor ao processar notificação"
        )
    
    