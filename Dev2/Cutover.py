def main():
    import getpass
    import csv
    from FW_GW_project_Master import Client
    host = "172.X.X.X"
    usr="admin"
    pwd = "!@####"
    input_file = csv.DictReader(open("data.csv",encoding="utf-8-sig"))
    for data in input_file:
     host=(data["Fabric_Host_IP"])
     Datacenter = (data["Datacenter"])
     tn = (data["Tenant_Name"])
     bd=(data["EPG"])
     vrf = bd
     Subnet=(data["Subnet"])
     Scope =""
     print("")
     print("Logging into **{} ** ACI FABRIC Controller IP:{}".format(Datacenter,host))
     print("")
     print("Configure the Tenant on:{}".format(tn))
     print("Configure the L2->L3 BD/EPG Name:{}".format(bd))
     print("Configure the L3 Subnet on EPG Name:{}".format(Subnet))
     print("")
    ACTION = input("Are you sure you want to push the configuration (y/n): ")

    if ACTION in ("y","yes","Y","YES"): 
     #FABRIC=Client(cfg.host, cfg.usr, cfg.pwd)
     FABRIC=Client(host, usr, pwd)
     print("Calling the Master function -> Authenticating into the Controller")
     FABRIC.login()
     t3=FABRIC.bd_Subnet(tn,bd,Subnet,Scope)
     t2=FABRIC.VRF_bd(tn,vrf,bd)
        
    

    elif ACTION in ("n","no","N","No"):
      print("Ending the script")
    else: 
      print("Please enter yes or no.")

 
if __name__ == '__main__':
    main()
