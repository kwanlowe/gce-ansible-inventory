#!/usr/bin/env python

#### Copyright 2017 Kwan L. Lowe
#### This is a crude Ansible inventory script for Google Compute Engine
from pprint import pprint

from googleapiclient import discovery
from oauth2client.client import GoogleCredentials
from httplib2 import Http
import sys
import json
import optparse

from oauth2client.service_account import ServiceAccountCredentials


def readGceConfig(gceConfigFile, nodeName):
    """ Reads node configuration file, returns dictionary. """ 

    import ConfigParser
    import sys
    import os.path

    config = ConfigParser.RawConfigParser()
    gceConfigFile = os.path.expanduser(gceConfigFile)
    
    gceConfig={}
    try:
        config.read(gceConfigFile)
        gceConfig['gceProject']  = config.get(nodeName, 'Project')
        gceConfig['gceScopes'] = config.get(nodeName, 'Scopes')
        gceConfig['gceSecret'] = config.get(nodeName, 'Secret')
        gceConfig['gceZone'] = config.get(nodeName, 'Zone') 
        gceConfig['gceOutput'] = config.get(nodeName, 'Output') 

        return gceConfig

    except IOError:
        print "Unable to locate node configuration file " + gceConfigFile + '.\n'
        sys.exit(3)
        raise 
    except ConfigParser.NoSectionError:
         print "Unable to locate section [" + nodeName + "]" + " in " + gceConfigFile + ".\n"
         sys.exit(3)
    else:
         print "Unexpected error in readNodeConfig: %s" % e
         sys.exit(1)


#################################
# main
#################################
parser = optparse.OptionParser()
parser.add_option( '--list', action="store_true", dest="invlist", help="List inventory")
parser.add_option( '--host', action="store", dest="hostname", help="Return host list")
options, args = parser.parse_args()

node = options.hostname
getlist = options.invlist

### Read the GCE configurations from setupfile
### FUTURE: Loop through each config section and output 
###         each project as a separate group for ansible.

gceConfig = readGceConfig("inventory_data.cfg", "Config")

outputType = gceConfig["gceOutput"]
myscopes = [gceConfig["gceScopes"]]
project = gceConfig["gceProject"]
zone = gceConfig["gceZone"]

credentials = ServiceAccountCredentials.from_json_keyfile_name(gceConfig["gceSecret"], scopes=myscopes)
service = discovery.build('compute', 'v1', credentials=credentials)
request = service.instances().list(project=project, zone=zone)

hosts = []
response = request.execute()
for instance in response['items']:
    hosts.append(instance['name'])

ips = []
for instance in response['items']:
    if instance['status'] != 'TERMINATED':
       for item in instance['networkInterfaces']:
           for access in item['accessConfigs']:
              if 'natIP' in access:
                ips.append(access['natIP'])


gceList = { gceConfig["gceProject"] : { "hosts" : hosts, "vars" : {} } }
gceIps = { gceConfig["gceProject"] : { "hosts" : ips, "vars" : {} } }

if getlist:
    if outputType == "hostname":
        print json.dumps(gceList)
    elif outputType == "ipaddress":
        print json.dumps(gceIps)
    else:
        print "Invalid Output type in config."
        print "Please select 'hostname' or 'ipaddress'."
        sys.exit(1)
elif len(node) != 0:
   ### Output an empty list.D.. 
   ### Perhaps project metadata could go here...
   print json.dumps(gceList[gceConfig["gceProject"]]["vars"])
