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
       gw_subnet=(data.vlan_list[x]["gw_subnet"])
       vlan_phy_interface=(data.vlan_list[x]["vlan_phy_interface"])
       l3out_ipadd=(data.vlan_list[x]["l3out_ipadd"])
       aci_l3out_nexthop=(data.vlan_list[x]["aci_l3out_nexthop"])
       l3out_rm_name=(data.vlan_list[x]["l3out_rm_name"])
       l3out_nh_interface=l3out_int_name
       l3out_vlan_name=l3out_int_name+"_L3out"
       advertise_subnet = gw_subnet
       distance = "10"
       zone_name= l3out_int_name+"_Zone"
       advertise_subnet = gw_subnet
       access_list = "rof_adv_list"
       config_block="router/access-list"   #"system/zone" or "router/ospf" or "router/static" or "router/access-list" or "router/route-map"
       interface_block="global/system/interface"
       print ("")
       print("Logging into Fortimanager Controller:{}".format(host))
       print("Configure the FW :{}".format(device_name))
       print("Configure the new L3out interface :{}".format(l3out_int_name))
       print("Associate the new L3out int. into memeber of :{}".format(zone_name))
       print("Configure the .1Q Sub-interface vlan for L3out #:{}".format(vlan_id))
       print("Configure the Physical interface for new L3out:{}".format(vlan_phy_interface))
       print("Configure the Next-hop IP address ACI :{}".format(aci_l3out_nexthop))
       print("Configure the IP address on L3out interface:{}".format(l3out_ipadd))
       print("Configure the Route-map {} on FW:{}".format(l3out_rm_name,device_name))
       print("Configure the Access-list {} on the FW:{}".format(access_list,device_name))    
          
   
       ACTION = input("Are you sure you want to push the configuration (y/n): ")
       if ACTION in ("y","yes","Y","YES"): 
         FM=FortiManager(usr, pwd, host)
         print("Calling the Master function -> Authenticating into the FM Controller")
         t0=FM.login()
         t1=FM.add_vlan_interface(device_name, l3out_vlan_name, vdom_name, l3out_ipadd,vlan_id,vlan_phy_interface)
         t2=FM.add_zone_interface(device_name, zone_name, l3out_vlan_name)
         t3=FM.add_static_route(device_name, l3out_vlan_name, gw_subnet, distance, aci_l3out_nexthop)
         t4= FM.add_access_list(device_name, advertise_subnet, access_list)
         t5= FM.add_acl_to_rm(device_name, l3out_rm_name, access_list)
         t6=FM.add_rm_to_ospf(device_name, l3out_rm_name)
         #t7=FM.get_config_block(device_name,scope, config_block)
         t8=FM.get_interface_block(device_name, interface_block)
         t8=FM.quick_install_device(adom, device_name,l3out_vlan_name)    ### Push the configuration from Fortimanager to Fortigate Firewall.
         t10=FM.logout()
       elif ACTION in ("n","no","N","No"):
          print("Ending the script")
       else: 
         print("Please enter yes or no.")
      except IndexError:
       print("Oops!  Out of the vlan migration range.  please check and Try again...")  
 
if __name__ == '__main__':
    main()