from typing import List, Optional
from pydantic import BaseModel, Field

class EncryptedContent(BaseModel):
    data: str
    dataKey: str
    dataSignature: str
    encryptionCertificateId: str
    encryptionCertificateThumbprint: str

class ResourceData(BaseModel):
    odata_type: Optional[str] = Field(default=None, alias="odata.type")
    odata_id: Optional[str] = Field(default=None, alias="odata.id")
    id: Optional[str] = None

class NotificationItem(BaseModel):
    subscriptionId: str
    changeType: str
    clientState: str
    resource: str
    resourceData: Optional[ResourceData] = None
    tenantId: Optional[str] = None
    encryptedContent: Optional[EncryptedContent] = None

class NotificationPayload(BaseModel):
    value: List[NotificationItem] 