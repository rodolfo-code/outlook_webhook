import os
from dotenv import load_dotenv

load_dotenv()

# Azure AD Credentials
CLIENT_ID = os.getenv("CLIENT_ID")
TENANT_ID = os.getenv("TENANT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

WEBHOOK_BASE_URL = os.getenv("WEBHOOK_BASE_URL")

def build_webhook_url(path: str) -> str:
    base_url = WEBHOOK_BASE_URL.rstrip('/')
    path = path.lstrip('/')
    return f"{base_url}/{path}"

WEBHOOK_NOTIFICATION_ENDPOINT = build_webhook_url(os.getenv("WEBHOOK_NOTIFICATION"))
WEBHOOK_LIFECYCLE_ENDPOINT = build_webhook_url(os.getenv("WEBHOOK_LIFECYCLE"))

ENCRYPTION_CERTIFICATE = os.getenv("ENCRYPTION_CERTIFICATE")
ENCRYPTION_CERTIFICATE_ID = os.getenv("ENCRYPTION_CERTIFICATE_ID")

# Microsoft Graph API Endpoints
GRAPH_API_ENDPOINT = "https://graph.microsoft.com/v1.0"
GRAPH_API_SCOPE = ["https://graph.microsoft.com/.default", "User.Read", "Mail.ReadBasic", "Mail.Read", "Mail.Send", "Mail.Send.Shared"]

# Subscription Configuration
SUBSCRIPTION_EXPIRATION_DAYS = 3

# Converte a string da chave privada para bytes usando bytes()
PRIVATE_KEY = bytes(os.getenv("PRIVATE_KEY"), 'utf-8') if os.getenv("PRIVATE_KEY") else None
CLIENT_SECRET_STATE = os.getenv("CLIENT_SECRET_STATE")
