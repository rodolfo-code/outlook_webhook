import logging

from fastapi import Depends
from services.client import GraphClient
from utils.normalize_email_data import normalize_email_data

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self, graph_client: GraphClient = Depends(GraphClient)):
        self.client = graph_client.client

    async def get_email_data(self, payload: dict) -> dict: 
        """
        Obtém os dados de uma mensagem de e-mail específica.
        
        Args:
            resource: O recurso da mensagem de e-mail a ser obtido
        """

        resource = payload.get("value")[0].get("resource").split("/")
        user_id = resource[1]
        message_id = resource[3]
        
        try:
            logger.info(f"Obtendo dados da mensagem de e-mail {user_id} {message_id}...")

            email_data = await self.client.users.by_user_id(user_id).messages.by_message_id(message_id).get()

            logger.info(f"Dados da mensagem de e-mail obtidos com sucesso.")
            
            return normalize_email_data(email_data)
        except Exception as e:
            logger.error(f"Erro ao obter dados da mensagem de e-mail {user_id} {message_id}: {e}")
            raise
