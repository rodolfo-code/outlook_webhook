import logging
from datetime import datetime, timedelta
from msgraph import GraphServiceClient
from datetime import datetime, timedelta, timezone 
from azure.identity.aio import ClientSecretCredential
from msgraph.generated.models.subscription import Subscription
from app.config import CLIENT_SECRET_STATE, ENCRYPTION_CERTIFICATE, ENCRYPTION_CERTIFICATE_ID, TENANT_ID, CLIENT_ID, CLIENT_SECRET, GRAPH_API_ENDPOINT, GRAPH_API_SCOPE, SUBSCRIPTION_EXPIRATION_DAYS, WEBHOOK_LIFECYCLE_ENDPOINT, WEBHOOK_NOTIFICATION_ENDPOINT
from app.models.email import Email
from app.utils.normalize_email_data import normalize_email_data

class GraphAPI:
    def __init__(self):
        self.client: GraphServiceClient
        self.initialize_graph_client()

    def initialize_graph_client(self):
        """
        Inicializa o cliente do Microsoft Graph API.
        """

        try:
            logging.info("Criando credenciais usando Azure Identity...")

            credentials = ClientSecretCredential(
                tenant_id=TENANT_ID,
                client_id=CLIENT_ID,
                client_secret=CLIENT_SECRET
            )
            
            # Inicializa o cliente Graph
            self.client = GraphServiceClient(credentials=credentials)

            logging.info("Cliente do Microsoft Graph API inicializado com sucesso.")

        except Exception as e:
            logging.error(f"Erro ao inicializar cliente do Microsoft Graph Client: {e}")
            raise

            # ?$select=subject,body,receivedDateTime,from"
    async def create_subscription(self, 
                    resource: str,
                    change_type: str = "created"
                ):
        """
        Cria uma assinatura (webhook) para receber notificações quando novos e-mails chegarem.

        Args: 
            resource: O recurso a ser monitorado (por padrão, mensagens do usuário)
            change_type: O tipo de mudança a ser monitorado (created, updated, deleted)

        Returns:
            dict: Os detalhes da assinatura criada
        """

        # Link para documentaçao https://learn.microsoft.com/en-us/graph/api/resources/subscription?view=graph-rest-1.0

        try:
            # Data de expiração (máximo de 3 dias)
            expiration_date = datetime.now(timezone.utc) + timedelta(days=SUBSCRIPTION_EXPIRATION_DAYS)
            expiration_string = expiration_date.isoformat(timespec='seconds').replace('+00:00', 'Z')

            subscription = Subscription()

            # Tipo de alteração que acionará a notificação do webhook (creatred, updated, deleted).
            subscription.change_type = change_type

            # A URL HTTPS para onde o Microsoft Graph enviará as notificações de eventos.            
            subscription.notification_url = "https://04a1-89-181-155-219.ngrok-free.app/webhook/notification"
            # subscription.notification_url = WEBHOOK_NOTIFICATION_ENDPOINT

            # URL opcional para onde o Microsoft Graph enviará notificações sobre o ciclo de vida da subscription.
            # Ex: Notificações de expiração iminente, problemas de validação, etc.
            # subscription.lifecycle_notification_url = WEBHOOK_LIFECYCLE_ENDPOINT

            # O recurso do Microsoft Graph a ser monitorado para alterações em algum recurso.

            # subscription.resource = f"{resource}?$select=Subject,bodyPreview,importance,receivedDateTime,from,toRecipients,ccRecipients,bccRecipients,hasAttachments,conversationId,conversationIndex,isRead,parentFolderId,receivedDateTime,replyTo,internetMessageId,Id"
            subscription.resource = resource
            

            # A data e hora em que a subscription irá expirar, no formato ISO 8601 (com 'Z' para UTC).
            subscription.expiration_date_time = expiration_string

            # Uma string de estado gerada pelo cliente que será incluída em cada notificação.
            # Essencial para verificar a autenticidade da notificação no seu endpoint de webhook.
            subscription.client_state = CLIENT_SECRET_STATE
            subscription.latest_supported_tls_version = "v1_2"

            subscription.include_resource_data = False
            # subscription.encryption_certificate = ENCRYPTION_CERTIFICATE
            # subscription.encryption_certificate_id = ENCRYPTION_CERTIFICATE_ID
            
            logging.info("Criando subscription...")

            response = await self.client.subscriptions.post(subscription)

            logging.info("Subscription criada com sucesso.")
            return response
                        
        except Exception as e:
            logging.error(f"Erro ao criar subscription: {e}")
            raise


    async def list_subscriptions(self):
            """
            Lista todas as subscriptions ativas.
            """
            try:
                logging.info("Listando subscriptions...")
                subscriptions = await self.client.subscriptions.get()
                logging.info(f"Subscriptions encontradas: {len(subscriptions.value)}")
                return subscriptions.value
            except Exception as e:
                logging.error(f"Erro ao listar subscriptions: {e}")
                raise

    async def delete_subscription(self, subscription_id: str):
        """
        Deleta uma subscription específica.
        
        Args:
            subscription_id: ID da subscription a ser deletada
        """
        try:
            logging.info(f"Deletando subscription {subscription_id}...")
            await self.client.subscriptions.by_subscription_id(subscription_id).delete()
            logging.info(f"Subscription {subscription_id} deletada com sucesso.")
            return True
        except Exception as e:
            logging.error(f"Erro ao deletar subscription {subscription_id}: {e}")
            raise


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
            logging.info(f"Obtendo dados da mensagem de e-mail {user_id} {message_id}...")

            email_data = await self.client.users.by_user_id(user_id).messages.by_message_id(message_id).get()

            logging.info(f"Dados da mensagem de e-mail obtidos com sucesso.")
            
            return normalize_email_data(email_data)
        except Exception as e:
            logging.error(f"Erro ao obter dados da mensagem de e-mail {user_id} {message_id}: {e}")
            raise

