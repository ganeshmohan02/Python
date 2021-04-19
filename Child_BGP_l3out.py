def main():
    import getpass
    from Master_Parent import Client
    host = input("Enter the Fabric Controller IP/Hostname Ex:172.19.254.4 :")
    usr = input("Enter the Fabric username admin:")
    pwd = getpass.getpass(prompt="Enter the password:")
    tn = input("Enter the Tenant Name:")
    vrf = input("Enter the VRF Name:")
    bd = input("Enter the Bridge_ID Name:")
    L3OUT_NAME = input("Enter the L3OUT Name:")
    L3OUT_DOMAIN = input("Enter the L3OUT Domain Name ex:L3Dom:")
    EXTERNAL_SUBNETS_NAME = input("Enter the L3OUT EXTERNAL_SUBNETS_NAME:")
    Node_ID = input("Enter the Leaf/Node_ID :")
    PORT = input("Enter the Ethernet interface 1/X :")
    SVI_VLAN = input("Enter the .1Q SVI_VLAN#:")
    SVI_PRI_IP = input("Enter the SVI Primary_IP address/Mask:")
    SVI_SEC_IP = input("Enter the SVI Secondary_IP address/Mask:")
    ROUTER_ID = input("Enter the unique ROUTER_ID per Node:")
    MTU = input("Enter the MTU Size:")
    BGP_Peer_IP = input("Enter the BGP_Neigbor_IP:")
    REMOTE_ASN = input("Enter the BGP REMOTE_ASN:")
    LOCAL_ASN = input("Enter the BGP LOCAL_ASN:")

    ACTION = input("Are you sure you want to push the configuration (y/n): ")

    if ACTION in ("y","yes","Y","YES"): 
     #FABRIC=Client(cfg.host, cfg.usr, cfg.pwd)
     FABRIC=Client(host, usr, pwd)
     print("Calling the Master function -> Authenticating into the Controller")
     FABRIC.login()
     t1=FABRIC.tenant(tn,vrf,bd)
     t20=FABRIC.L3OUT_BGPRAS(tn,vrf,L3OUT_NAME,L3OUT_DOMAIN,EXTERNAL_SUBNETS_NAME,Node_ID,PORT,SVI_VLAN,SVI_PRI_IP,MTU,BGP_Peer_IP,ROUTER_ID,REMOTE_ASN)
     t21=FABRIC.L3OUT_BGPLAS(tn,L3OUT_NAME,Node_ID,PORT,BGP_Peer_IP,LOCAL_ASN)
     t22=FABRIC.L3OUT_SEC_IP(tn,L3OUT_NAME,Node_ID,PORT,SVI_SEC_IP) 
    elif ACTION in ("n","no","N","No"):
      print("Ending the script")
    else: 
      print("Please enter yes or no.")

 
if __name__ == '__main__':
    main()