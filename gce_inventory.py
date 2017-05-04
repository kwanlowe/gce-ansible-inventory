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
import ConfigParser
from os.path import expanduser

from oauth2client.service_account import ServiceAccountCredentials

## Update the following line to the location of your inventory configuration file.
configFile = "inventory_data.cfg"
##

configFile = expanduser(configFile)

def readGceConfig(gceConfigFile, nodeName):
    """ Reads node configuration file, returns dictionary. """ 

    import ConfigParser
    import sys

    config = ConfigParser.RawConfigParser()
    
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
         print "Unexpected error while reading configuration file:\n %s" % e
         sys.exit(1)


#################################
# main
#################################
parser = optparse.OptionParser()
parser.add_option( '--list', action="store_true", dest="invlist", help="List inventory")
parser.add_option( '--host', action="store", dest="hostname", help="Return host list")
options, args = parser.parse_args()

if (options.invlist == None) and (options.hostname == None) :
    parser.error("Options missing. Check usage with -h.")
    sys.exit(1)

node = options.hostname
getlist = options.invlist

### Read the GCE configurations from setupfile and loop

config = ConfigParser.RawConfigParser()
config.read(configFile)
sections =  config.sections()

allGroups = {} 
if getlist:
    for groupName in  sections:
        ### FUTURE: Can we pass configParser object instead
        ###         of reading the configFile anew each iteration?
        gceConfig = readGceConfig(configFile, groupName)
    
        outputType = gceConfig["gceOutput"]
        myscopes = [gceConfig["gceScopes"]]
        project = gceConfig["gceProject"]
        zone = gceConfig["gceZone"]
    
        credentials = ServiceAccountCredentials.from_json_keyfile_name(gceConfig["gceSecret"], scopes=myscopes)
        service = discovery.build('compute', 'v1', credentials=credentials)
        request = service.instances().list(project=project, zone=zone)
    
        if outputType == "hostname":
            hosts = []
            response = request.execute()
            for instance in response['items']:
                hosts.append(instance['name'])
    
            allGroups.update({ groupName : { "hosts" : hosts, "vars" : {} }} )
    
        elif outputType == "ipaddress":
            hosts = []
            response = request.execute()
            for instance in response['items']:
                if instance['status'] != 'TERMINATED':
                   for item in instance['networkInterfaces']:
                       for access in item['accessConfigs']:
                          if 'natIP' in access:
                            hosts.append(access['natIP'])
            allGroups.update({ groupName : { "hosts" : hosts, "vars" : {} }} )
    
    
        else:
            print "Invalid Output type in config."
            print "Please select 'hostname' or 'ipaddress'."
            sys.exit(1)


    print json.dumps(allGroups)
elif len(node) != 0:
    ### Output an empty list.D.. 
    ### Perhaps project metadata could go here...
    print json.dumps({}) 


