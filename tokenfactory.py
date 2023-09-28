import jwt
import os
import datetime
from enum import Enum
from apiexception import UnverifiedUserToken, UserNotFound, InvalidToken

class Intent(Enum):
    LOGIN = 1
    MAIL_VERIFY = 2
    OTHERS = 3

class TokenFactory:
    @staticmethod
    def veryfy(token: str, intent=Intent.LOGIN) -> tuple:
        try:
            payload = jwt.decode(token, os.getenv("VPN_TOKEN_KEY"), algorithms=["HS256"])
            print(f"Payload: {payload}")
            return token, payload["mail"]
        
        except jwt.InvalidTokenError as e:
            print(f"Invalid signature: {e}")

        except Exception as e:
            print ("Token verification error: ", e)

    @staticmethod
    def cretateVerifiedUserToken(mail : str):
        return TokenFactory.create({
            "mail": mail,
            "exp": datetime.datetime.now() + datetime.timedelta(days=30),
            "verified": "1",
            "iss": "irootsoftware"
        })
    
    @staticmethod
    def createUnverifiedUserToken(mail: str) -> str:
        return TokenFactory.create({
            "mail": mail,
            "exp": datetime.datetime.now() + datetime.timedelta(minutes=10),
            "verified": "0",
            "iss": "irootsoftware"
        })

    @staticmethod
    def create(payload):
        return jwt.encode(payload, os.getenv("VPN_TOKEN_KEY"))
    
    @staticmethod
    def getMail(token: str):
        pass

    

    