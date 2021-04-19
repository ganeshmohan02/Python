def main():
    import getpass
    from FW_GW_project_Master import Client
    host = "172.19.254.4"
    usr="admin"
    pwd = "!@#CiScO123"
    #tn = input("Enter the Tenant Name:")
    tn = "HNSEC_FW_GW"
    vrf = input("Enter the VRF Name:")
    #L3OUT_NAME = input("Enter the L3OUT Name:")
    L3OUT_NAME = vrf
    L3OUT_DOMAIN = "fw_l3Dom"
    #L3OUT_SUBNETS_NAME = input("Enter the L3OUT L3OUT_SUBNETS_NAME:")
    L3OUT_SUBNETS_NAME = L3OUT_NAME+"_Ext_Network"
    SVI_VLAN = input("Enter the .1Q SVI_VLAN ID#:")
    PRI_Node_ID = input("Enter the Leaf PRI_Node_ID Ex:10X :")
    SEC_Node_ID = input("Enter the Leaf SEC_Node_ID  Ex:10Y:")
    PRI_PORT = input("Enter the Ethernet interface on Leaf PRI_Node_ID X/X :")
    SEC_PORT = input("Enter the Ethernet interface on Leaf SEC_Node_ID X/X :")
    PRI_SVI_IP = input("Enter the SVI Primary_IP address/Mask:")
    SEC_SVI_IP = input("Enter the SVI Secondary_IP address/Mask:")
    SVI_GW_IP = input("Enter the SVI GW_IP(HSRP_IP)address/Mask:")
    Next_hop = input("Enter the L3out Next_hop :")
    PRI_ROUTER_ID = input("Enter the unique Leaf PRI_Node ROUTER_ID (Node.Node.MgmtIP.#):")
    SEC_ROUTER_ID = input("Enter the unique Leaf SEC_Node ROUTER_ID (Node.Node.MgmtIP.#):")
    APP = "3tier_APP"
    Consumer_EPG = "WEB_EPG"
    Subnet = "192.168.4.1/24"
    #Dest_Network = input("Enter the L3out External Network Ex:0.0.0.0/0 :")
    Provider_EPG = L3OUT_SUBNETS_NAME
    Dest_Network = "0.0.0.0/0"
    #Contract_name1 = input("Enter the Contract Name :")
    Contract_name = vrf+"_ct"
    #Contract_name = "APP_ct"
    Contract_sub = Contract_name+"_sub"
    #Contract_Scope = input("Enter the Contract Scope (vrf,tenant,global) :")
    Contract_Scope = "tenant"
    #Contract_Scope = "VRF"
    #MTU = input("Enter the MTU Size:")
    MTU = "1500"
    #host = input("Enter the Fabric Controller IP/Hostname Ex:172.19.254.4 :")
    #usr = input("Enter the Fabric username admin:")
    #pwd = getpass.getpass(prompt="Enter the password:")
    #bd = input("Enter the Bridge_ID Name:")

    ACTION = input("Are you sure you want to push the configuration (y/n): ")

    if ACTION in ("y","yes","Y","YES"): 
     #FABRIC=Client(cfg.host, cfg.usr, cfg.pwd)
     FABRIC=Client(host, usr, pwd)
     print("Calling the Master function -> Authenticating into the Controller")
     FABRIC.login()
     t1=FABRIC.tenant(tn,vrf)
     t20=FABRIC.L3OUT_Config(tn,vrf,L3OUT_NAME,L3OUT_DOMAIN,L3OUT_SUBNETS_NAME,PRI_Node_ID,PRI_PORT,SVI_VLAN,PRI_SVI_IP,MTU,PRI_ROUTER_ID)
     t22=FABRIC.L3OUT_GW_IP(tn,L3OUT_NAME,PRI_Node_ID,PRI_PORT,SVI_GW_IP) 
     t23=FABRIC.L3OUT_Static(tn,L3OUT_NAME,PRI_Node_ID,Dest_Network,Next_hop)
     t20_1=FABRIC.L3OUT_Config(tn,vrf,L3OUT_NAME,L3OUT_DOMAIN,L3OUT_SUBNETS_NAME,SEC_Node_ID,SEC_PORT,SVI_VLAN,SEC_SVI_IP,MTU,SEC_ROUTER_ID)
     t22_1=FABRIC.L3OUT_GW_IP(tn,L3OUT_NAME,SEC_Node_ID,SEC_PORT,SVI_GW_IP) 
     t23_1=FABRIC.L3OUT_Static(tn,L3OUT_NAME,SEC_Node_ID,Dest_Network,Next_hop)
     t24=FABRIC.L3OUT_Subnets(tn,L3OUT_NAME,L3OUT_SUBNETS_NAME,Dest_Network)
     t25=FABRIC.Contract(tn,Contract_name,Contract_sub,Contract_Scope)
     t26=FABRIC.Prov_Contract(tn,L3OUT_NAME,Contract_name,Provider_EPG)
     t27=FABRIC.Cons_Contract(tn,Contract_name,APP,Consumer_EPG)
    
    elif ACTION in ("n","no","N","No"):
      print("Ending the script")
    else: 
      print("Please enter yes or no.")

 
if __name__ == '__main__':
    main()