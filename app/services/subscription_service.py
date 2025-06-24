import logging

from fastapi import Depends
from services.client import GraphClient
from datetime import datetime, timedelta, timezone
from msgraph.generated.models.subscription import Subscription

from config import CLIENT_SECRET_STATE, SUBSCRIPTION_EXPIRATION_DAYS, WEBHOOK_LIFECYCLE_ENDPOINT, WEBHOOK_NOTIFICATION_ENDPOINT

logger = logging.getLogger(__name__)

class SubscriptionService:
    def __init__(self, graph_client: GraphClient = Depends(GraphClient)):
        self.client = graph_client.client

    async def create_subscription(self, resource: str, change_type: str = "created"):
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
            subscription.notification_url = WEBHOOK_NOTIFICATION_ENDPOINT
            # subscription.notification_url = "https://d72c-89-181-155-219.ngrok-free.app/webhook/notification"

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
                result = await self.client.subscriptions.get()

                subscriptions_list = []
                for subscription in result.value:
                    subscriptions_list.append(subscription.id)

                logging.info(f"Subscriptions encontradas: {len(subscriptions_list)}")
                return subscriptions_list
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