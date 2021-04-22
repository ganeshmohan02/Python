def main():
    import getpass
    import csv
    from FW_GW_project_Master import Client
    #host = "172.19.254.4"
    usr="admin"
    pwd = "!@#CiScO123"
    #tn = "HNSEC_FW_GW"
    input_file = csv.DictReader(open("data.csv",encoding="utf-8-sig"))
    for data in input_file:
     host=(data["Fabric_Host_IP"])
     Datacenter = (data["Datacenter"])
     tn = (data["Tenant_Name"])
     EPG=(data["EPG"])
     SVI_VLAN=(data["SVI_VLAN"])
     PRI_Node_ID=(data["PRI_Node_ID"])
     SEC_Node_ID=(data["SEC_Node_ID"])
     PRI_PORT=(data["PRI_PORT"])
     SEC_PORT=(data["SEC_PORT"])
     PRI_SVI_IP1=(data["PRI_SVI_IP"])
     PRI_SVI_IP = PRI_SVI_IP1+"/29"
     SEC_SVI_IP1=(data["SEC_SVI_IP"])
     SEC_SVI_IP =SEC_SVI_IP1+"/29"
     SVI_GW_IP1=(data["SVI_GW_IP"])
     SVI_GW_IP = SVI_GW_IP1+"/29"
     Next_hop=(data["Next_hop"])
     Dest_Network =(data["Dest_Network"])
     Contract_Scope = (data["Contract_Scope"])
     APP= (data["APP_Profile_Name"])
     MTU = (data["MTU"])
     L3OUT_DOMAIN = (data["L3OUT_DOMAIN"])
     vrf = EPG
     L3OUT_NAME = EPG
     L3OUT_SUBNETS_NAME = L3OUT_NAME+"_Ext_Network"
     PRI_ROUTER_ID = PRI_Node_ID+"."+PRI_Node_ID+"."+PRI_Node_ID+"."+SVI_VLAN
     SEC_ROUTER_ID = SEC_Node_ID+"."+SEC_Node_ID+"."+SEC_Node_ID+"."+SVI_VLAN
     Consumer_EPG = EPG+"_EPG"
    #Subnet = "192.168.4.1/24"
     Provider_EPG = L3OUT_SUBNETS_NAME
     Contract_name = EPG+"_ct"
     Contract_sub = Contract_name+"_sub"
     print ("")
     print("Logging into **{} ** ACI FABRIC Controller IP:{}".format(Datacenter,host))
     print("Configure the Tenant Configure on:{}".format(tn))
     print("Configure the VRF/EPG Name:{}".format(vrf))
     print("Configure the .1Q SVI_VLAN ID#:{}".format(SVI_VLAN))
     print("Configure the Leaf PRI_Node_ID Ex:1XX:{}".format(PRI_Node_ID))
     print("Configure the Leaf SEC_Node_ID Ex:1YY: {}".format(SEC_Node_ID))
     print("Configure the Ethernet interface on PRI_Node_Port:{}".format(PRI_PORT))
     print("Configure the Ethernet interface on SEC_Node_Port:{}".format(SEC_PORT))
     print("Configure the SVI Primary_IP for PRI_Node:{}".format(PRI_SVI_IP))
     print("Configure the SVI Second._IP for SEC_Node:{}".format(SEC_SVI_IP))
     print("Configure the SVI GW_IP on PRI_SEC_Node:{}".format(SVI_GW_IP))
     print("Configure the FW/RTR L3out NEXT_HOP IP_Address:{}".format(Next_hop))
     print("Configure the Destination Network :{}".format(Dest_Network))
     print ("")
     print("Configure the Primary Node ROUTER_ID:{}".format(PRI_ROUTER_ID))
     print("Configure the Second Node ROUTER_ID:{}".format(SEC_ROUTER_ID))
     print("Configure the MTU value :{}".format(MTU))
     print("Configure the Application Profile Name:{}".format(APP))
     print ("")
     #print ("************Contract information****")
     print("Configure the Contract Name :{}".format(Contract_name))
     print("Configure the Contract Scope :{}".format(Contract_Scope))
     print("Configure the Consumer contract on EPG :{}".format(Consumer_EPG))
     print("Configure the Provider contract on EPG :{}".format(Provider_EPG))
     print ("")
  
    ACTION = input("Are you sure you want to push the above configuration (y/n): ")

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