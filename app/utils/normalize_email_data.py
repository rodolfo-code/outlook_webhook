from app.models.email import Email


def normalize_email_data(email_data: dict) -> Email:
    """
    Normaliza os dados do email em um formato padronizado.
    
    Args:
        email_data: Objeto contendo os dados do email
        
    Returns:
        dict: Dicionário com os dados do email normalizados
    """
    email = Email.from_graph_data(email_data)
    return email.to_dict()
