import wgconfig
import datamanager
import datetime
import os
import subprocess
from mlogger import logger
from wg_client_service.wg_conf_client import WgConfServiceClient
import json

class VPNManager:
    @staticmethod
    def getUserConf(mail: str, device: dict[str, str]) -> dict[str,str]:
        if VPNManager.hasActiveSubsciption(mail):
            confName = datamanager.getDeviceConf(mail, device["id"])
            if confName:
                conf = VPNManager.parseConf(confName)
                return conf
            else:
                deviceCount = datamanager.getDeviceCount(mail)
                if deviceCount < 3:
                    # Create new conf, 
                    print(device)
                    confName = VPNManager.makeConf(mail, device["id"])
                    # save it to database,
                    device["config"] = confName
                    datamanager.addUserDevice(mail, device)
                    # then load it
                    conf = VPNManager.parseConf(confName)
                    return conf
                else:
                    # Excess device
                    return None
            
        # User already has 3 registered device
            

    @staticmethod
    def hasActiveSubsciption(mail: str) -> bool:
        endSubDate = datamanager.getEndSub(mail)
        if endSubDate:
            today = datetime.date.today()
            return today <= endSubDate
        return False
    
    @staticmethod
    def parseConf(conf_: str) -> dict[str, str]:
        userConf = WgConfServiceClient.getClientConf(conf_)
        return json.loads(userConf)
    
    @staticmethod
    def makeConf(mail: str, deviceId: str) -> str:
        confName = deviceId
        #subprocess.run(["/root/./wireguard_cl_add.sh", confName])
        WgConfServiceClient.createClientConf(deviceId)
        return confName

    @staticmethod
    def makeConfName(mail:str, deviceId: str) -> str:
        mail = VPNManager.cleanStr(mail)
        deviceId = VPNManager.cleanStr(deviceId)
        confName = mail+deviceId
        return confName

    @staticmethod
    def cleanStr(txt: str)->str:
        return txt.replace(".","").replace("@","").replace("_", "").replace("-","")
    
    @staticmethod
    def getDevices(email : str) -> list[dict[str,str]]:
        devices = datamanager.getDevices(email)
        # TODO: convert devices into dict
        devices_ = []
        for device in devices:
            d = {
                "device_id" : device.d_id,
                "device_os" : device.d_os,
                "device_name" : device.d_name,
                "devoce_type" : device.d_type,

            }
            devices_.append(d)

        return devices_
    
    @staticmethod
    def removeDevice(email: str, deviceId : str) -> str:
        try:
            removed = datamanager.removeDevice(deviceId, email)
            if removed:
                #subprocess.run(["/root/./wireguard_cl_delete.sh", deviceId])
                WgConfServiceClient.deleteClientConf(deviceId)
                return removed
        except Exception as e:
            logger.exception(f"Error while removing device: {deviceId}")


if __name__=="__main__":
    #VPNManager.getUserConf("s", "d")
    mail = "oscarmendeleiev@gmail.com"
    mail2 = "root00.localhost@protonmail.com"
    print(f"Has sub: {VPNManager.hasActiveSubsciption(mail)}")
    print(f"Has sub2: {VPNManager.hasActiveSubsciption(mail2)}")