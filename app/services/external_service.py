import httpx
import logging
from config import EXTERNAL_API_URL


logger = logging.getLogger(__name__)

class ExternalService:
    """
    Classe para enviar requisições para a API externa (agente)
    """

    def __init__(self):
        self.client = httpx.AsyncClient()
        self.base_url = EXTERNAL_API_URL

    async def send_email(self, payload: dict):

        # endpoint = f"{self.base_url}/graph-microsoft"
        endpoint = EXTERNAL_API_URL
        try:
            response = await self.client.post(
                endpoint,
                json=payload
            )

            response.raise_for_status()
            logger.info(f"Notificação enviada com sucesso para {self.base_url}")
            return True
        
        except httpx.HTTPError as e:
            logger.error(f"Erro ao enviar notificação: {str(e)}")
            return False
