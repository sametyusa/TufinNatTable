import requests
from requests.auth import HTTPBasicAuth
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import datetime
import json, re, pprint, time, pdb

"""
Tufin'den F5 Big-IP pool IP'lerini alir. 
DEVELOPMENT EDITITON
(c) Samet Atalar
"""
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

tufinURL="https://YOUR_TUFIN_INTERFACE_IP/securetrack/api"
tufinUser="YOUR_TUFIN_USER"
tufinpass="YOUR_TUFIN_USER_PASSWORD"
virtualIP=dict()
finalList=dict() #Pool VIP, Pool Name ve Pool Member IP'ler bu listede
deviceIDList = [tufindeviceid,tufindeviceid2]
simdi=datetime.datetime.now()
def uploadTable(finalIPList): 
    print("%s Uploading  F5 pool IPs to Database..."%simdi)
    print(finalIPList)
    headers={"Content-Type":"application/json"}
    poolIP=[]
    for poolName, f5nodeip in finalIPList.items(): 
        posttoservice = requests.post("https://127.0.0.1/NatIPUploader.php",data={"update":"1","internetip":"0.0.0.0","privateip":virtualIP[poolName],"f5update":"1","f5node":json.dumps(f5nodeip)},timeout=200,verify=False)
        print(posttoservice.text)
        posttoservice.close()
        time.sleep(0.5)

def getPoolMembers(poolName,vip,config):
        """Cluster IP'lerini getirir"""
        print("%s Searching members in %s" %(simdi,poolName))
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
                pprint.pprint("Liste %s, VIP %s"%(finalList,vip))
                finalList.clear()

def getPoolConfig(deviceid):
        """F5 Pool yapilandirmasini getirir"""
        print("%s Downloading configurations from Tufin  device id %d" %(simdi,deviceid))
        tufinrequrl=tufinURL+"/devices/%d/config" % deviceid
        headers={"Content-Type":"application/json","Accept":"application/json"}
        r=requests.get(tufinrequrl, auth=HTTPBasicAuth(tufinUser, tufinpass),verify=False)
        r.close()
        hasRulesVirtualIP=dict()
        """
        1. Once tum VIP isimleri alinir. 
        2. Bir sonraki vip ismine kadar olan yazi icerisinde pool adi aranir. (pool varsa rule yok sayilir. )
        3. Pool adi varsa getPoolMember fonksiyonu cagrilir. Yoksa irule bulunup isimler cekilir. iRuledaki ilk pool alinir.
        4. uploadTable web servisine verileri yukler
        """
        ltmVirtualRegex=re.findall(r"ltm\svirtual\s([\w]+).*?\ndestination\s(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}).*?\nip\-protocol\s([a-z]+)\nmask\s(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})[\s\S]*?pool\s([\w\-]+)",r.text)
        for pc in ltmVirtualRegex:
                print("%s Searching pools of %s"%(simdi,pc[0]))
                #Eger config icinde rules varsa pool adi rulestan geliyor.
                ltmVIPRegex=re.search(r"ltm\svirtual\s(%s)*\s{([\s\S]*?ltm\svirtual)"%pc[0],r.text)
                try:
                        ltmSearchPoolRegex = re.findall(r"pool\s([\w+]*)",ltmVIPRegex.group(2))    
                        if(len(ltmSearchPoolRegex)>0):
                                print("%s Pool found for %s"%(simdi,pc[0]))
                                virtualIP[pc[4]] = pc[1]
                                getPoolMembers(pc[4],pc[1],r.text)
                        else:
                                ltmFoundRuleName=re.search(r"rules\s\{\n(\w+)\n}",ltmVIPRegex.group(2))
                                print("%s searching irule %s for %s"%(simdi,ltmFoundRuleName.group(1),pc[0]))
                                ltmiRuleRegex=re.search(r"ltm\srule\s%s\s{([\s\S]*?ltm\srule)"%ltmFoundRuleName.group(1),r.text) #Istenen irule
                                ltmSearchPoolInRule = re.search(r"pool\s([\w+]*)",ltmiRuleRegex.group(1))   
                                if(ltmSearchPoolInRule.group() is not None or ltmSearchPoolInRule.group() != ""):
                                        poolNameinRule=ltmSearchPoolInRule.group(1)
                                        print ("%s pool %s for %s"%(simdi,poolNameinRule,ltmSearchPoolInRule.group(1)))
                                        virtualIP[poolNameinRule] = pc[1]
                                        getPoolMembers(poolNameinRule,pc[1],r.text)
                                else:
                                        print("%s No rule found for %s"%(simdi,ltmFoundRuleName.group(1)))
                except AttributeError as e:
                        print(e)
                        pass                 

for deviceid in deviceIDList:
        #findPoolMembers(privateiplist,deviceid)
        getPoolConfig(deviceid)
