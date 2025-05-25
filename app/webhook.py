import logging
from fastapi import APIRouter, HTTPException, Request, Response
from fastapi.responses import PlainTextResponse
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from datetime import datetime
from app.config import WEBHOOK_LIFECYCLE_ENDPOINT, WEBHOOK_NOTIFICATION_ENDPOINT
from app.graph import GraphAPI

router = APIRouter()

logger = logging.getLogger(__name__)

# Modelos Pydantic para validação do payload
class ResourceData(BaseModel):
    odata_type: str = None
    odata_id: str = None
    id: str = None

class NotificationItem(BaseModel):
    subscription_id: str
    change_type: str
    client_state: str
    resource: str
    resource_data: ResourceData
    tenant_id: str

class NotificationPayload(BaseModel):
    value: List[NotificationItem]


@router.post("/notification")
async def notification_webhook(request: Request):
    try:
        # Validação da subscription
        validation_token: Optional[str] = request.query_params.get("validationToken")
        if validation_token:
            logger.info(f"Recebida requisição de validação com token: {validation_token}")
            return PlainTextResponse(content=validation_token, status_code=200)

        # Log da notificação real
        logger.info("Recebida notificação do webhook")
        logger.debug("Headers: %s", dict(request.headers))

        # Lê e valida o JSON recebido
        payload = await request.json()
        logger.debug("Payload recebido: %s", payload)

        notification = NotificationPayload(**payload)

        for item in notification.value:
            if item.client_state != "secretClientState":
                logger.warning("ClientState inválido: %s", item.client_state)
                raise HTTPException(status_code=400, detail="ClientState inválido")

            logger.info(
                "Processando notificação - Subscription: %s, ChangeType: %s, Resource: %s",
                item.subscription_id,
                item.change_type,
                item.resource
            )

            client = GraphAPI()

            if item.change_type == "created":
                await client.create_subscription()

        # Responde com 202 Accepted para notificações reais
        return Response(status_code=202)

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Erro ao processar notificação: %s", str(e))
        raise HTTPException(
            status_code=500,
            detail="Erro interno do servidor ao processar notificação"
        )
    
@router.post("/lifecycle")
async def lifecycle_webhook(request: Request):

    validation_token: Optional[str] = request.query_params.get("validationToken")
    return PlainTextResponse(content=validation_token, status_code=200)

    if validation_token:
        logger.info(f"Recebida requisição de validação com token: {validation_token}")
        return PlainTextResponse(content=validation_token, status_code=200)
    
    # Adicionar lógica para tratar eventos de ciclo de vida, como expiração
    payload = await request.json()
    logger.info(f"Lifecycle notification payload: {payload}")
    return {"status": "received"}


# @router.post("/notification")
# async def notification_webhook(request: Request):
#     """
#     Endpoint para receber notificações do Microsoft Graph API.
    
#     Este endpoint é chamado quando ocorrem eventos monitorados (novos emails, etc).
    
#     O endpoint deve:
#     1. Validar o clientState
#     2. Processar a notificação
#     3. Responder rapidamente (dentro de 30 segundos)
    
#     Args:
#         request (Request): Objeto de requisição do FastAPI
        
#     Returns:
#         Response: Resposta 202 Accepted
        
#     Raises:
#         HTTPException: Se a notificação for inválida
#     """
#     try:
#         # Verifica se é uma requisição de validação
#         validation_token: Optional[str] = request.query_params.get("validationToken")
#         if validation_token:
#             logger.info(f"Recebida requisição de validação com token: {validation_token}")
#             return Response(
#                 status_code=200,
#                 content=validation_token,
#                 # media_type="text/plain",
#                 # headers={
#                 #     "Content-Type": "text/plain",
#                 # }
#             )

#         # Log da requisição recebida
#         logger.info("Recebida notificação do webhook")
#         logger.debug("Headers: %s", dict(request.headers))
        
#         # Lê o corpo da requisição
#         payload = await request.json()
#         logger.debug("Payload recebido: %s", payload)
        
#         # Valida o payload usando Pydantic
#         notification = NotificationPayload(**payload)
        
#         # Processa cada item da notificação
#         for item in notification.value:
#             # Valida o clientState
#             if item.client_state != "secretClientState":
#                 logger.warning("ClientState inválido: %s", item.client_state)
#                 raise HTTPException(
#                     status_code=400,
#                     detail="ClientState inválido"
#                 )
            
#             # Log dos detalhes da notificação
#             logger.info(
#                 "Processando notificação - Subscription: %s, ChangeType: %s, Resource: %s",
#                 item.subscription_id,
#                 item.change_type,
#                 item.resource
#             )
            
#             # Inicializa o cliente Graph
#             client = GraphAPI()
            
#             # Processa baseado no tipo de mudança
#             if item.change_type == "created":
#                 await client.create_subscription()
#             # elif item.change_type == "updated":
#             #     await process_updated_notification(item)
#             # elif item.change_type == "deleted":
#             #     await process_deleted_notification(item)
#             # else:
#             #     logger.warning("Tipo de mudança desconhecido: %s", item.change_type)
        
#         # Responde com 202 Accepted
#         return Response(
#             status_code=200,
#             content=validation_token,
#             media_type="text/plain"
#         )
        
#     except HTTPException:
#         raise
        
#     except Exception as e:
#         logger.error("Erro ao processar notificação: %s", str(e))
#         raise HTTPException(
#             status_code=500,
#             detail="Erro interno do servidor ao processar notificação"
#         )

@router.get("/validate")
async def validate_webhook(request: Request):
    """
    Endpoint para validação do webhook pela Microsoft Graph API.
    
    Este endpoint é chamado pela Microsoft Graph API em dois cenários:
    1. Quando uma nova subscription é criada
    2. Periodicamente para verificar se o webhook ainda está ativo
    
    Args:
        request (Request): Objeto de requisição do FastAPI
        
    Returns:
        Response: Resposta com o token de validação
        
    Raises:
        HTTPException: Se o token não for fornecido ou for inválido
    """
   
    try:
        validation_token: Optional[str] = request.query_params.get("validationToken")
        
        logger.info("Recebida requisição de validação do webhook")
        logger.debug("Headers: %s", dict(request.headers))
        
        if not validation_token:
            logger.warning("Token de validação não fornecido na requisição")
            raise HTTPException(
                status_code=400,
                detail="Token de validação não fornecido"
            )
            
        logger.info("Token de validação recebido: %s", validation_token)
        
        # Responde com o token no formato correto
        return Response(
            status_code=200,
            content=validation_token,
            media_type="text/plain",
            headers={
                "Content-Type": "text/plain",
            }
        )
        
    except HTTPException:
        logger.warning("No validation token provided in the request")
        raise HTTPException(status_code=400, detail="Validation token not found")
    

# @router.get("/webhook/resourceNotifications")
# async def resource_notifications(request: Request):
