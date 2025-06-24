from pydantic import BaseModel


class Task(BaseModel):
    title: str
    description: str
    client: str
    contract: str
    responsible_email: str
    requester_email: str
    labels: list[str]