import logging
from fastapi import APIRouter, Depends, HTTPException
from models.task import Task
from services.planner_management_service.planner_management_service import PlannerManagementService
# from app.services.planner_management_service.planner_management_service import PlannerManagementService

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/planner/task")
async def create_task(
    task: Task,
    planner_service: PlannerManagementService = Depends(PlannerManagementService)
):
    try:
        created_task_resopnse = await planner_service.insert_task(task)

        return {
            "created_task": created_task_resopnse
        }
    
    except Exception as e:
        logger.error(f"Erro ao criar tarefa: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno do servidor ao criar tarefa: {str(e)}"
        ) 



@router.get("/planner")
async def get_user_groups(
    planner_service: PlannerManagementService = Depends(PlannerManagementService)
):
    
    task = Task(
        title="Criar webpart de noticias",
        description="Usuario solicitou a inclusao de novas colunas de dados no download de excel para o cliente Vale do formulario de solicitação de serviço F",
        client="Vale",
        contract="Integridade - DDP",
        responsible_email="AlexW@w7drx.onmicrosoft.com",
        requester_email="requester@email.com"
    )

    try:        
        created_task_resopnse = await planner_service.insert_task(task)
        
        return {
            "created_task": created_task_resopnse
        }
        
    except Exception as e:
        logger.error(f"Erro ao buscar grupos para {task.responsible_email}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno do servidor ao buscar grupos: {str(e)}"
        ) 