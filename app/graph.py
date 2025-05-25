import logging
from datetime import datetime, timedelta
from msgraph import GraphServiceClient
from datetime import datetime, timedelta, timezone 
from azure.identity.aio import ClientSecretCredential
from msgraph.generated.models.subscription import Subscription
from app.config import TENANT_ID, CLIENT_ID, CLIENT_SECRET, GRAPH_API_ENDPOINT, GRAPH_API_SCOPE, SUBSCRIPTION_EXPIRATION_DAYS, WEBHOOK_LIFECYCLE_ENDPOINT, WEBHOOK_NOTIFICATION_ENDPOINT

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


    async def create_subscription(self, 
                    resource="/users/{user-id}/mailFolders('Inbox')/messages",
                    change_type="created"
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

            # Tipo de alteração que acionará a notificação do webhook.
            # Pode ser 'created', 'updated', 'deleted' ou uma combinação separada por vírgula.
            subscription.change_type = change_type

            # A URL HTTPS para onde o Microsoft Graph enviará as notificações de eventos.
            # Esta URL deve ser publicamente acessível.
            
            # subscription.notification_url = "https://6d15-89-181-155-219.ngrok-free.app/webhook/notification"
            subscription.notification_url = WEBHOOK_NOTIFICATION_ENDPOINT

            # URL opcional para onde o Microsoft Graph enviará notificações sobre o ciclo de vida da subscription.
            # Ex: Notificações de expiração iminente, problemas de validação, etc.
            subscription.lifecycle_notification_url = WEBHOOK_LIFECYCLE_ENDPOINT

            # O recurso do Microsoft Graph a ser monitorado para alterações.
            # "/users/{user-id}/mailfolders('inbox')/messages" monitora as mensagens na caixa de entrada do usuário especificado.
            subscription.resource = resource

            # A data e hora em que a subscription irá expirar, no formato ISO 8601 (com 'Z' para UTC).
            subscription.expiration_date_time = expiration_string

            # Uma string de estado gerada pelo cliente que será incluída em cada notificação.
            # Essencial para verificar a autenticidade da notificação no seu endpoint de webhook.
            subscription.client_state = "secretClientState"
            subscription.latest_supported_tls_version = "v1_2"

            logging.info("Criando subscription...")

            response = await self.client.subscriptions.post(subscription)
            
            # Verifica se a assinatura foi criada com sucesso
            if response.status_code == 201:
                logging.info("Subscription criada com sucesso.")
                return response.json()
            else:
                logging.error(f"Failed to create subscription. Status code: {response.status_code}, Response: {response.text}")
                raise None
            
        except Exception as e:
            logging.error(f"Erro ao criar subscription: {e}")
            raise


    # def get_messages_details(self, message_id: str):
    #     """
    #     Obtém os detalhes de uma mensagem específica.
    #     """



            

        
