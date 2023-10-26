from flask import Flask, request
import json
from utils import Utility
from auth import Auth, AuthType, AuthErrCode
from apiexception import CodeDoesNotMatch, CodeExpired
from usermanager import UserManager
from mail import PostOffice
from vpnmanager import VPNManager
from mlogger import handler
import logging

app = Flask(__name__)
app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)


@app.get("/vpn/ping")
def ping():
    return "pong", 200

@app.get("/vpn/login")
def login():
    # Check if it has auth header
    # check auth type
    # verify authe
    #   Check database if uname/pwd login
    #       Assign new token
    #   verify token validity if token
    # Send user vpn config
    
    app.logger.info(f"{request.remote_addr} Login request")
    authHeaders = request.headers
    for h in authHeaders.keys():
        app.logger.info(f"Header_key: {h}")
    if Utility.hasAuthHeader(request.headers):
        auth = Auth.getAuth(request.headers.get("Authorization"))
        return UserManager.login(auth)
    return "Bad request", 400
    
@app.post("/vpn/signup")
def signup():
    app.logger.info(f"{request.remote_addr} Signup request")
    contentLength = request.headers.get("Content-Length", type=int)
    if contentLength <= 160:
        try:
            forms = json.loads(request.data)
            print(request.headers.get("Content-Length", type=int))            
            return UserManager.handleSignup(forms)
        except json.JSONDecodeError as e:
            app.logger.exception("Json error while handling signuo form")
            response = {
                "error": "bad_request",
                "error_description": "The json data can not be parsed"
            }
            return response, 400
        except Exception as e:
            app.logger.exception("Error with signup")
            response = {
                "error": "server_error",
                "error_description": str(e)
            }
            return response, 500
    else:
        app.logger.critical(f"{signup.__name__}: Payload too large, size = {contentLength}")
        return "payload_too_large", 413

@app.post("/vpn/mail/verify")
def verifyMail():
    app.logger.info(f"{request.remote_addr} Mail verification")
    contentLength = request.headers.get("Content-Length", type=int)
    if contentLength <= 160:
        try:
            data = json.loads(request.data)
            code = data["code"]
            mail = data["mail"]
            PostOffice.verify(mail, code)
            UserManager.makeUserVerified(mail)
            res = {
                "mail": mail
            }
            return res, 200
        except CodeExpired as e:
                UserManager.generateNewCode(mail)
                res = {
                    "error": "code_expired",
                    "error_description": "Verification code has expired, check your mail for the new one"
                }
                app.logger.info(f"{mail}: code_expired")
                return res, 401
        except json.decoder.JSONDecodeError as e:
            res = {
                    "error": "bad_request",
                    "error_description": "A json payload is expected"
                }
            app.logger.exception(f"{verifyMail.__name__}: No json Payload")
            return res, 400
        except CodeDoesNotMatch:
            res = {
                "error": "code_not_match",
                "error_description": "Code provided to not match"
            }
            app.logger.info(f"{mail}: Verification code does not match")
            return res, 403
        
        except Exception as e:
            app.logger.exception(f"{verifyMail.__name__}: Error occured")
            return "Unknown error", 500
    else:
        res = {
            "error": "payload_too_large",
            "error_description": "The body length exceed the limit"
        }
        app.logger.critical(f"{signup.__name__}: Payload too large, size = {contentLength}")
        return res, 413

@app.post("/vpn/userconf")
def userConf():
    app.logger.info(f"{request.remote_addr} Get user conf")
    contentLength = request.headers.get("Content-Length", type=int)
    if contentLength > 160:
        return "bad request", 400
    if Utility.hasAuthHeader(request.headers):
        auth = Auth.getAuth(request.headers.get("Authorization"))
        if auth.atype != AuthType.BEARER:
            return "Authorization header not properly formated", 400
        
        authResult = auth.authenticate()
        if authResult.errCode == AuthErrCode.SUCCESS:
            #TODO: change the request method to post and add json body that has device information
            device = json.loads(request.data)
            conf = VPNManager.getUserConf(authResult.mail, device)
            if conf:
                return conf, 200
            else:
                result = {
                    "error": "device_eccess",
                    "error_description": "You've reached the maximum number of 3 regustered device, or has no active subscription"
                }
                app.logger.info(f"{authResult.mail}: device_eccess")
                return result, 403
        else:
            result = {
                "error": "invalid_token",
                "error_description": "An access token is require in the auth header to make this request"
                }
            app.logger.info(f"{authResult.mail}: invalid_token")
            return result, 401
    else:
        result = {
            "error": "unauthorized",
            "error_description": "An access token is require in the auth header to make this request"
        }
        app.logger.info(f"{userConf.__name__}: An access token is require in the auth header to make this request")
        return result, 401
    
@app.get("/vpn/devices")
def userDevices():
    app.logger.info(f"{request.remote_addr} Get devices")
    if Utility.hasAuthHeader(request.headers):
        auth = Auth.getAuth(request.headers.get("Authorization"))
        if auth.atype != AuthType.BEARER:
            return "Authorization header not properly formated", 400
        
        authResult = auth.authenticate()
        if authResult.errCode == AuthErrCode.SUCCESS:
            devices = VPNManager.getDevices(authResult.mail)
            return devices, 200
        else: 
            result = {
                    "error": "invalid_token",
                    "error_description": "An access token is require in the auth header to make this request"
                }
            app.logger.info(f"{authResult.mail}: invalid_token")
            return result, 401
    
    else:
        result = {
                    "error": "unauthorized",
                    "error_description": "An access token is require in the auth header to make this request"
            }

        return result, 401
    
@app.delete("/vpn/devices/delete/<device_id>")
def removeDevice(device_id: str):
    app.logger.info(f"{request.remote_addr} Remove device")
    if Utility.hasAuthHeader(request.headers):
        auth = Auth.getAuth(request.headers.get("Authorization"))
        if auth.atype != AuthType.BEARER:
            return "Authorization header not properly formated", 400
        
        authResult = auth.authenticate()
        if authResult.errCode == AuthErrCode.SUCCESS:
           app.logger.info(f"{authResult.mail} removing device: {device_id}")
           removed = VPNManager.removeDevice(authResult.mail, device_id)
           if removed:
               return {"device": device_id}, 200
           return {"device": device_id}, 204

        else:
            result = {
                    "error": "invalid_token",
                    "error_description": "An access token is require in the auth header to make this request"
                }
            app.logger.info(f"{authResult.mail}: invalid_token")
            return result, 401
    else:
        return "bad request", 400
    
if __name__ == "__main__":
    app.run(host="0.0.0.0")
    

