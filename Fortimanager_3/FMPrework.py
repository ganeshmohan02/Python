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
       current_vlan_interface=(data.vlan_list[x]["current_vlan_interface"])
       l3out_nh_interface=l3out_int_name
       l3out_vlan_name=l3out_int_name+"_L3out"
       distance = "10"
       prefix ="prefix"
       zone_name= l3out_int_name+"_Zone"
       access_list = "rof_adv_list"
       gw_subnet = gw_network +"/"+ gw_mask
       config_block="system/zone"   #"system/zone" or "router/ospf" or "router/static" or "router/access-list" or "router/route-map"
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
       print("Configure the Current interface on the FW:{}".format(current_vlan_interface))   
          
   
       ACTION = input("Are you sure you want to push the configuration (y/n): ")
       if ACTION in ("y","yes","Y","YES"): 
         FM=FortiManager(usr, pwd, host)
         print("Calling the Master function -> Authenticating into the FM Controller")
         t0=FM.login()
         t1=FM.add_vlan_interface(device_name, l3out_vlan_name, vdom_name, l3out_ipadd,vlan_id,l3out_phy_interface)
         t2=FM.add_zone_interface(device_name, zone_name, l3out_vlan_name,current_vlan_interface)
         t3=FM.add_static_route(device_name, l3out_vlan_name, gw_subnet, distance, aci_l3out_nexthop)
         t4=FM.create_access_list(device_name, access_list)
         t100=FM.get_acl_block(device_name,scope, "router/access-list")
         get_acl=t100 
         verify_acl = get_acl["result"][0]["data"][0]
         #print(verify_acl)
         acl_rule=verify_acl["rule"]
         acl_name=verify_acl["name"]
         if None == acl_rule and acl_name == access_list:
            print("ACL Entries not exist.")
            t5= FM.add_access_list(device_name, gw_subnet, access_list)
         else:
            print("ACL entire already exist")             
         curr_data = get_acl["result"][0]["data"][0]["rule"]
         #print(curr_data)
         prefix_len = int(len(curr_data))
         #print(a)
         i=0
         prefix_list =[]
         for i in range(prefix_len):
               acl_prefix=curr_data[i]["prefix"]
               acl_prefixes=(acl_prefix[0])
               prefix_list.append(acl_prefixes) 
         print (prefix_list)           
         if gw_network in prefix_list:
            print ("The new prefix already exist !!: {}".format(gw_network))
         else: 
           print ("updating the new prefix: {}".format(gw_network))     
           t7=FM.append_access_list(device_name, gw_subnet, t100,access_list)   
         t8= FM.add_acl_to_rm(device_name, l3out_rm_name, access_list)
         t9=FM.add_rm_to_ospf(device_name, l3out_rm_name)
         t7=FM.get_config_block(device_name,scope, config_block)
         #t8=FM.get_interface_block(device_name, interface_block)
         t9=FM.quick_install_device(adom, device_name,l3out_vlan_name)    ### Push the configuration from Fortimanager to Fortigate Firewall.
         t10=FM.logout()
       elif ACTION in ("n","no","N","No"):
          print("Ending the script")
       else: 
         print("Please enter yes or no.")
      except IndexError:
       print("Oops!  Out of the vlan migration range.  please check and Try again...")  
 
if __name__ == '__main__':
    main()