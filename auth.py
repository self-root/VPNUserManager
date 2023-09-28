from tokenfactory import TokenFactory, Intent
from datamanager import User
import base64
from apiexception import UnverifiedUser, UserNotFound, InvalidToken
from enum import Enum
from utils import Utility

class AuthType(Enum):
    BASIC = 1
    BEARER = 2
    NONE = 3

class AuthErrCode(Enum):
    SUCCESS = 1
    NO_USER = 2
    UNVERIFIED_MAIL = 3
    BAD_REQUEST = 4
    INVALID_TOKEN = 5

class AuthResult:
    def __init__(self, errCode=AuthErrCode.SUCCESS) -> None:
        self.errCode = errCode
        self.token = ''
        self.mail = ''

class Auth:
    def __init__(self, atype : AuthType, value : str) -> None:
        self.atype = atype
        self.value = value
        self.mail = ""

    def authenticate(self, intent=Intent.LOGIN) -> AuthResult:
        """
        Authenticate the user. Return a token or raise an exception

        Returns:
            str: a new token or the existing token if still valid
        """
        if self.atype == AuthType.BASIC:
            return self._basicAuth()
        elif self.atype == AuthType.BEARER:           
            verfyResult = TokenFactory.veryfy(self.value, intent)
            if verfyResult:
                authResult = AuthResult()
                authResult.errCode = AuthErrCode.SUCCESS
                authResult.token, authResult.mail = verfyResult
                return authResult
            else:
                return AuthResult(AuthErrCode.INVALID_TOKEN)
        else:
            return AuthResult(AuthErrCode.BAD_REQUEST)
        
    def _basicAuth(self) -> AuthResult:
        """
        Authenticate user with mail and password

        Returns:
            AuthResult: an object containing an error code and the user token if auth successfull
        """
        decodedBytes = base64.b64decode(self.value)
        print(f"Basic header decoded: {decodedBytes}")
        basicHeader = decodedBytes.decode()
        credentials =  basicHeader.split(":", 1)
        authResult = AuthResult()
        if len(credentials) != 2:
            authResult.errCode = AuthErrCode.BAD_REQUEST
            return authResult
        self.mail, password = credentials
        authResult.mail = self.mail
        user = User.get_or_none(mail=self.mail, password=Utility.hashPassword(password))
        if user:
            if user.verified == True:
                authResult.token = TokenFactory.cretateVerifiedUserToken(self.mail)
                authResult.errCode = AuthErrCode.SUCCESS
            else: #UnverifiedUser
                authResult.errCode = AuthErrCode.UNVERIFIED_MAIL
                
        else:
            authResult.errCode = AuthErrCode.NO_USER

        return authResult
        
    def makeTempToken(self):
        return TokenFactory.createUnverifiedUserToken(self.mail)
    
    @staticmethod
    def getAuth(auth : str):
        """
        Parse and extract authentication information from the input string.

        Args:
            auth (str): The authentication string in the format 'Basic <value>' or 'Bearer <value>'.

        Returns:
            Auth: An Auth object containing the authentication type and value.
        """
        print(f"Auth header: {auth}")
        splited = auth.split(" ")
        if len(splited) == 2:
            if splited[0] == "Basic":
                return Auth(AuthType.BASIC, splited[1])
            elif splited[0] == "Bearer":
                return Auth(AuthType.BEARER, splited[1])

        return Auth(AuthType.NONE, "")