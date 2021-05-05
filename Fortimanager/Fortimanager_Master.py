#!/usr/local/bin/python3

import requests
import json
import time

requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)


class FortiManager:
    def __init__(self, username, password, url, session=None):
        self.USERNAME = username
        self.PASSWORD = password
        self.URL = url
        self.HEADERS = {"Content-type": "application/json"}
        self.session = session

    def login(self):
        print("\n Login to the FortiManager....")
        params = {
            "method": "exec",
            "params": [{"url": "sys/login/user", "data": [{"passwd": self.PASSWORD, "user": self.USERNAME}],}],
            "id": 1,
            "session": None,
        }

        res = requests.post(url=self.URL, headers=self.HEADERS, json=params, verify=False)
        res = res.json()
        self.session = res["session"]
        print("Login to the Fortimanager")
        return res

    def logout(self):

        params = {
            "method": "exec",
            "params": [{"url": "/sys/logout"}],
            "session": self.session,
            "id": 1,
        }

        res = requests.post(url=self.URL, headers=self.HEADERS, json=params, verify=False)
        res = res.json()
        print("\n Logout from the FortiManager\n")
        return res


    def get_connection_status(self, adom):
        print("\n Login to the Fortigate FW :{}\n".format(adom))
        params = {
            "method": "get",
            "params": [
                {
                    "url": "/dvmdb/adom/" + adom + "/device",
                    "fields": ["name", "ip", "sn", "platform_str", "conn_status", "mgmt_mode"],
                    "filter": [["conn_status", "!=", 1]],
                    "loadsub": 0,
                }
            ],
            "id": 1,
            "session": self.session,
        }

        res = requests.post(url=self.URL, headers=self.HEADERS, json=params, verify=False)
        res = res.json()
        print (res)
        return res

    # T10.Push the configuration from Fortimanger to fortigate FW.    
    def quick_install_device(self, adom, device_name,vlan_name):
        print("\n FortiManager pushing all the config. to Fortigate FW: {} for L3out :{}\n".format(device_name,vlan_name))
        params = {
            "method": "exec",
            "params": [
                {
                    "url": "/securityconsole/install/device",
                    "data": {"adom": adom, "scope": [{"name": device_name, "vdom": "root",}],},
                }
            ],
            "id": 1,
            "session": self.session,
        }

        res = requests.post(url=self.URL, headers=self.HEADERS, json=params, verify=False)
        res = res.json()
        return res


    # T1.Configure the L3out interface.
    def add_vlan_interface(self, device_name, vlan_name, vdom_name, ipadd_subnet,vlan_id,phy_interface):
        print("Configure the FM L3out VLAN-interface: {}".format(vlan_name))
        params = {
            "method": "set",
            "params": [
                {
                    "url": "/pm/config/device/"+ device_name +"/global/system/interface",
                    "data": [{"name": vlan_name,"vdom": vdom_name, "ip": ipadd_subnet, "vlanid": vlan_id,"interface": phy_interface,"status": 1,"allowaccess": 130},],
                }
            ],
            "id": 1,
            "session": self.session,
        }

        res = requests.post(url=self.URL, headers=self.HEADERS, json=params, verify=False)
        res = res.json()
        #print(json.dumps(params, indent=4))
        return res

    #2 Configure the L3out into Zone interface
    def add_zone_interface(self, device_name, zone_name, interface_name):
        print("Configure the FM to associate the VLAN into Zone policy:{}".format(zone_name))
        params = {
            "method": "set",
            "params": [
                {
                    "url": "/pm/config/device/"+ device_name +"/vdom/root/system/zone",
                    "data": [{ "name": zone_name, "interface":interface_name},],
                }
            ],
            "id": 1,
            "session": self.session,
        }

        res = requests.post(url=self.URL, headers=self.HEADERS, json=params, verify=False)
        res = res.json()
        #print(json.dumps(params, indent=4))
        return res


#3 Add the Static Route
    def add_static_route(self, device_name, interface, destination, distance, gateway):
        print("Configure the FM to add static route for destination :{}".format(destination))
        params = {
            "method": "set",
            "params": [
                {
                    "url": "/pm/config/device/" + device_name + "/vdom/root/router/static",
                    "data": [{"device": interface, "dst": destination, "distance": distance, "gateway": gateway}],
                }
            ],
            "id": 1,
            "session": self.session,
        }

        res = requests.post(url=self.URL, headers=self.HEADERS, json=params, verify=False)
        res = res.json()
        #print(json.dumps(params, indent=4))
        return res   
   
    def disable_vlan_interface(self, device_name, vlan_name, vdom_name, ipadd_subnet,vlan_id,phy_interface):
        print("Configure the FM to disable the sub-interface ")
        params = {
            "method": "set",
            "params": [
                {
                    "url": "/pm/config/device/"+ device_name +"/global/system/interface",
                    "data": [{"id": 0,"vdom": vdom_name, "ip": ipadd_subnet, "vlanid": vlan_id,"interface": phy_interface,"status": 0},],
                }
            ],
            "id": 1,
            "session": self.session,
        }

        res = requests.post(url=self.URL, headers=self.HEADERS, json=params, verify=False)
        res = res.json()
        #print(json.dumps(params, indent=4))
        return res

    def add_access_list(self, device_name, advertise_subnet, access_list):
        print("Configure the FM to create the access_list and then add the prefixes")
        params = {
            "method": "set",
            "params": [
                {
                    "url": "/pm/config/device/"+ device_name +"/vdom/root/router/access-list",
                    "data": [{"rule":[{ "id":0,"prefix": advertise_subnet}],"name": access_list}],
                     #"data": [{"rule":[{ "edit":0,"prefix": advertise_subnet}],"name": access_list}],
     
                }
            ],
            "id": 1,
            "session": self.session,
        }
        res = requests.post(url=self.URL, headers=self.HEADERS, json=params, verify=False)
        res = res.json()
        #print(json.dumps(params, indent=4))
        return res   
    
    def add_acl_to_rm(self, device_name, l3out_rm_name, access_list):
        print("Configure the FM to create the route-map and associate the access-list ")
        params = {
            "method": "set",
            "params": [
                {
                    "url": "/pm/config/device/"+ device_name +"/vdom/root/router/route-map",
                    "data": [{ "rule": [{"action": 0,"match-ip-address": access_list}],
                    "name": l3out_rm_name
                }],
     
                }
            ],
            "id": 1,
            "session": self.session,
        }
        res = requests.post(url=self.URL, headers=self.HEADERS, json=params, verify=False)
        res = res.json()
        #print(json.dumps(params, indent=4))
        return res  


#4 Redistribute the Static route into OSPF with Route-map
    
    def add_rm_to_ospf(self, device_name, l3out_rm_name):
        print("Configure the FM to associate the Route-map into OSPF Static Redistribution ")
        params = {
            "method": "set",
            "params": [
                   {
                    "url": "/pm/config/device/" + device_name + "/vdom/root/router/ospf",
                    "data": {"redistribute": [
                        { "metric": 0, "metric-type": 0, "name": "bgp","routemap": [],"status": 0,"tag": 0  },
                    {
                        "metric": 0,
                        "metric-type": 0,
                        "name": "connected",
                        "routemap": [],
                        "status": 0,
                        "tag": 0
                    },
                    {
                        "metric": 0,
                        "metric-type": 0,
                        "name": "isis",
                        "routemap": [],
                        "status": 0,
                        "tag": 0
                    },
                    {
                        "metric": 0,
                        "metric-type": 0,
                        "name": "rip",
                        "routemap": [],
                        "status": 0,
                        "tag": 0
                    },
                    {   "metric": 0,
                        "metric-type": 0,
                        "name": "static",
                        "routemap": l3out_rm_name,
                        "status": 1,
                        "tag": 0
                    }
                ],},
            }],
            "id": 1,
            "session": self.session,
        }          
        res = requests.post(url=self.URL, headers=self.HEADERS, json=params, verify=False)
        res = res.json()
        #print(json.dumps(params, indent=4))
        return res
            


    # Pull the configuration from the Fortimanager Database.
    def get_config_block(self, device_name, scope, config_block):
        print("\n Pulling current REST API configuration from the controller for :{}\n".format(config_block))
        params = {
            "method": "get",
            "params": [{"url": "/pm/config/device/" + device_name + "/" + scope + "/" + config_block, }],
            "id": 1,
            "session": self.session,
        }
        res = requests.post(url=self.URL, headers=self.HEADERS, json=params, verify=False)
        res = res.json()
        #print(json.dumps(res, indent=4))
        return res  
          
    # Pull the global interface configuration from the Fortimanager Database.
    def get_interface_block(self, device_name, interface_block):
        print("\n Pulling current REST API configuration from the controller for :{}\n".format(interface_block))
        params = {
            "method": "get",
            "params": [{"url": "/pm/config/device/" + device_name + "/"+ interface_block, }],
            "id": 1,
            "session": self.session,
        }
        res = requests.post(url=self.URL, headers=self.HEADERS, json=params, verify=False)
        res = res.json()
        print(json.dumps(res, indent=4))
        return res
"""
    def append_access_list(self, device_name, advertise_subnet, t7,access_list):
        new_data = [{"rule":[{ "id":0,"prefix": advertise_subnet}],}],
        print(new_data)
        res = t7
        curr_data = res["result"][0]["data"]
        print(curr_data)
        rules=curr_data[0]["rule"].append(new_data)
        print(rules)
        #print("Configure the FM to create the access_list and then add the prefixes"
        params = {
            "method": "set",
            "params": [
                {
                    "url": "/pm/config/device/"+ device_name +"/vdom/root/router/access-list",
                    "data": [{"rule":rules,"name": access_list}],

     
                }
            ],
            "id": 1,
            "session": self.session,
        }
        res = requests.post(url=self.URL, headers=self.HEADERS, json=params, verify=False)
        res = res.json()
        #print(json.dumps(params, indent=4))
        return res   

   def append_access_list(self, device_name, advertise_subnet, access_list):
        print("Configure the FM to create the access_list and then add the prefixes")
        params = {
            "method": "set",
            "params": [
                {
                    "url": "/pm/config/device/"+ device_name +"/vdom/root/router/access-list",
                    "data": [{"rule":[{ "id":0,"prefix": advertise_subnet}],"name": access_list}],
                     #"data": [{"rule":[{ "edit":0,"prefix": advertise_subnet}],"name": access_list}],
     
                }
            ],
            "id": 1,
            "session": self.session,
        }
        res = requests.post(url=self.URL, headers=self.HEADERS, json=params, verify=False)
        res = res.json()
        #print(json.dumps(params, indent=4))
        return res 
       
    # Pull the configuration from the Fortimanager Database.
    def get_config_block(self, device_name, scope, config_block):
        print("\n Pulling current REST API configuration from the controller for :{}\n".format(config_block))
        params = {
            "method": "get",
            "params": [{"url": "/pm/config/device/" + device_name + "/" + scope + "/" + config_block, }],
            "id": 1,
            "session": self.session,
        }
        res = requests.post(url=self.URL, headers=self.HEADERS, json=params, verify=False)
        res = res.json()
        #print(json.dumps(res, indent=4))
        return res 
    def update_access_list(device_name, list_name, data):
       
    fmg = FortiManager("fortiapi", "fortiapi", "https://172.19.255.53/jsonrpc")
    fmg.login()
    res = get_config_block(device_name, "vdom/root", "router/access-list" + list_name)
    url = res["result"][0]["url"]
    curr_data = res["result"][0]["data"]
    curr_data[0]["rule"].append(data)
   
    res = fmg.add_config_block(curr_data, url)    

    """