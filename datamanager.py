from peewee import (MySQLDatabase, Model, 
                    SmallIntegerField, CharField, DateField,
                    BooleanField, ForeignKeyField,
            )
import datetime
from utils import Utility
import os

db = MySQLDatabase("vpn_user_db",
                        host="localhost",
                        user=os.getenv("VPN_DB_USERNAME"),
                        password=os.getenv("VPN_DB_PASSWORD"))
class BaseModel(Model):
    class Meta:
        database = db

class User(BaseModel):
    mail = CharField(max_length=100, unique=True, null=False)
    verified = BooleanField(default=False)
    password = CharField(max_length=64, null=False)
    
class Subscription(BaseModel):
    date_sub = DateField(default=datetime.date.today())
    end_sub = DateField(null=False)
    user = ForeignKeyField(User)


class Device(BaseModel):
    d_type = CharField(max_length=100)
    d_name = CharField(max_length=100)
    d_os = CharField(max_length=60)
    d_id = CharField(max_length=200, unique=True)
    user = ForeignKeyField(User)
    config = CharField(max_length=200, unique=True)

#class Config(BaseModel):
#    conf = CharField(max_length=100, unique=True)
#    device = ForeignKeyField(Device)
      

def saveUser(mail: str, password: str):
    pwd = Utility.hashPassword(password)
    user = User.create(mail=mail, password=pwd)
    user.save()

def setUserVerified(mail: str):
    user = User.get(mail=mail)
    user.verified = True
    user.save()

def getDevices(mail: str):
    return (Device.select(Device, User).join(User).where(Device.user.mail==mail))

def getDevice(deviceId: str) -> Device:
    return Device.get_or_none(d_id=deviceId)

def getDeviceCount(mail: str):
    return len(getDevices(mail))

def getDeviceConf(mail: str, deviceId: str) -> str:
    """
    Get the config file name of the user's device from the database,
    it is assumed that the user has at least one config file when this function is called
    """
    """device =  (
        Config.select(
            Config,
            Device,
            User
        ).join(Device).where(Device.d_id==deviceId)
        .join(User).where(Device.user.mail==mail))[0]"""
    device = Device.get_or_none(d_id=deviceId) #Should be getOrNone??
    if device:
        if device.user.mail == mail:
            return device.config
    return device


def addUserDevice(mail: str, device: dict[str, str]) -> Device:
    user = User.get_or_none(mail=mail)
    if user:
        device_ = Device.create(d_id=device['id'], config=device["config"], user=user)
        device_.save()
        return device_


def removeDevice(deviceId: str, mail: str):
    device = getDevice(deviceId)
    if device.user.mail == mail:
        device.delete_instance()

def addSubscription(mail: str, untilDate: datetime.date):
    user_ = User.get_or_none(mail=mail)
    if user_:
        sub = Subscription.get_or_none(user=user_.id)
        if sub:
            sub.end_sub = untilDate
            sub.save()
        
        else:
            sub = Subscription.create(end_sub=untilDate, user=user_)
            sub.save()

def getEndSub(mail: str) -> datetime.date:
    user_ = User.get_or_none(mail=mail)
    if user_:
        sub = Subscription.get_or_none(user=user_.id)
        if sub:
            return sub.end_sub
    


if __name__ == "__main__":
    with db:
        #db.create_tables([User, Subscription, Subscribe, Device, Config])
        #user = User.create(mail="oscar.thegreat@outlook.com", verified=True, password="12345")
        #user.save()
        #db.drop_tables([Device])
        db.create_tables([User, Subscription, Device])
        #device = Device.create(d_id="moto_3328", user=1)
        #conf_ = Config.create(conf="oscar12ww4.conf", device=2)
        #query = (Device.select(Device, User).join(User).where(Device.user.mail == "oscarmendeleiev@gmail.com"))
        
        #for i in query:
        #    print(f"id: {i.d_id},  {i.user.mail}")

        #q = (Config.select(Config,Device, User).join(Device).where(Device.d_id=="moto_3328").join(User).where(Device.user.mail == "oscarmendeleiev@gmail.com"))[0]
        #for i in q:
        #print(f"Conf {q.conf},  {q.device.d_id}")

        #print(f"Conf@: {getDeviceConf('oscarmendeleiev@gmail.com', 'moto_3328')}")

        #print(f"User device count: {deviceCount('oscarmendeleiev@gmail.com')}")
        