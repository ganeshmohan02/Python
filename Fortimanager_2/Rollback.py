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
       gw_subnet=(data.vlan_list[x]["gw_subnet"])
       current_phy_interface=(data.vlan_list[x]["current_phy_interface"])
       current_vlan_interface = (data.vlan_list[x]["current_vlan_interface"])
       print ("")
       print("Logging into Fortimanager Controller:{}".format(host))
       print("Configure the FW :{}".format(device_name))
       print("Enable the old interface :{} on Subnet {}".format(current_vlan_interface,gw_subnet))          
       ACTION = input("Are you sure you want to push the configuration (y/n): ")
       if ACTION in ("y","yes","Y","YES"): 
         FM=FortiManager(usr, pwd, host)
         print("Calling the Master function -> Authenticating into the FM Controller")
         t0=FM.login()
         t1=FM.rollback_vlan_interface(device_name, vdom_name,current_vlan_interface,current_phy_interface)
         t8=FM.quick_install_device(adom, device_name,current_vlan_interface)    ### Push the configuration from Fortimanager to Fortigate Firewall.
         t10=FM.logout()
       elif ACTION in ("n","no","N","No"):
          print("Ending the script")
       else: 
         print("Please enter yes or no.")
      except IndexError:
       print("Oops!  Out of the vlan migration range.  please check and Try again...")  
 
if __name__ == '__main__':
    main()