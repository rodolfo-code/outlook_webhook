from typing import List
import logging

from fastapi import Depends

from services.client import GraphClient
from msgraph import GraphServiceClient

logger = logging.getLogger(__name__)

class GroupService:

    def __init__(self, graph_client: GraphClient):
        self.graph_client: GraphServiceClient = graph_client

    async def get_squad_group_id_by_email(self, user_email: str) -> str:
        group = await self.list_user_groups(user_email)
        squad_group_id = group[0]['id']

        return squad_group_id

    async def list_user_groups(self, user_email: str) -> List[dict]:
        """
        Lista os grupos que o usuário participa baseado no email.
        """

        try:
            user = await self.graph_client.users.by_user_id(user_email).get()
            
            # Depois, buscar os grupos que o usuário participa
            # Usando member_of para obter grupos
            groups_response = await self.graph_client.users.by_user_id(user.id).member_of.get()
            
            groups_data = []
            if hasattr(groups_response, 'value'):
                for group in groups_response.value:
                    if "squad" in group.display_name.lower():
                        group_info = {
                            "id": group.id,
                            "display_name": group.display_name,
                            "description": getattr(group, 'description', None),
                            "mail": getattr(group, 'mail', None),
                            "group_types": getattr(group, 'group_types', []),
                            "visibility": getattr(group, 'visibility', None)
                        }

                        groups_data.append(group_info)
            
            return groups_data
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Erro ao buscar grupos para {user_email}: {error_msg}")
            
