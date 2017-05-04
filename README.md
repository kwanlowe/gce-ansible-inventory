# gce-ansible-inventory #

## Purpose ##

This is a kludgey bit of code to return hosts or ip addresses for a given GCE project. 
I wrote it in the past hour after struggling with various inventory scripts to work.
The docs for gce.py are apparently outdated. The ones for the node-based inventory script
broke on my version of node, then on libcloud, then something else. There's most likely
a proper script somewhere that does exactly what this does but my google-fu has failed.

## How to Use ##
### Install Google API client for Python ###

```
mkdir -p ~/bin/gce_venv
virtualenv ~/bin/gce/venv/bin/active
pip install --upgrade pip
pip install --upgrade setuptools
pip install google-api-python-client
```

### Setup the preferences file ###
You'll need to configure the inventory_data.cfg file with the following:

```
[Project1]
Project = rstudio-1234
Scopes = https://www.googleapis.com/auth/compute.readonly
Secret = /home/kwan/.ssh/RStudio-0123434c25bc7.json
Zone = us-east1-b
Output = hostname

[Project2]
Project = tensorflow-1234
Scopes = https://www.googleapis.com/auth/compute.readonly
Secret = /home/kwan/.ssh/RStudio-40de34c25bc7.json
Zone = us-east1-b
Output = ipaddress
```

All these fields should be self-explanatory.  The "Output" field just selects either
the hostname or the IP address to print.

### Edit script to place the configuration file ###
By default it looks in the current directory but can be modified to a different location such
as some path in your Ansible tree (or out of it).

```
vi gce_inventory.py

configFile = "~/src/ansible/inventory_data.cfg"
```



## Usage ##
The usage is simple:
```
./gce_inventory.py [--list|--host]
```

Once the inventory file is configured you can test with:
```
(gce_venv) [kwan@infinity gceBuildServer]$ ./gce_inventory.py --list
{"Project1": {"hosts": ["35.190.130.202", "35.185.107.33"], "vars": {}}, 
 "Project2": {"hosts": ["kll-tester-003", "kll-tester-004"], "vars": {}}
}

(gce_venv) [kwan@infinity gceBuildServer]$ ./gce_inventory.py --host doesntmatter
{}
```

To use in Ansible, you'll need to put it your path and configure Ansible to use it
as a dynamic inventory. To test you can do something like:

```
ansible rstudio-2345 -i ./gce_inventory.py -a "hostname"
```

If all works well, you should see something like:
```
(gce_venv) [kwan@infinity gceBuildServer]$ ansible Project1 -i ./gce_inventory.py -a "hostname"
35.190.130.202 | SUCCESS | rc=0 >>
kll-tester-003

35.185.107.33 | SUCCESS | rc=0 >>
kll-tester-004
```


