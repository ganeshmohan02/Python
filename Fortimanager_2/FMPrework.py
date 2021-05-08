def main():
    from Fortimanager_Master import FortiManager
    import fwinput_cfg as data
    host= "https://172.19.255.53/jsonrpc"
    usr="fortiapi"
    pwd= "fortiapi"   
    i = input("Enter the no.of vlan's you want to Migration:")
    for x in range(int(i)):
      try:
       device_name=(data.vlan_list[x]["device_name"])
       scope=(data.vlan_list[x]["scope"])
       adom=(data.vlan_list[x]["adom"])
       vdom_name=(data.vlan_list[x]["vdom_name"])
       l3out_int_name=(data.vlan_list[x]["l3out_int_name"])
       vlan_id = (data.vlan_list[x]["vlan_id"])
       gw_network=(data.vlan_list[x]["gw_network"])
       gw_mask=(data.vlan_list[x]["gw_mask"])
       l3out_phy_interface=(data.vlan_list[x]["l3out_phy_interface"])
       l3out_ipadd=(data.vlan_list[x]["l3out_ipadd"])
       aci_l3out_nexthop=(data.vlan_list[x]["aci_l3out_nexthop"])
       l3out_rm_name=(data.vlan_list[x]["l3out_rm_name"])
       l3out_nh_interface=l3out_int_name
       l3out_vlan_name=l3out_int_name+"_L3out"
       distance = "10"
       prefix ="prefix"
       zone_name= l3out_int_name+"_Zone"
       access_list = "rof_adv_list"
       #Network = "192.168.6.0"
       #SubnetMask = "255.255.255.0"
       gw_subnet = gw_network +"/"+ gw_mask
       config_block="router/access-list"   #"system/zone" or "router/ospf" or "router/static" or "router/access-list" or "router/route-map"
       interface_block="global/system/interface"
       print ("")
       print("Logging into Fortimanager Controller:{}".format(host))
       print("Configure the FW :{}".format(device_name))
       print("Configure the new L3out interface :{}".format(l3out_int_name))
       print("Associate the new L3out int. into member of :{}".format(zone_name))
       print("Configure the .1Q Sub-interface vlan for L3out #:{}".format(vlan_id))
       print("Configure the Physical interface for new L3out:{}".format(l3out_phy_interface))
       print("Configure the Next-hop IP address ACI :{}".format(aci_l3out_nexthop))
       print("Configure the GW_subnet Next-hop to ACI :{}".format(gw_subnet))
       print("Configure the IP address on L3out interface:{}".format(l3out_ipadd))
       print("Configure the Route-map {} on FW:{}".format(l3out_rm_name,device_name))
       print("Configure the Access-list {} on the FW:{}".format(access_list,device_name))    
          
   
       ACTION = input("Are you sure you want to push the configuration (y/n): ")
       if ACTION in ("y","yes","Y","YES"): 
         FM=FortiManager(usr, pwd, host)
         print("Calling the Master function -> Authenticating into the FM Controller")
         t0=FM.login()
         #t1=FM.add_vlan_interface(device_name, l3out_vlan_name, vdom_name, l3out_ipadd,vlan_id,l3out_phy_interface)
         #t2=FM.add_zone_interface(device_name, zone_name, l3out_vlan_name)
         #t3=FM.add_static_route(device_name, l3out_vlan_name, gw_subnet, distance, aci_l3out_nexthop)
         t7=FM.get_config_block(device_name,scope, "router/access-list")
         #print(t7)
         res=t7  
         #print(res)
         curr_data = res["result"][0]["data"][0]["rule"]
         curr_data1 = res["result"][0]["data"][0]
         acl_rule=curr_data1["rule"]
         acl_name=curr_data1["name"]
         acl_prefix=curr_data[0]["prefix"]
         #print(acl_rule)
         #print(acl_name)
         print(acl_prefix[0])
         print(acl_prefix[1])
         if None == acl_rule and acl_name == access_list:
          print("ACL Entries not exist.")
          t4= FM.add_access_list(device_name, gw_subnet, access_list)
         elif acl_prefix[0]==gw_network and acl_prefix[1]==gw_mask:
          print("ACL entire already exist")      
         else:
            print("Append the new entire in the access-list")
            t8=FM.append_access_list(device_name, gw_subnet, t7,access_list)
          #if gw_subnet not in acl: 
           # print("Appending the new prefixes into the existing access-list")
           # t8=FM.append_access_list(device_name, gw_subnet, t7,access_list)
           # break  

         #t5= FM.add_acl_to_rm(device_name, l3out_rm_name, access_list)
         #t6=FM.add_rm_to_ospf(device_name, l3out_rm_name)
         #t7=FM.get_config_block(device_name,scope, config_block)
         #t8=FM.append_access_list(device_name, gw_subnet, t7,access_list)
         #t8=FM.get_interface_block(device_name, interface_block)
         #t8=FM.quick_install_device(adom, device_name,l3out_vlan_name)    ### Push the configuration from Fortimanager to Fortigate Firewall.
         t10=FM.logout()
       elif ACTION in ("n","no","N","No"):
          print("Ending the script")
       else: 
         print("Please enter yes or no.")
      except IndexError:
       print("Oops!  Out of the vlan migration range.  please check and Try again...")  
 
if __name__ == '__main__':
    main()