def main():
    import getpass
    import csv
    from FW_GW_project_Master import Client
    usr="admin"
    pwd = "!@#CiScO123"
    input_file = csv.DictReader(open("data.csv",encoding="utf-8-sig"))
    for data in input_file:
     host=(data["Fabric_Host_IP"])
     Datacenter = (data["Datacenter"])
     tn = (data["Tenant_Name"])
     bd=(data["EPG"])
     Subnet= (data["Subnet"])
     L3OUT_NAME = bd
     Contract_name = bd+"_ct"
     print("")
     print("Logging into **{} ** ACI FABRIC Controller IP:{}".format(Datacenter,host))
     print("")
     print("Rollback the Tenant Configuration: {}".format(tn))
     print("Rollback the EPG Configurtion : {}".format(bd))
     print("Rollback the L3->L2 EPG/BD,L3OUT,Contract Configurtion")

    ACTION = input("Are you sure you want to push the configuration (y/n): ")

    if ACTION in ("y","yes","Y","YES"): 
     FABRIC=Client(host, usr, pwd)
     print("Calling the Master function -> Authenticating into the Controller")
     FABRIC.login()
     t19=FABRIC.bd_L2(tn,bd)
     t28=FABRIC.Del_L3OUT(tn,L3OUT_NAME)
     t29=FABRIC.Del_Contract(tn,Contract_name)
    elif ACTION in ("n","no","N","No"):
      print("Ending the script")
    else: 
      print("Please enter yes or no.")

 
if __name__ == '__main__':
    main()