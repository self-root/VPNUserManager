import re
import secrets
import redis
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from enum import Enum
from jinja2 import Environment, FileSystemLoader
from apiexception import CodeDoesNotMatch, CodeExpired
import asyncio

class Mail:
    def __init__(self, subject: str, to: str, body: str) -> None:
        self.subject = subject
        self.__from = "irootsoftware@gmail.com"
        self.__pwd = "olcxknzixncgyfec"
        self.__host = "smtp.gmail.com"
        self.__port = 465 #587
        self.to = to
        self.body = body

    async def send(self):
        multipart = MIMEMultipart()
        multipart["Subject"] = self.subject
        multipart["From"]= self.__from
        multipart["To"] = self.to
        message = MIMEText(self.body, "html")
        multipart.attach(message)
        context = ssl.create_default_context()
    
        with smtplib.SMTP_SSL(self.__host, self.__port, context=context) as server:
            server.login(self.__from, self.__pwd)
            server.sendmail(
                self.__from,
                self.to,
                multipart.as_string()
            )

class MailType(Enum):
    VERIFICATION = 1
    ACCOUNT_ACTIVATED = 2
    SUBSCRIPTION = 3

class PostOffice:
    @staticmethod
    def sendVerificationMail(mail: str):
        verificationCode = PostOffice.generateRandomDigits()
        PostOffice.saveVerificationCode(mail, verificationCode)
        print("User mail: ", mail)
        verifMail = Mail(
            "Verifiy email",
            mail,
            PostOffice.renderMailBody(MailType.VERIFICATION, {"code": verificationCode}))
        asyncio.run(verifMail.send()) 

    @staticmethod
    def generateRandomDigits() -> int:
        random = ""
        for _ in range(0, 6):
            random += str(secrets.randbelow(10))
        return random

    @staticmethod
    def mailAddressValid(mail: str) -> bool:
        if re.fullmatch("^[a-zA-Z0-9.!#$%&’*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\\.[a-zA-Z0-9-]+)*$", mail):
            return True
        return False
    
    @staticmethod
    def renderMailBody(mailType: MailType, content: dict[str, str]) -> str:
        env = Environment(loader=FileSystemLoader("templates/"))
        template = None
        if mailType == MailType.VERIFICATION:
            template = env.get_template("verification.html")
            return template.render(content)
    
    @staticmethod
    def saveVerificationCode(key: str,code: str):
        r = redis.Redis(host='127.0.0.1', port=6379)
        r.set(key, code, 10*60)

    @staticmethod
    def getVerivicationCode(mail: str):
        r = redis.Redis(host='127.0.0.1', port=6379)
        code = r.get(mail)
        if code is not None:
            return code.decode()
        

    @staticmethod
    def verify(mailAddress: str, verificationCode: str) -> bool:
        code = PostOffice.getVerivicationCode(mailAddress)
        print(f"VerifCode: {code} VS {verificationCode}")

        if code == verificationCode:
            return True
        
        if code == None:
            raise CodeExpired("Verification code has expired")
        else:
            raise CodeDoesNotMatch("Wrong verification code")

        
        
    
if __name__ == "__main__":
    mail = Mail("Test", "oscar.thegreat@outlook.com", "<h1>Hello, world</h1>")
    mail.send()