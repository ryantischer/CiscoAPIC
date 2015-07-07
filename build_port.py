__author__ = 'ryantischer'
#!/usr/bin/env python
#
# Written by Ryan Tischer @ Cisco

#Script configures a phyiscal port in an EPG for a bare metal server
#Assumes the phyiscal port is configured under fabric \ access policies

#Requires sys, json and requests.
#Requires http enabled on the APIC.  Optionally can configure TLS1.1/1.2 on script server for https and will require
#changing base_url and workingURL to https

# To enable http on APIC...

#On the menu bar, FABRIC -> Fabric Policies -> Pod Policies -> Policies -> Communication
#Under Communication, click the default policy
#In the Work pane, enable HTTP and disable HTTPS

#NOTE:  Configuration is atomic, if it fails for whatever reason, the entire configuration fails.

#usage Can be run by opening this file and directly editing the variables.  Optionally command line agruments can be
#used.  If command line agruments are used the script only checks for correct number of agruments.  --help prints help


import json
import requests
import sys

numArg = len(sys.argv)
if numArg == 1:
    #Vars to be filled out.  Can be switched to sys agrv
    apic = "10.91.85.170"
    username = "admin"
    password = "cisco13579"
    apicTenant = "Tischer"
    apicANP = "2-TierApp"
    apicEPG = "DBServers"
    apicVlan = "1"
    apicPOD = "pod-1"
    apicSwitch = "101"
    apicPort = "eth1/13414"

elif numArg == 2 and sys.argv[numArg-1] == "--help":

    print " usage: python build_port.py apicip username password tenant ANP epg vlan POD switch port"
    print " example: python build_port.py 10.91.85.170 admin cisco123 tenant1 2Tierapp DBservers 1 pod-1 101 eth1/1"
    print " help found with --help"
    print""
    sys.exit() #bail out

elif numArg == 11:
    apic = sys.argv[1]
    username = sys.argv[2]
    password = sys.argv[3]
    apicTenant = sys.argv[4]
    apicANP = sys.argv[5]
    apicEPG = sys.argv[6]
    apicVlan = sys.argv[7]
    apicPOD = sys.argv[8]
    apicSwitch = sys.argv[9]
    apicPort = sys.argv[10]

else:
    print "You did something wrong.  Read below and try again"
    print " usage: build_port.py apicip username password tenant ANP epg vlan POD switch port"
    print " example: build_port.py 10.91.85.170 admin cisco123 tenant1 2Tierapp DBservers 1 pod-1 101 eth1/1"
    sys.exit() #bail out

#Login into APIC and get a cookie

#build base url
base_url = 'http://' + apic + '/api/aaaLogin.json'

# create credentials structure
name_pwd = {"aaaUser": {"attributes": {"name": "username", "pwd": "password"}}}
name_pwd["aaaUser"]["attributes"]["pwd"] = password
name_pwd["aaaUser"]["attributes"]["name"] = username


# log in to API, get cookie
try:
    post_response = requests.post(base_url, json=name_pwd, timeout = 5)
except requests.exceptions.RequestException as e:
    print "Error with http connection  Your error is around... "
    print e
    sys.exit()

# get token from login response structure
auth = json.loads(post_response.text)
try:
    login_attributes = auth['imdata'][0]['aaaLogin']['attributes']
except:
    print "Authenication error"
    sys.exit()
auth_token = login_attributes['token']

# create cookie array from token
cookies = {}
cookies['APIC-Cookie'] = auth_token

#once we have the cookie we can make changes

#build dict to send to apic
workingUrl =  "http://" + apic + "/api/node/mo/uni/tn-" + apicTenant + "/ap-" + apicANP + "/epg-" + apicEPG + ".json"
workingData = {"fvRsPathAtt":{"attributes":{"encap":"vlan-1","instrImedcy":"immediate","tDn":"topology/pod-1/paths-101/pathep-[eth1/1]","status":"created"},"children":[]}}
workingData["fvRsPathAtt"]["attributes"]["encap"] = "vlan-1" + apicVlan
workingData["fvRsPathAtt"]["attributes"]["tDn"] = "topology/" + apicPOD + "/paths-" + apicSwitch + "/pathep-[" +apicPort + "]"

#create the static port in egp
try:
    post_response = requests.post(workingUrl, cookies=cookies, json=workingData)
    print "http code = " + str(post_response)
    print "http code 400 will show up if configuation is already present"
    print ""
    print "data send to APIC..."
    print json.dumps(workingData, sort_keys=True, indent=4)
    print ""
    print "URL = " + workingUrl
except requests.exceptions.RequestException as e:
    print "something went wrong with sending json to APIC. Your issue is around"
    print e
    sys.exit()
