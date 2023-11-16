from tokenfactory import TokenFactory, Intent
from datamanager import User, Admin
import base64
from apiexception import UnverifiedUser, UserNotFound, InvalidToken
from enum import Enum
from utils import Utility
from abc import ABC, abstractmethod

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

class AuthBase(ABC):
    def __init__(self, atype: AuthType, value: str) -> None:
        self.atype = atype
        self.value = value

    @abstractmethod
    def authenticate(self) -> AuthResult:
        pass
    
    @abstractmethod
    def basicAuth(self) -> AuthResult:
        pass

    @staticmethod
    def getBasicCredentials(basicAuthHeader: str) -> tuple:
        """
            Parse value of a Basic authentication (username:password),
            and return a tuple containing (username, password)
            Param:
                basicAuthHeader: base64 encoded 'username:password' credentials
            Return:
                tuple containing username and password
        """
        decodedBytes = base64.b64decode(basicAuthHeader)
        print(f"Basic header decoded: {decodedBytes}")
        basicHeader = decodedBytes.decode()
        return basicHeader.split(":", 1)
    
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

class AdminAuth(AuthBase):
    def __init__(self, atype: AuthType, value: str) -> None:
        super().__init__(atype, value)
        self.username = ""

    def authenticate(self) -> AuthResult:
        if self.atype == AuthType.BASIC:
            return self.basicAuth()
        elif self.atype == AuthType.BEARER:           
            verfyResult = TokenFactory.verifyaAdmin(self.value)
            if verfyResult:
                authResult = AuthResult()
                authResult.errCode = AuthErrCode.SUCCESS
                authResult.token, authResult.mail = verfyResult
                return authResult
            else:
                return AuthResult(AuthErrCode.INVALID_TOKEN)
        else:
            return AuthResult(AuthErrCode.BAD_REQUEST)
        
    def basicAuth(self) -> AuthResult:
        credentials =  AuthBase.getBasicCredentials(self.value)
        authResult = AuthResult()
        if len(credentials) != 2:
            authResult.errCode = AuthErrCode.BAD_REQUEST
            return authResult
        self.username, password = credentials
        self.username = self.username.replace(" ", "")
        password = password.replace(" ", "")
        authResult.mail = self.username
        user = Admin.get_or_none(username=self.username, password=Utility.hashPassword(password))
        if user:
            authResult.token = TokenFactory.createAdminToken(self.password)
            authResult.mail = self.username
            authResult.errCode = AuthErrCode.SUCCESS
                
        else:
            authResult.errCode = AuthErrCode.NO_USER

        return authResult

class Auth(AuthBase):
    def __init__(self, atype: AuthType, value: str) -> None:
        super().__init__(atype, value)
        self.mail = ""

    def authenticate(self) -> AuthResult:
        """
        Authenticate the user. Return a token or raise an exception

        Returns:
            str: a new token or the existing token if still valid
        """
        if self.atype == AuthType.BASIC:
            return self.basicAuth()
        elif self.atype == AuthType.BEARER:           
            verfyResult = TokenFactory.veryfy(self.value)
            if verfyResult:
                authResult = AuthResult()
                authResult.errCode = AuthErrCode.SUCCESS
                authResult.token, authResult.mail = verfyResult
                return authResult
            else:
                return AuthResult(AuthErrCode.INVALID_TOKEN)
        else:
            return AuthResult(AuthErrCode.BAD_REQUEST)
        
    def basicAuth(self) -> AuthResult:
        """
        Authenticate user with mail and password

        Returns:
            AuthResult: an object containing an error code and the user token if auth successfull
        """
        credentials =  AuthBase.getBasicCredentials(self.value)
        authResult = AuthResult()
        if len(credentials) != 2:
            authResult.errCode = AuthErrCode.BAD_REQUEST
            return authResult
        self.mail, password = credentials
        self.mail = self.mail.replace(" ", "")
        password = password.replace(" ", "")
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
    
    