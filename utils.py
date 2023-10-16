from werkzeug.datastructures import Headers
import os
import hashlib
from mlogger import logger

class Utility:

    @staticmethod
    def hasAuthHeader(requestHeader : Headers) -> bool:
        """
        Check if the 'Authorization' header is present in the request headers.

        Args:
            requestHeader (Headers): The request headers.

        Returns:
            bool: True if 'Authorization' header is present, False otherwise.
        """
        logger.debug(f"Headers: {requestHeader.keys()}")
        return  "Authorization" in requestHeader.keys()
    
    @staticmethod
    def hashPassword(pwd: str) -> str:
        password = pwd + os.getenv("VPN_TOKEN_KEY")
        hashed = hashlib.sha256(password.encode())
        return hashed.hexdigest()