import logging
import asyncio
from services.email_service import EmailService
from services.external_service import ExternalService
from utils.functions import save_request_to_json

logger = logging.getLogger(__name__)

async def process_notification_async(
    payload: dict,
    graph_api: EmailService,
    external_service: ExternalService
):

    async def async_task():
        try:
            email_data = await graph_api.get_email_data(payload)
            
            save_request_to_json(email_data, "email")

            await external_service.send_email(email_data)
        except Exception as e:
            logger.error("Erro no processamento assíncrono: %s", str(e))

    asyncio.create_task(async_task()) 