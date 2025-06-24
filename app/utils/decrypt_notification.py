import base64
import json
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import hmac
import hashlib
import logging

from config import PRIVATE_KEY

logger = logging.getLogger(__name__)

def decrypt_data(encrypted_data: str, encrypted_key: str) -> str:
    """
    Descriptografa os dados do email usando a chave privada do certificado.
    """    
    try:
        # Validação dos parâmetros de entrada
        if not encrypted_data or not encrypted_key:
            raise ValueError("Dados criptografados ou chave não podem ser nulos")

        if not PRIVATE_KEY:
            raise ValueError("Chave privada não configurada")

        private_key = serialization.load_pem_private_key(
            PRIVATE_KEY,
            password=None
        )

        # Descriptografa a chave de dados
        try:
            encrypted_key_bytes = base64.b64decode(encrypted_key)
            data_key = private_key.decrypt(
                encrypted_key_bytes,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA1()),
                    algorithm=hashes.SHA1(),
                    label=None
                )
            )
        except Exception as e:
            raise ValueError(f"Erro ao descriptografar a chave de dados: {str(e)}")

        # Descriptografa os dados usando a chave de dados
        try:
            from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
            from cryptography.hazmat.backends import default_backend

            # Decodifica os dados criptografados
            encrypted_data_bytes = base64.b64decode(encrypted_data)
            
            # Extrai o IV (primeiros 16 bytes) e os dados criptografados
            iv = encrypted_data_bytes[:16]
            ciphertext = encrypted_data_bytes[16:]

            # Cria o cipher usando AES em modo CBC
            cipher = Cipher(
                algorithms.AES(data_key),
                modes.CBC(iv),
                backend=default_backend()
            )
            decryptor = cipher.decryptor()

            # Descriptografa os dados
            decrypted_data = decryptor.update(ciphertext) + decryptor.finalize()

            # Remove o padding PKCS7
            padding_length = decrypted_data[-1]
            decrypted_data = decrypted_data[:-padding_length]

            # Decodifica para string
            decoded_data = decrypted_data.decode('utf-8')
            logger.debug("Dados descriptografados com sucesso")
            return decoded_data

        except Exception as e:
            raise ValueError(f"Erro ao descriptografar os dados: {str(e)}")

    except ValueError as ve:
        logger.error(f"Erro de validação ao descriptografar dados: {str(ve)}")
        raise
    except Exception as e:
        logger.error(f"Erro inesperado ao descriptografar dados: {str(e)}")
        raise