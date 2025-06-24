import logging
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from fastapi.responses import PlainTextResponse
from datetime import datetime
from config import CLIENT_SECRET_STATE
from middlewares.webhook_validator import validate_graph_request
from services.email_service import EmailService
from services.external_service import ExternalService
from services.notification_processor import process_notification_async
from utils.functions import save_request_to_json

router = APIRouter()

logger = logging.getLogger(__name__)

@router.post("/notification")
async def notification_webhook(
        request: Request,
        background_tasks: BackgroundTasks,
        validated_request: dict = Depends(validate_graph_request),
        graph_api: EmailService = Depends(EmailService),
        external_service: ExternalService = Depends(ExternalService)
    ):
    
    try:
        validation_token = request.query_params.get("validationToken")

        if validation_token:
            return PlainTextResponse(content=validation_token, status_code=200)
        
        payload = validated_request["payload"]

        request_data = {
            "headers": dict(request.headers),
            "body": payload,
            "timestamp": datetime.now().isoformat()
        }

        save_request_to_json(request_data, "notification")

        background_tasks.add_task(
            process_notification_async,
            payload,
            graph_api,
            external_service
        )


        # email_data = await graph_api.get_email_data(payload)

        # save_request_to_json(email_data, "email")

        # await external_service.send_email(email_data)
 
        return PlainTextResponse(status_code=202)

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Erro ao processar notificação: %s", str(e))
        raise HTTPException(
            status_code=500,
            detail="Erro interno do servidor ao processar notificação"
        )
    
    