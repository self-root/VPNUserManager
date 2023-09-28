from flask import Flask, request
import json
from utils import Utility
from auth import Auth, AuthType, AuthErrCode
from apiexception import CodeDoesNotMatch, CodeExpired
from usermanager import UserManager
from mail import PostOffice
from tokenfactory import Intent
from vpnmanager import VPNManager

app = Flask(__name__)

@app.get("/vpnusers/ping")
def ping():
    return "pong", 200

@app.get("/vpnusers/login")
def login():
    # Check if it has auth header
    # check auth type
    # verify authe
    #   Check database if uname/pwd login
    #       Assign new token
    #   verify token validity if token
    # Send user vpn config
    
    if Utility.hasAuthHeader(request.headers):
        auth = Auth.getAuth(request.headers.get("Authorization"))
        return UserManager.login(auth)
        """if auth.atype == AuthType.NONE:
            return "Authorization header not properly formated", 400
        else:
            try:
                token, mail = auth.authenticate()
                res = {
                    "token": token,
                    "mail": mail
                }
                return res, 200
            except UnverifiedUser as e:
                tempToken = auth.makeTempToken()
                UserManager.generateNewCode(auth.mail)
                res = {
                    "err": "unverifieduser",
                    "temptoken": tempToken
                }
                return res, 401
            except UnverifiedUserToken:
                res = {
                    "err": "unverifiedusertoken",
                    "temptoken": token
                }
                return res, 401
            except UserNotFound:
                return "User not found", 404
            except InvalidToken:
                res = {
                    "err": "invalidtoken",
                }
                return res, 401
            except jwt.InvalidTokenError as e:
                print(f"Invalid token: {e}")
                res = {
                    "err": "invalidtoken",
                }
                return res, 401

            except Exception as e:
                print(f"ERROR: {e}")
                return "Internall error", 500
    else:
        return "Bad request", 400
    """
    
@app.post("/vpnusers/signup")
def signup():
    contentLength = request.headers.get("Content-Length", type=int)
    if request.is_json and contentLength <= 160:
        try:
            forms = json.loads(request.data)
            print(request.headers.get("Content-Length", type=int))            
            return UserManager.handleSignup(forms)
        except json.JSONDecodeError:
            response = {
                "error": "bad_request",
                "error_description": "The json data can not be parsed"
            }
            return response, 400
    else:
        return "payload_too_large", 413

@app.post("/vpnusers/mail/verify")
def verifyMail():
    contentLength = request.headers.get("Content-Length", type=int)
    if request.is_json and contentLength <= 160:
        try:
            data = json.loads(request.data)
            code = data["code"]
            mail = data["mail"]
            PostOffice.verify(mail, code)
            token = UserManager.makeUserToken(mail)
            UserManager.makeUserVerified(mail)
            res = {
                "token": token,
                "mail": mail
            }
            return res, 200
        except CodeExpired:
                UserManager.generateNewCode(mail)
                res = {
                    "error": "code_expired",
                    "error_description": "Verification code has expired, check your mail for the new one"
                }
                return res, 401
        except CodeDoesNotMatch:
            res = {
                "error": "code_not_match",
                "error_description": "Code provided to not match"
            }
            return res, 403
        
        except Exception as e:
            print("ERROR::: ", e)
            return "Unknown error", 500

@app.post("/vpnuser/userconf")
def userConf():
    contentLength = request.headers.get("Content-Length", type=int)
    if not request.is_json or contentLength > 160:
        return "bad request", 400
    if Utility.hasAuthHeader(request.headers):
        auth = Auth.getAuth(request.headers.get("Authorization"))
        if auth.atype != AuthType.BEARER:
            return "Authorization header not properly formated", 400
        
        authResult = auth.authenticate()
        if authResult.errCode == AuthErrCode.SUCCESS:
            #TODO: change the request method to post and add json body that has device information
            device = json.loads(request.data)
            conf = VPNManager.getUserConf(authResult.mail, {"id": device})
            if conf:
                return conf, 200
            else:
                result = {
                    "error": "device_eccess",
                    "error_description": "You've reached the maximum number of 3 regustered device"
                }

                return result, 403
        else:
            result = {
                    "error": "invalid_token",
                    "error_description": "An access token is require in the auth header to make this request"
                }

            return result, 401
    else:
        result = {
                    "error": "unauthorized",
                    "error_description": "An access token is require in the auth header to make this request"
            }

        return result, 401
    

