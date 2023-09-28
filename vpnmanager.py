import wgconfig
import datamanager
import datetime
import os
import subprocess

class VPNManager:
    @staticmethod
    def getUserConf(mail: str, device: dict[str, str]) -> dict[str,str]:
        if VPNManager.hasActiveSubsciption(mail):
            deviceCount = datamanager.getDeviceCount(mail)
            if deviceCount == 0:
                # Create new conf, 
                print(device)
                confName = VPNManager.makeConf(mail, device["id"])
                # save it to database,
                device["config"] = confName
                datamanager.addUserDevice(mail, device)
                # then load it
                conf = VPNManager.parseConf(confName)
                return conf

            elif deviceCount < 3:
                confName = datamanager.getDeviceConf(mail, device["id"])
                conf = VPNManager.parseConf(confName)
                return conf
            
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
        confPath = "/root"
        wg = wgconfig.WGConfig(os.path.join(confPath, conf_))
        wg.read_file()
        interface = wg.get_interface()
        peer = wg.get_peer(wg.get_peers()[0])

        return {**interface, **peer}
    
    @staticmethod
    def makeConf(mail: str, deviceId: str) -> str:
        confName = VPNManager.makeConfName(mail, deviceId)
        subprocess.run(["/root/./wireguard_cl_add.sh", confName])
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
    

if __name__=="__main__":
    #VPNManager.getUserConf("s", "d")
    mail = "oscarmendeleiev@gmail.com"
    mail2 = "root00.localhost@protonmail.com"
    print(f"Has sub: {VPNManager.hasActiveSubsciption(mail)}")
    print(f"Has sub2: {VPNManager.hasActiveSubsciption(mail2)}")