from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

@dataclass
class EmailAddress:
    name: str
    address: str

@dataclass
class EmailBody:
    content: str
    content_type: str  # "html" ou "text"

@dataclass
class Email:
    id: str
    subject: str
    from_: EmailAddress
    to_recipients: List[EmailAddress] = field(default_factory=list)
    body: EmailBody = None
    received_date_time: datetime = None
    sent_date_time: datetime = None
    is_read: bool = False
    has_attachments: bool = False

    def to_dict(self):
        return {
            "id": self.id,
            "subject": self.subject,
            "from": {
                "name": self.from_.name,
                "address": self.from_.address
            },
            "to": [{
                "name": recipient.name,
                "address": recipient.address
            } for recipient in self.to_recipients],
            "body": {
                "content": self.body.content,
                "content_type": self.body.content_type
            },
            "received_date_time": self.received_date_time.isoformat() if self.received_date_time else None,
            "sent_date_time": self.sent_date_time.isoformat() if self.sent_date_time else None,
            "is_read": self.is_read,
            "has_attachments": self.has_attachments
        }

    @classmethod
    def from_graph_data(cls, email_data):
        """Cria um objeto Email a partir dos dados retornados pelo Microsoft Graph API"""
        from_address = EmailAddress(
            name=email_data.from_.email_address.name,
            address=email_data.from_.email_address.address
        )

        to_recipients = [
            EmailAddress(
                name=recipient.email_address.name,
                address=recipient.email_address.address
            ) for recipient in email_data.to_recipients
        ]

        body = EmailBody(
            content=email_data.body.content,
            content_type=email_data.body.content_type.value
        )

        return cls(
            id=email_data.id,
            subject=email_data.subject,
            from_=from_address,
            to_recipients=to_recipients,
            body=body,
            received_date_time=email_data.received_date_time,
            sent_date_time=email_data.sent_date_time,
            is_read=email_data.is_read,
            has_attachments=email_data.has_attachments
        )