import requests
from requests.auth import HTTPBasicAuth
from requests.packages.urllib3.exceptions import InsecureRequestWarning

import json, re, pprint, time

"""
Tufin'den Internet firewall configini alip
NAT tablosu yazar. 
v1.1
"""
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

tufinURL="https://yourTufinIP/securetrack/api"
tufinUser="yourTufinUser"
tufinpass="yourTufinPassword"
publicIPList=dict()
privateIPList=[]
deviceIDList = [yourDeviceID,yourDeviceID2]

natListenerURL = "http://yourWebServerIP/NatIPUploader.php"

def uploadTable(internetIPList):
    print("Uploading  NAT Table to Database...")
    headers={"Content-Type":"application/json"}
    for publicip, privateip in internetIPList.items():
        posttoservice = requests.post(natListenerURL,data={"add":"1","internetip":publicip,"privateip":privateip},timeout=200)
        print(publicip)
        pprint.pprint(posttoservice.text)
        posttoservice.close()
        time.sleep(0.5)
		
def getIPFromDB(ip):
	#IP veritabaninda zaten var mi
	getIPInfo = requests.post(natListenerURL,data={"singleip":"1","ip":ip},timeout=200)
	return getIPInfo.json()
	
def getAllIPFromDB():
	#Var olan listeyi alir ve yenisiyle karsilastirir. Farklari DBden siler
	getNatTable = requests.post(natListenerURL,data={"geturl":"1","startlimit":"0","stoplimit":"500","whichip":"both"},timeout=200)
	return getNatTable.json()

def deleteFromDB(ip):
	deleteIP = requests.post(natListenerURL,data={"deleteip":"1","ip":ip},timeout=200)
	return deleteIP.json()

for deviceid in deviceIDList:
    print("Downloading configurations from Tufin  device id %d" % deviceid)
    tufinrequrl=tufinURL+"/devices/%d/config" % deviceid
    headers={"Content-Type":"application/json","Accept":"application/json"}
    r=requests.get(tufinrequrl, auth=HTTPBasicAuth(tufinUser, tufinpass),verify=False)
    publicIPRegex = re.findall(r"extip \b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}",r.text)
    privateIPRegex = re.findall(r'mappedip "\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}"',r.text)
    #response = http.urlopen(request)
    #json_response = json.loads(request.data)
    r.close()
    for privateipf in privateIPRegex:
        privateipn=privateipf.split(" ")
        splitquote = privateipn[1].split("\"")
        privateIPList.append(splitquote[1])
    i=0
    for publicipf in publicIPRegex:
        publicipn=publicipf.split(" ")
        publicIPList[publicipn[1]] = privateIPList[i]
        i=i+1
#pprint.pprint(publicIPList)
print("=====================")
print("Found %d nat rules" % len(publicIPList))
print("=====================")
uploadTable(publicIPList)		#Once yukle, sonra fazlaliklari sil
existingList = getAllIPFromDB()
searchList = existingList["nat"]
for id,publicip,privateip,f5node,created,updated in searchList:
	try:
		publicIPList[publicip]
					
	except KeyError:
		print("Cannot found this in new configuration: %s"% publicip)
		msg=deleteFromDB(publicip)
		print(msg)
	#if len(publicIPList[publicip])<1:
	#	print("%s yok"% publicip)

	
print("Finished.")
