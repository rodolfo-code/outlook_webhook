from datetime import datetime
import json
import os

from fastapi import logger


def save_request_to_json(request_data: dict, endpoint: str):
    """
    Salva os dados da requisição em um arquivo JSON com timestamp.
    
    Args:
        request_data (dict): Dados da requisição
        endpoint (str): Nome do endpoint que recebeu a requisição
    """
    
    # Cria o diretório de logs se não existir
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        
    # Gera nome do arquivo com timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{log_dir}/{endpoint}_{timestamp}.json"
    
    # Salva os dados no arquivo
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(request_data, f, indent=4, ensure_ascii=False)
        
      