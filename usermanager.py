from mail import PostOffice
import datamanager
from peewee import IntegrityError
from tokenfactory import TokenFactory
from auth import Auth, AuthErrCode

class UserManager:
    @staticmethod
    def login(auth : Auth):
        authResult = auth.authenticate()
        if authResult.errCode == AuthErrCode.SUCCESS:
            response = {
                "token": authResult.token,
                "mail": authResult.mail,
                "end_sub": datamanager.getEndSub(authResult.mail)
                }
            
            return response, 200
        
        elif authResult.errCode == AuthErrCode.INVALID_TOKEN:
            response = {
                "error": "invalid_token",
                "error_description": "The access token provided is invalid or expired."
            }
            return response, 401
        
        elif authResult.errCode == AuthErrCode.BAD_REQUEST:
            response = {
                "error": "bad_request",
                "error_description": "The request is not properly formatted"
            }
            return response, 400
        
        elif authResult.errCode == AuthErrCode.NO_USER:
            response = {
                "error": "invalid_credentials",
                "error_description": "The provided email or/and password are not valid"
            }
            return response, 401
        
        elif authResult.errCode == AuthErrCode.UNVERIFIED_MAIL:
            PostOffice.sendVerificationMail(authResult.mail)
            response = {
                "error": "forbidden",
                "error_description": "The email address has not been verified"
            }
            return response, 403


    @staticmethod
    def handleSignup(form: dict[str, str]) -> str:
        if "mail" and "pwd" in form:
            if PostOffice.mailAddressValid(form["mail"]):
                try:
                    datamanager.saveUser(form["mail"], form["pwd"])
                    #send verification mail to user
                    PostOffice.sendVerificationMail(form["mail"])
                    #create temporary token
                    return "added", 200
                except IntegrityError:
                    response = {
                        "error": "conflict",
                        "error_description": "Email address already registered"
                    }
                    return response, 409
                
            else:
                print(f"Invalid mail {form['mail']}")
                response = {
                        "error": "invalid_email",
                        "error_description": "A valid email address was not provided"
                    }
                return response, 400
        else:
            response = {
                        "error": "bad_request",
                        "error_description": "The form did not contain mail and pwd"
                    }
            return response, 400
        
    @staticmethod
    def makeUserToken(mail: str) -> str:
        return TokenFactory.cretateVerifiedUserToken(mail)
    
    @staticmethod
    def generateNewCode(mail: str):
        PostOffice.sendVerificationMail(mail)
    @staticmethod
    def makeUserVerified(mail: str):
        datamanager.setUserVerified(mail)
        

