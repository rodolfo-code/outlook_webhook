import logging
from msgraph import GraphServiceClient
from azure.identity.aio import ClientSecretCredential
from config import TENANT_ID, CLIENT_ID, CLIENT_SECRET

logger = logging.getLogger(__name__)

class GraphClient:
    def __init__(self):
        self.client: GraphServiceClient
        self.initialize_graph_client()

    def initialize_graph_client(self):
        """
        Inicializa o cliente do Microsoft Graph API.
        """

        try:
            logger.info("Criando credenciais usando Azure Identity...")

            credentials = ClientSecretCredential(
                tenant_id=TENANT_ID,
                client_id=CLIENT_ID,
                client_secret=CLIENT_SECRET
            )
            
            # Inicializa o cliente Graph
            self.client = GraphServiceClient(credentials=credentials)

            logger.info("Cliente do Microsoft Graph API inicializado com sucesso.")

        except Exception as e:
            logger.error(f"Erro ao inicializar cliente do Microsoft Graph Client: {e}")
            raise
