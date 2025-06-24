import logging
from pydantic import BaseModel
from models.task import Task
from services.client import GraphClient
from msgraph import GraphServiceClient
from msgraph.generated.models.planner_task import PlannerTask
from msgraph.generated.models.planner_assignments import PlannerAssignments
from msgraph.generated.models.planner_task_details import PlannerTaskDetails
from kiota_abstractions.base_request_configuration import RequestConfiguration
from msgraph.generated.models.planner_applied_categories import PlannerAppliedCategories



logger = logging.getLogger(__name__)


class PlannerService:
    def __init__(self, graph_client: GraphClient):
        self.graph_client: GraphServiceClient = graph_client


    async def create_plan_task(self, plan_task: Task, group_id: str):

        labels = {}
        for label in plan_task.labels:
            labels[label] = True

        try:

            plan = await self.get_backlog_plan_by_group_id(group_id)
            plan_id = plan["id"]

            bucket = await self.get_bucket_id_by_plan_id(plan_id)
            bucket_id = bucket["id"]

            user = await self.get_user_id_by_email(plan_task.responsible_email)

            task = PlannerTask(
                plan_id=plan_id,
                bucket_id=bucket_id,
                title=plan_task.title,
                applied_categories= PlannerAppliedCategories(
                    additional_data=labels
                ),
                assignments=PlannerAssignments(
                    additional_data={
                        user.id: {
                            "@odata.type": "microsoft.graph.plannerAssignment", 
                            "orderHint": " !"
                        },

                    }
                )
            )

            plan_task_created = await self.graph_client.planner.tasks.post(body=task)

            if plan_task_created and plan_task.description:
                await self.insert_details_in_task(plan_task_created.id, plan_task)

            return plan_task_created
        
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Erro ao salvar task: {error_msg}")
            if "404" in error_msg:
                logger.error(f"Grupo {group_id} não encontrado ou sem Planner habilitado")
            raise

    
    async def get_backlog_plan_by_group_id(self, group_id: str):

        try:
            plans = await self.graph_client.groups.by_group_id(group_id).planner.plans.get()

            plans_data = []
            if hasattr(plans, 'value'):

                for plan in plans.value:
                    created_by_info = {}
                    if hasattr(plan.created_by, 'user') and plan.created_by.user:
                        created_by_info = {
                            "user_id": plan.created_by.user.id,
                            "display_name": plan.created_by.user.display_name
                        }
                    elif hasattr(plan.created_by, 'application') and plan.created_by.application:
                        created_by_info = {
                            "application_id": plan.created_by.application.id,
                            "display_name": plan.created_by.application.display_name
                        }
                    
                    plan_info = {
                        "id": plan.id,
                        "title": plan.title,
                        "description": getattr(plan, 'description', None),
                        "created_by": created_by_info,
                        "created_datetime": getattr(plan, 'created_date_time', None),
                        "owner": getattr(plan, 'owner', None),
                        "container": {
                            "container_id": plan.container.container_id,
                            "type": str(plan.container.type),
                            "url": getattr(plan.container, 'url', None)
                        } if hasattr(plan, 'container') and plan.container else None
                    }

                    plans_data.append(plan_info)

            return plans_data[0]
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Erro ao buscar plans para grupo {group_id}: {error_msg}")

            if "404" in error_msg:
                logger.error(f"Grupo {group_id} não encontrado ou sem Planner habilitado")
            raise
        

    async def get_bucket_id_by_plan_id(self, plan_id: str):
        try:
            plan_buckets = await self.graph_client.planner.plans.by_planner_plan_id(plan_id).buckets.get()

            if hasattr(plan_buckets, 'value') and plan_buckets.value:

                return {
                    "id": plan_buckets.value[0].id,
                }
            else:
                logger.warning(f"Nenhum bucket encontrado para o plan {plan_id}")
                return None

        except Exception as e:
            error_msg = str(e)
            logger.error(f"Erro ao buscar buckets para plan {plan_id}: {error_msg}")
            
            if "404" in error_msg:
                logger.error(f"Buckets para plan {plan_id} não encontrado")
            raise
        

    async def insert_details_in_task(self, task_id: str, plan_task: Task):
        try:
            
            details = f"Cliente: {plan_task.client}"
            details += f"\nContrato: {plan_task.contract}"
            details += f"\nSolicitante: {plan_task.requester_email}"
            details += f"\n\nDescrição: {plan_task.description}"
            
            updated_details = PlannerTaskDetails()
            updated_details.description = details

            details_etag = await self.get_task_details_etag(task_id)

            request_configuration = RequestConfiguration()
            request_configuration.headers.add("If-Match", details_etag)

            await self.graph_client.planner.tasks.by_planner_task_id(task_id).details.patch(
                updated_details, 
                request_configuration=request_configuration
            )
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Erro ao inserir detalhes na task {task_id}: {error_msg}")
            
            if "400" in error_msg and "format of value" in error_msg.lower():
                logger.error(f"Formato de ETag inválido para task {task_id}. Verifique se o ETag está sendo obtido corretamente.")
            
            raise

    async def get_user_id_by_email(self, email: str):
        user = await self.graph_client.users.by_user_id(email).get()
        return user

    async def get_task_details_etag(self, task_id: str):
        existing_details = await self.graph_client.planner.tasks.by_planner_task_id(task_id).details.get()
        etag = existing_details.additional_data.get('@odata.etag')
        return etag