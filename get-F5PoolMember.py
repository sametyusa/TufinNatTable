import requests
from requests.auth import HTTPBasicAuth
from requests.packages.urllib3.exceptions import InsecureRequestWarning

import json, re, pprint, time, pdb

"""
Tufin'den F5 Big-IP pool IP'lerini alir. 
(c) Samet Atalar
"""
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

tufinURL="https://yourTufinIP/securetrack/api"
tufinUser="yourTufinUser"
tufinpass="yourTufinPassword"
virtualIP=dict()
finalList=dict() #Pool VIP, Pool Name ve Pool Member IP'ler bu listede
#deviceid ,,
deviceIDList = [yourDeviceID,yourDeviceID2]
def uploadTable(finalIPList): 
    print("Uploading  F5 pool IPs to Database...")
    headers={"Content-Type":"application/json"}
    poolIP=[]
    for poolName, f5nodeip in finalIPList.items(): 
        posttoservice = requests.post("http://yourWebServerIP/NatIPUploader.php",data={"update":"1","internetip":"0.0.0.0","privateip":virtualIP[poolName],"f5update":"1","f5node":json.dumps(f5nodeip)},timeout=200)
    #   pprint.pprint("%s: %s => %s"%(poolName, virtualIP[poolName],f5nodeip))
        print(posttoservice.text)
        posttoservice.close()
        time.sleep(0.5)

def getPoolMembers(poolName,vip,config):
        """Cluster IP'lerini getirir"""
        print("Searching members in %s" % poolName)
        #poolNameRegex=re.findall(r"")
        pattern = r"ltm\spool\s(%s)\s\{([\s\S]*?)\}\nltm\spool" % re.escape(poolName)
        poolMemberRegex=re.findall(pattern,config)
        for pmip in poolMemberRegex:
                memberIPregex=re.findall(r"address\s(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})",pmip[1])
                poolIP=[]
                for mip in memberIPregex:
                        #print(mip)
                        poolIP+=memberIPregex
                        finalList[pmip[0]] = tuple(poolIP)
                        poolIP = []
                uploadTable(finalList)
                finalList.clear()

def getPoolConfig(deviceid):
        """F5 Pool yapilandirmasini getirir"""
        print("Downloading configurations from Tufin  device id %d" % deviceid)
        tufinrequrl=tufinURL+"/devices/%d/config" % deviceid
        headers={"Content-Type":"application/json","Accept":"application/json"}
        r=requests.get(tufinrequrl, auth=HTTPBasicAuth(tufinUser, tufinpass),verify=False)
        r.close()
        ltmVirtualRegex=re.findall(r"ltm\svirtual\s([\w]+).*?\ndestination\s(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}).*?\nip\-protocol\s([a-z]+)\nmask\s(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})[\s\S]*?pool\s([\w\-]+)",r.text)
        for pc in ltmVirtualRegex:
                virtualIP[pc[4]] = pc[1]
                getPoolMembers(pc[4],pc[1],r.text)
       #pprint.pprint(virtualIP)
                

for deviceid in deviceIDList:
        #findPoolMembers(privateiplist,deviceid)
        getPoolConfig(deviceid)