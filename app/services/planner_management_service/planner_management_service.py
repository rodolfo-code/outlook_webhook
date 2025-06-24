from fastapi import Depends, HTTPException
from pydantic import BaseModel
from msgraph.generated.models.planner_task import PlannerTask
from models.task import Task
from services.planner_management_service.planner_service import PlannerService
from services.planner_management_service.group_service import GroupService
from services.client import GraphClient
import logging

logger = logging.getLogger(__name__)


class PlannerManagementService:
    def __init__(self, graph_client: GraphClient = Depends(GraphClient)):
        self.graph_client = graph_client.client
        self.group_service = GroupService(self.graph_client)
        self.planner_service = PlannerService(self.graph_client)

    
    async def insert_task(self, task: Task):
        response = await self._manage_planner(task)
        return response


    async def _manage_planner(self, task: Task):
        group_id = await self.group_service.get_squad_group_id_by_email(task.responsible_email)

        plan_task_created = await self.planner_service.create_plan_task(task, group_id)

        return plan_task_created


            