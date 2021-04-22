import requests
import json
from string import Template
requests.urllib3.disable_warnings()
"""
Author: Ganesh Mohan
Date: 12/23/2020
Purpose: Send API calls to APIC and print status 
Version: 1.3
"""

class AuthenticationError(Exception):
    pass
class Client:
    def __init__(self, host, usr, pwd):
        #self.jar = requests.cookies.RequestsCookieJar()
        self.host = host
        self.usr = usr
        self.pwd = pwd
        self.client = requests.Session() 
#Pushing the configuration in the APIC controller   
    def POST(self, url, data,Role):
        response= self.client.post('https://%s%s' % (self.host, url),data=json.dumps(data),timeout=5,verify=False)
        resp=response.text
        if 'error' in resp:
          print("\n!!!!{}: Config already exist or config issue..Code{}\n".format(Role,response))
          print("!!!!Error code:{}\n".format(resp))
          #raise AuthenticationError
        else:
          print(">>>>{}:>>>>>Done # Status Code>{}".format(Role,response))
        return response
#Pulling the data in the APIC controller        
    def get(self, url):
        print("getting into the controller:{}".format(url))
        r=self.client.get('https://%s%s' % (self.host, url),timeout=5,verify=False)
        print("get response {}".format(r))
        return r
#Login into APIC using static Credentials.
    def login(self):
        data = {"aaaUser": {"attributes": {"name": self.usr, "pwd": self.pwd}}}
        res= self.client.post('https://%s/api/aaaLogin.json' % (self.host),data=json.dumps(data),timeout=5,verify=False)
        print(res)
        if res.status_code != 200 or 'error' in res.json()['imdata'][0]:
            raise AuthenticationError


#T1:Create Tenant,VRF
    def tenant(self,Tname,VRF):
        Role='T1:Create/Modifying the tenant:{},VRF:{}'.format(Tname,VRF)
        print("\n Logining into the tenant:{}\n".format(Tname))
        data = { "fvTenant":{"attributes":{"dn":"uni/tn-"+Tname,"status":"created,modified"},"children":[
               #{"fvBD":{"attributes":{"dn":"uni/tn-"+Tname+"/BD-"+BD+"_bd","name":BD+"_bd","arpFlood":"true","unicastRoute":"true","rn":"BD-"+BD+"_bd","status":"created,modified"},
               #"children":[{"fvRsCtx":{"attributes":{"tnFvCtxName":VRF+"_vrf","status":"created,modified"},"children":[]   }}],
               {"fvCtx":{"attributes":{"dn":"uni/tn-"+Tname+"/ctx-"+VRF+"_vrf","name": VRF+"_vrf","rn":"ctx-"+VRF+"_vrf","status":"created,modified"},"children":[]
              }}]}}
        return self.POST('/api/mo/uni/tn-{}.json'.format(Tname), data,Role)

    def VRF_bd(self,Tname,VRF,BD):
        Role='T3: Associate BD:{} into VRF:{} in Tenant {}'.format(BD,VRF,Tname)
        #print("\nCreating the tenant:{}\n".format(Tname))
        data = { "fvTenant":{"attributes":{"dn":"uni/tn-"+Tname,"status":"created,modified"},"children":[
               {"fvBD":{"attributes":{"dn":"uni/tn-"+Tname+"/BD-"+BD+"_bd","name":BD+"_bd","arpFlood":"false","unkMacUcastAct":"proxy","unicastRoute":"true","rn":"BD-"+BD+"_bd","status":"created,modified"},
               "children":[{"fvRsCtx":{"attributes":{"tnFvCtxName":VRF+"_vrf","status":"created,modified"},"children":[]   }}]}},
               {"fvCtx":{"attributes":{"dn":"uni/tn-"+Tname+"/ctx-"+VRF+"_vrf","name": VRF+"_vrf","rn":"ctx-"+VRF+"_vrf","status":"created,modified"},"children":[]
              }}]}}
        return self.POST('/api/mo/uni/tn-{}.json'.format(Tname), data,Role)    

#T2:Create L3 BD,Subnet and Scope of the subnet.
    def bd_Subnet(self,Tname,BD,Subnet,Scope):
        Role='T4: Creating the L3 BD:{} with Anycast GW:{} on Scope:{}'.format(BD,Subnet,Scope)
        scope_list = ['public', 'shared','private']
        if Scope in scope_list:
           data = {"fvSubnet": {"attributes": {"dn": "uni/tn-"+Tname+"/BD-"+BD+"_bd/subnet-["+Subnet+"]", "ctrl": "", "ip": Subnet, "rn": "subnet-["+Subnet+"]","scope":Scope, "status": "created,modified"},"children": [] } }
        else:
           data = {"fvSubnet": {"attributes": {"dn": "uni/tn-"+Tname+"/BD-"+BD+"_bd/subnet-["+Subnet+"]", "ctrl": "", "ip": Subnet, "rn": "subnet-["+Subnet+"]", "scope":"public,shared","status": "created,modified"},"children": [] } }
        return self.POST('/api/node/mo/uni/tn-{}/BD-{}_bd/subnet-[{}].json'.format(Tname,BD,Subnet), data,Role)

#T19 Create L2 BD domain.    
    def bd_L2(self,Tname,BD):
        Role="T19:{}-L2 BD domain(Flood/Unicast disabled):".format(BD)
        data = {"fvBD":{"attributes":{"dn":"uni/tn-"+Tname+"/BD-"+BD+"_bd","arpFlood":"true","unicastRoute":"false","unkMacUcastAct":"flood","status":"created,modified"},"children":[]}}
        return self.POST('/api/mo/uni/tn-{}/BD-{}_bd.json'.format(Tname,BD), data,Role)

#T20 Create L3OUT Primary IP & Secondary IP
    def L3OUT_Config(self,Tname,VRF,L3OUT_NAME,L3OUT_DOMAIN,L3OUT_SUBNETS,Node_ID,PORT,SVI_VLAN,SVI_IP,MTU,ROUTER_ID):
        Role="T20:Configure the {}_L3out on Node {}:".format(L3OUT_NAME,Node_ID)
        data = {"l3extOut":{"attributes":{"dn":"uni/tn-"+Tname+"/out-"+L3OUT_NAME,"name":L3OUT_NAME,"rn":"out-"+L3OUT_NAME,"status":"created,modified"},
               "children":[
               #{"l3extInstP":{"attributes":{"dn":"uni/tn-"+Tname+"/out-"+L3OUT_NAME+"/instP-"+L3OUT_SUBNETS,"name":L3OUT_SUBNETS,"rn":"instP-"+L3OUT_SUBNETS,"status":"created,modified"},"children":[{"l3extSubnet":{"attributes":{"dn":"uni/tn-"+Tname+"/out-"+L3OUT_NAME+"/instP-"+L3OUT_SUBNETS+"/extsubnet-[0.0.0.0/0]","ip":"0.0.0.0/0","status":"created,modified"},"children":[]}}]}},
               {"l3extInstP":{"attributes":{"dn":"uni/tn-"+Tname+"/out-"+L3OUT_NAME+"/instP-"+L3OUT_SUBNETS,"name":L3OUT_SUBNETS,"rn":"instP-"+L3OUT_SUBNETS,"status":"created,modified"},"children":[]}},
               {"l3extLNodeP":{"attributes":{"dn":"uni/tn-"+Tname+"/out-"+L3OUT_NAME+"/lnodep-"+L3OUT_NAME+"_nodeProfile","name":L3OUT_NAME+"_nodeProfile","status":"created,modified"},
               "children":[{"l3extLIfP":{"attributes":{"dn":"uni/tn-"+Tname+"/out-"+L3OUT_NAME+"/lnodep-"+L3OUT_NAME+"_nodeProfile/lifp-"+L3OUT_NAME+"_interfaceProfile","name":L3OUT_NAME+"_interfaceProfile","status":"created,modified"},
               "children":[{"l3extRsPathL3OutAtt":{"attributes":{"dn":"uni/tn-"+Tname+"/out-"+L3OUT_NAME+"/lnodep-"+L3OUT_NAME+"_nodeProfile/lifp-"+L3OUT_NAME+"_interfaceProfile/rspathL3OutAtt-[topology/pod-1/paths-"+Node_ID+"/pathep-[eth"+PORT+"]]","tDn":"topology/pod-1/paths-"+Node_ID+"/pathep-[eth"+PORT+"]","addr":SVI_IP,"ifInstT":"ext-svi","mtu":MTU,"encap":"vlan-"+SVI_VLAN,"status":"created,modified","rn":"rspathL3OutAtt-[topology/pod-1/paths-"+Node_ID+"/pathep-[eth"+PORT+"]]"},
               "children":[] }}]}},
               {"l3extRsNodeL3OutAtt":{"attributes":{"dn":"uni/tn-"+Tname+"/out-"+L3OUT_NAME+"/lnodep-"+L3OUT_NAME+"_nodeProfile/rsnodeL3OutAtt-[topology/pod-1/node-"+Node_ID+"]","tDn":"topology/pod-1/node-"+Node_ID,"rtrId":ROUTER_ID,"rtrIdLoopBack":"false","status":"created,modified"},
               "children":[]}}]}},
               {"l3extRsEctx":{"attributes":{"tnFvCtxName":VRF+"_vrf","status":"created,modified"},"children":[]}},{"l3extRsL3DomAtt":{"attributes":{"tDn":"uni/l3dom-"+L3OUT_DOMAIN,"status":"created,modified"},"children":[]}}]}}
        return self.POST('/api/node/mo/uni/tn-{}/out-{}.json'.format(Tname,L3OUT_NAME), data,Role)

    def L3OUT_GW_IP(self,Tname,L3OUT_NAME,Node_ID,PORT,SVI_GW_IP):
        Role="T21:Configure the GW IP Address on {}_L3OUT for Node {}:".format(L3OUT_NAME,Node_ID)
        data = {"l3extIp":{"attributes":{"addr":SVI_GW_IP,"status":"created,modified"},"children":[]}}  
        return self.POST('/api/node/mo/uni/tn-{}/out-{}/lnodep-{}_nodeProfile/lifp-{}_interfaceProfile/rspathL3OutAtt-[topology/pod-1/paths-{}/pathep-[eth{}]].json'.format(Tname,L3OUT_NAME,L3OUT_NAME,L3OUT_NAME,Node_ID,PORT),data,Role)

#T22 Create Static L3OUT
    def L3OUT_Static(self,Tname,L3OUT_NAME,Node_ID,Dest_Network,Next_hop):
            Role=  "T22:{}-L3 Static Route Configure Network {} as Next-hop:{} on Node {}:".format(L3OUT_NAME,Dest_Network,Next_hop,Node_ID)
            data=  {"ipRouteP":{"attributes":{"dn":"uni/tn-"+Tname+"/out-"+L3OUT_NAME+"/lnodep-"+L3OUT_NAME+"_nodeProfile/rsnodeL3OutAtt-[topology/pod-1/node-"+Node_ID+"]/rt-["+Dest_Network+"]","ip":Dest_Network,"rn":"rt-["+Dest_Network+"]","status":"created,modified"},
                    "children":[{"ipNexthopP":{"attributes":{"dn":"uni/tn-"+Tname+"/out-"+L3OUT_NAME+"/lnodep-"+L3OUT_NAME+"_nodeProfile/rsnodeL3OutAtt-[topology/pod-1/node-"+Node_ID+"]/rt-["+Dest_Network+"]/nh-["+Next_hop+"]","nhAddr":Next_hop,"rn":"nh-["+Next_hop+"]","status":"created,modified"},"children":[]}}]}}
            return self.POST('/api/node/mo/uni/tn-{}/out-{}/lnodep-{}_nodeProfile/rsnodeL3OutAtt-[topology/pod-1/node-{}]/rt-[{}].json'.format(Tname,L3OUT_NAME,L3OUT_NAME,Node_ID,Dest_Network), data,Role)
  #T23 Create Static L3OUT  
    def L3OUT_Subnets(self,Tname,L3OUT_NAME,L3OUT_SUBNETS,Dest_Network):  
        Role=  "T23:{}-L3out Subnets for Network {}:".format(L3OUT_NAME,Dest_Network)
        Dest_Network_list = ['0.0.0.0/0']
        if Dest_Network in Dest_Network_list:
           data= {"l3extSubnet":{"attributes":{"dn":"uni/tn-"+Tname+"/out-"+L3OUT_NAME+"/instP-"+L3OUT_SUBNETS+"/extsubnet-["+Dest_Network+"]","ip":Dest_Network,"scope":"import-security,shared-security,shared-rtctrl","aggregate":"shared-rtctrl","rn":"extsubnet-["+Dest_Network+"]","status":"created,modified"},"children":[]}}
        else:
           data= {"l3extSubnet":{"attributes":{"dn":"uni/tn-"+Tname+"/out-"+L3OUT_NAME+"/instP-"+L3OUT_SUBNETS+"/extsubnet-["+Dest_Network+"]","ip":Dest_Network,"scope":"import-security,shared-security,shared-rtctrl","aggregate":"","rn":"extsubnet-["+Dest_Network+"]","status":"created,modified"},"children":[]}}
        return self.POST('/api/node/mo/uni/tn-{}/out-{}/instP-{}/extsubnet-[{}].json'.format(Tname,L3OUT_NAME,L3OUT_SUBNETS,Dest_Network),data,Role)
  
#T24 Create Contract
    def Contract(self,Tname,Contract_name,Contract_sub,Scope):
        Role=  "T24:Create Contract {} under Tenant {}:".format(Contract_name,Tname)
        scope_list = ['tenant','global']
        if Scope in scope_list:
            data ={"vzBrCP":{"attributes":{"dn":"uni/tn-"+Tname+"/brc-"+Contract_name,"name":Contract_name,"scope":Scope,"rn":"brc-"+Contract_name,"status":"created,modified"},
              "children":[{"vzSubj":{"attributes":{"dn":"uni/tn-"+Tname+"/brc-"+Contract_name+"/subj-"+Contract_sub+"","name":Contract_sub,"rn":"subj-"+Contract_sub,"status":"created,modified"},
              "children":[{"vzRsSubjFiltAtt":{"attributes":{"status":"created,modified","tnVzFilterName":"default","directives":"none"},"children":[]}}]}}]}}
        else:
          data ={"vzBrCP":{"attributes":{"dn":"uni/tn-"+Tname+"/brc-"+Contract_name,"name":Contract_name,"rn":"brc-"+Contract_name,"status":"created,modified"},
              "children":[{"vzSubj":{"attributes":{"dn":"uni/tn-"+Tname+"/brc-"+Contract_name+"/subj-"+Contract_sub+"","name":Contract_sub,"rn":"subj-"+Contract_sub,"status":"created,modified"},
              "children":[{"vzRsSubjFiltAtt":{"attributes":{"status":"created,modified","tnVzFilterName":"default","directives":"none"},"children":[]}}]}}]}}    
        return self.POST('/api/node/mo/uni/tn-{}/brc-{}.json'.format(Tname,Contract_name),data,Role)

#T25 Provider Contract
    def Prov_Contract(self,Tname,L3OUT_NAME,Contract_name,P_EPG):
        Role=  "T25:Apply the Provider Contract under EPG {}:".format(P_EPG) 
        data={"fvRsProv":{"attributes":{"tnVzBrCPName":Contract_name,"status":"created,modified"},"children":[]}}
        return self.POST('/api/node/mo/uni/tn-{}/out-{}/instP-{}.json'.format(Tname,L3OUT_NAME,P_EPG),data,Role)
#T26 Consumer Contract    
    def Cons_Contract(self,Tname,Contract_name,APP,C_EPG):
        Role=  "T27:Apply the Consumer Contract under EPG {}:".format(C_EPG)
        data ={"fvRsCons":{"attributes":{"tnVzBrCPName":Contract_name,"status":"created,modified"},"children":[]}}
        return self.POST('/api/node/mo/uni/tn-{}/ap-{}/epg-{}.json'.format(Tname,APP,C_EPG),data,Role)


# T28 Rollback Plan: Delete the L3OUT.
    def Del_L3OUT(self,Tname,L3OUT_NAME):
        Role=  "T28:Rollback the L3OUT configuration:{} on Tenant:{}".format(L3OUT_NAME,Tname)
        data ={"l3extOut":{"attributes":{"dn":"uni/tn-"+Tname+"/out-"+L3OUT_NAME,"status":"deleted"},"children":[]}}
        return self.POST('/api/node/mo/uni/tn-{}/out-{}.json'.format(Tname,L3OUT_NAME),data,Role)

# T29 Rollback Plan: Delete the Contract.
    def Del_Contract(self,Tname,Contract_name):
        Role= "T29:Rollback the {} Contract on Tenant {}:".format(Contract_name,Tname)
        data={"vzBrCP":{"attributes":{"dn":"uni/tn-"+Tname+"/brc-"+Contract_name,"status":"deleted"},"children":[]}}
        return self.POST('/api/node/mo/uni/tn-{}/brc-{}.json'.format(Tname,Contract_name),data,Role)
   

def main():

    import apic_cfg as cfg
    client = Client(cfg.host, cfg.usr, cfg.pwd)
    print("\n Authenication in to the controller: {}\n".format(cfg.host))
    client.login()
    
if __name__ == '__main__':
    main()
