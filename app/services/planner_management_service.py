from fastapi import Depends, HTTPException
from pydantic import BaseModel
from services.client import GraphClient
import logging

logger = logging.getLogger(__name__)


class PlannerTask(BaseModel):
    title: str
    description: str


class PlannerManagementService:
    def __init__(self, graph_client: GraphClient = Depends(GraphClient)):
        self.graph_client = graph_client.client

    def create_planner_task(self, planner_task: PlannerTask):
        pass

    def get_planner_tasks(self):
        pass

    async def list_user_groups(self, user_email: str):
        """
        Lista os grupos que o usuário participa baseado no email.
        
        Args:
            user_email: Email do usuário para buscar os grupos
            
        Returns:
            Lista de grupos que o usuário participa
        """

        try:
            logger.info(f"Buscando usuário: {user_email}")
            
            # Primeiro, buscar o usuário pelo email
            user = await self.graph_client.users.by_user_id(user_email).get()
            
            logger.info(f"Usuário encontrado: {user.id}")
            logger.info(f"Buscando grupos para usuário: {user.id}")
            
            # Depois, buscar os grupos que o usuário participa
            # Usando member_of para obter grupos diretos e transitivos
            groups_response = await self.graph_client.users.by_user_id(user.id).member_of.get()
            
            # Extrair os dados dos grupos
            groups_data = []
            if hasattr(groups_response, 'value'):
                for group in groups_response.value:
                    group_info = {
                        "id": group.id,
                        "display_name": group.display_name,
                        "description": getattr(group, 'description', None),
                        "mail": getattr(group, 'mail', None),
                        "group_types": getattr(group, 'group_types', []),
                        "visibility": getattr(group, 'visibility', None)
                    }
                    groups_data.append(group_info)
            
            logger.info(f"Grupos encontrados: {len(groups_data)}")
            return groups_data
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Erro ao buscar grupos para {user_email}: {error_msg}")
            
            # Verificar se é erro de permissão
            if "Authorization_RequestDenied" in error_msg or "403" in error_msg:
                raise HTTPException(
                    status_code=403, 
                    detail="Permissões insuficientes. Verifique se as permissões foram configuradas no Azure AD: User.Read.All, Group.Read.All, GroupMember.Read.All, Directory.Read.All"
                )
            elif "404" in error_msg or "not found" in error_msg.lower():
                raise HTTPException(
                    status_code=404,
                    detail=f"Usuário com email {user_email} não encontrado"
                )
            else:
                raise HTTPException(status_code=500, detail=f"Erro ao buscar grupos: {error_msg}") 