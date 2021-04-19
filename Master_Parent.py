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


#T1:Create Tenant,VRF and L3 BD.
    def tenant(self,Tname,VRF,BD):
        Role='T1:tenant:{},VRF:{},L3_BD:{}'.format(Tname,VRF,BD)
        print("\nCreating the tenant:{}\n".format(Tname))
        data = { "fvTenant":{"attributes":{"dn":"uni/tn-"+Tname,"status":"created,modified"},"children":[
               {"fvBD":{"attributes":{"dn":"uni/tn-"+Tname+"/BD-"+BD+"_bd","name":BD+"_bd","arpFlood":"true","unicastRoute":"true","rn":"BD-"+BD+"_bd","status":"created,modified"},
               "children":[{"fvRsCtx":{"attributes":{"tnFvCtxName":VRF+"_vrf","status":"created,modified"},"children":[]   }}]}},
               {"fvCtx":{"attributes":{"dn":"uni/tn-"+Tname+"/ctx-"+VRF+"_vrf","name": VRF+"_vrf","rn":"ctx-"+VRF+"_vrf","status":"created,modified"},"children":[]
              }}]}}
        return self.POST('/api/mo/uni/tn-{}.json'.format(Tname), data,Role)
#T2:Create L3 BD,Subnet and Scope of the subnet.
    def bd_Subnet(self,Tname,BD,Subnet,Scope):
        Role='T2: Creating the L3 BD:{} with Anycast GW:{} on Scope:{}'.format(BD,Subnet,Scope)
        scope_list = ['public', 'shared','private']
        if Scope in scope_list:
           data = {"fvSubnet": {"attributes": {"dn": "uni/tn-"+Tname+"/BD-"+BD+"_bd/subnet-["+Subnet+"]", "ctrl": "", "ip": Subnet, "rn": "subnet-["+Subnet+"]","scope":Scope, "status": "created,modified"},"children": [] } }
        else:
           data = {"fvSubnet": {"attributes": {"dn": "uni/tn-"+Tname+"/BD-"+BD+"_bd/subnet-["+Subnet+"]", "ctrl": "", "ip": Subnet, "rn": "subnet-["+Subnet+"]", "status": "created"},"children": [] } }
        return self.POST('/api/node/mo/uni/tn-{}/BD-{}_bd/subnet-[{}].json'.format(Tname,BD,Subnet), data,Role)
#T3:Create APP policy.    
    def app_profile(self,Tname,APP):
        Role="T3:{}-Application profile:".format(APP)
        data = {"fvAp":{"attributes":{"dn":"uni/tn-"+Tname+"/ap-"+APP+"_ap","name":APP+"_ap","rn":"ap-"+APP+"_ap","status":"created,modified"},"children":[] }}
        return self.POST('/api/mo/uni/tn-{}/ap-{}_ap.json'.format(Tname,APP), data,Role)
#T4:Create EPG and assoicate the BD. 
    def epg(self,Tname,BD,APP,EPG):
        Role="T4:EPG:{}".format(EPG)
        data = {"fvAEPg":{"attributes":{"dn":"uni/tn-"+Tname+"/ap-"+APP+"_ap/epg-"+EPG+"_epg","name":EPG+"_epg","rn":"epg-"+EPG+"_epg","status":"created,modified"},
        "children":[{"fvRsBd":{"attributes":{"tnFvBDName":BD+"_bd","status":"created,modified"},"children":[] }}]}}
        return self.POST('/api/mo/uni/tn-{}/ap-{}_ap.json'.format(Tname,APP), data,Role)
#T5 Create Static vlan pool. Domain is mapped 1:1 to vlan.
    def Static_vlan(self,VLAN_NAME,VLAN_ID): 
        Role="T5: Static vlan:{}".format(VLAN_ID)
        data = {"fvnsVlanInstP":{"attributes":{"dn":"uni/infra/vlanns-["+VLAN_NAME+"_vlans]-static","name":VLAN_NAME+"_vlans",
               "allocMode":"static","rn":"vlanns-["+VLAN_NAME+"_vlans]-static","status":"created"},
           "children":[
                 {"fvnsEncapBlk":{"attributes":{"dn":"uni/infra/vlanns-["+VLAN_NAME+"_vlans]-static/from-[vlan-"+VLAN_ID+"]-to-[vlan-"+VLAN_ID+"]",
                  "from":"vlan-"+VLAN_ID,"to":"vlan-"+VLAN_ID,"rn":"from-[vlan-"+VLAN_ID+"]-to-[vlan-"+VLAN_ID+"]","status":"created,modified"},
               "children":[]
            }}]}}
        return self.POST('/api/node/mo/uni/infra/vlanns-[{}_vlans]-static.json'.format(VLAN_NAME), data,Role)
#T6 Create physical domain. Domain is mapped 1:1 to vlan.
    def PhysDomain(self,PHY_D,VLAN_NAME): 
        Role="T6:Physical Domain:{}".format(PHY_D)
        #url='https://{}/api/node/mo/uni/phys-PHY_D_phys.json'.format(APIC)
        data= {"physDomP":{"attributes":{"dn":"uni/phys-"+PHY_D+"_phys","name":PHY_D+"_phys","rn":"phys-"+PHY_D+"_phys","status":"created,modified"},
          "children":[ {"infraRsVlanNs":{ "attributes":{"tDn":"uni/infra/vlanns-["+VLAN_NAME+"_vlans]-static","status":"created,modified"},"children":[]
            }}]}}
        return self.POST('/api/node/mo/uni/phys-{}_phys.json'.format(PHY_D), data,Role)
#T7 Attach EPG to bare metal/Physical domain
    def AttPhyEPG(self,Tname,PHY_D,APP,EPG):
        Role="T7: Attaching the Physical domain :{} into EPG: {}".format(PHY_D,EPG)
        data = {"fvRsDomAtt":{"attributes":{"resImedcy":"immediate","tDn":"uni/phys-"+PHY_D+"_phys","status":"created"},"children":[]}}
        return self.POST('/api/node/mo/uni/tn-{}/ap-{}_ap/epg-{}_epg.json'.format(Tname,APP,EPG), data,Role)
#T8 Configure the Leaf_ID_FROM as a Trunk Interface
    def EpgStaticPort(self,Tname,APP,EPG,LEAF_ID_FROM,LEAF_ID_TO,PORT,VLAN,Mode):
        if Mode == "Trunk" or Mode == "trunk":
        #Configure the Leaf_ID_FROM as a Trunk Interface
           Role="T8.1: Enabling Trunk interface vlan {} on Leaf_ID:{} on port eth1/{} into EPG: {}".format(VLAN,LEAF_ID_FROM,PORT,EPG)
           data = { "fvRsPathAtt":{"attributes":{"encap":"vlan-"+VLAN,"instrImedcy":"immediate","tDn":"topology/pod-1/paths-"+LEAF_ID_FROM+"/pathep-[eth1/"+PORT+"]","status":"created"},"children":[] } }
           self.POST('/api/node/mo/uni/tn-{}/ap-{}_ap/epg-{}_epg.json'.format(Tname,APP,EPG), data,Role) 
        #Configure the Leaf_ID_TO as a Trunk Interface
           Role="T8.2: Enabling Trunk interface vlan {} on Leaf_ID:{} on port eth1/{} into EPG: {}".format(VLAN,LEAF_ID_TO,PORT,EPG)
           data = { "fvRsPathAtt":{"attributes":{"encap":"vlan-"+VLAN,"instrImedcy":"immediate","tDn":"topology/pod-1/paths-"+LEAF_ID_TO+"/pathep-[eth1/"+PORT+"]","status":"created"},"children":[] } }
           return self.POST('/api/node/mo/uni/tn-{}/ap-{}_ap/epg-{}_epg.json'.format(Tname,APP,EPG), data,Role) 
        elif Mode == "Access" or Mode == "access":
        #Configure the Leaf_ID_FROM as a Access Interface
           Role="T8.3: Enabling Access interface vlan {} on Leaf_ID:{} on port eth1/{} into EPG: {}".format(VLAN,LEAF_ID_FROM,PORT,EPG)
           data = {"fvRsPathAtt":{"attributes":{"encap":"vlan-"+VLAN,"mode":"native","instrImedcy":"immediate","tDn":"topology/pod-1/paths-"+LEAF_ID_FROM+"/pathep-[eth1/"+PORT+"]","status":"created"},"children":[]}}
           self.POST('/api/node/mo/uni/tn-{}/ap-{}_ap/epg-{}_epg.json'.format(Tname,APP,EPG), data,Role)
        #Configure the Leaf_ID_TO as a Access Interface
           Role="T8.4: Enabling Access interface vlan {} on Leaf_ID:{} on port eth1/{} into EPG: {}".format(VLAN,LEAF_ID_TO,PORT,EPG)
           data = {"fvRsPathAtt":{"attributes":{"encap":"vlan-"+VLAN,"mode":"native","instrImedcy":"immediate","tDn":"topology/pod-1/paths-"+LEAF_ID_TO+"/pathep-[eth1/"+PORT+"]","status":"created"},"children":[]}}
           return self.POST('/api/node/mo/uni/tn-{}/ap-{}_ap/epg-{}_epg.json'.format(Tname,APP,EPG), data,Role)
        else:
            Print("Please specify interface mode as : access or trunk ")
#T9 Create/Verify AAEP
    def AAEP(self,AAEP): 
        Role="T9: Creating AAEP:{}".format(AAEP)
        data = {"infraAttEntityP":{"attributes":{"dn":"uni/infra/attentp-"+AAEP+"_aaep","name":AAEP+"_aaep","rn":"attentp-"+AAEP+"_aaep","status":"created,modified"},"children":[  ] } } 
        return self.POST('/api/node/mo/uni/infra/attentp-{}_aaep.json'.format(AAEP),data,Role)
#T10 AAEP attaching with Physical domain    
    def AAEPPhy(self,AAEP,PHY_D):
        Role="T10: Attaching the AAEP:{} and physical domain:{}".format(AAEP,PHY_D)
        data = {"infraRsDomP":{"attributes":{"tDn":"uni/phys-"+PHY_D+"_phys","status":"created,modified"},"children":[]}}
        return self.POST('/api/node/mo/uni/infra/attentp-{}_aaep.json'.format(AAEP), data,Role)
#T11 Create switch profile
    def Switch_pro(self,Switch_Prof,LEAF_ID_FROM,LEAF_ID_TO):
        Role="T11 Switch profile:{}".format(Switch_Prof)
        data ={ "infraNodeP":{ "attributes":{"dn":"uni/infra/nprof-"+Switch_Prof+"_leafProf","name":Switch_Prof+"_leafProf","rn":"nprof-"+Switch_Prof+"_leafProf","status":"created,modified"},
             "children":[{ "infraLeafS":{"attributes":{
             "dn":"uni/infra/nprof-"+Switch_Prof+"_leafProf/leaves-"+Switch_Prof+"_LeafSel-typ-range",
             "type":"range","name":Switch_Prof+"_LeafSel","rn":"leaves-"+Switch_Prof+"_LeafSel-typ-range","status":"created"},
             "children":[{"infraNodeBlk":{"attributes":{
                "dn":"uni/infra/nprof-"+Switch_Prof+"_leafProf/leaves-"+Switch_Prof+"_LeafSel-typ-range/nodeblk-f6ff793728a065ed",
             "from_":LEAF_ID_FROM,"to_":LEAF_ID_TO,"name":"f6ff793728a065ed","rn":"nodeblk-f6ff793728a065ed","status":"created"}, 
             "children":[] } } ] } } ] }}
        return self.POST('/api/node/mo/uni/infra/nprof-{}_leafProf.json'.format(Switch_Prof), data,Role)
#T12 Create interface profile
    def Interface_pro(self,Int_Prof,port):
        Role="T12: Interface profile:{} and port {}".format(Int_Prof,port)
        data= { "infraAccPortP":{"attributes":{"dn":"uni/infra/accportprof-"+Int_Prof+"_intProf","name":Int_Prof+"_intProf",
               "rn":"accportprof-"+Int_Prof+"_intProf","status":"created,modified"},
         "children":[{"infraHPortS":{"attributes":{
                    "dn":"uni/infra/accportprof-"+Int_Prof+"_intProf/hports-"+Int_Prof+"_port"+port+"-typ-range",
                    "name":Int_Prof+"_port"+port,"rn":"hports-"+Int_Prof+"_port"+port+"-typ-range","status":"created,modified"},
         "children":[{"infraPortBlk":{
              "attributes":{"dn":"uni/infra/accportprof-"+Int_Prof+"_intProf/hports-"+Int_Prof+"_port"+port+"-typ-range/portblk-block2",
                    "fromPort":port,"toPort":port,"name":"block2","rn":"portblk-block2","status":"created,modified"}, "children":[ ] } },
                   {"infraRsAccBaseGrp":{"attributes":{"status":"created,modified"}, "children":[  ] } } ] } } ] } }
        return self.POST('/api/node/mo/uni/infra/accportprof-{}_intProf.json'.format(Int_Prof), data,Role)
#T13 Associate interface profile to switch profile
    def IntP2SWP(self,Int_Prof,Switch_Prof):
        Role="T13: Associate interface profile:{} and switch profile {}".format(Int_Prof,Switch_Prof)  
        data ={"infraRsAccPortP":{"attributes":{"tDn":"uni/infra/accportprof-"+Int_Prof+"_intProf","status":"created,modified"},"children":[ ] }}
        return self.POST('/api/node/mo/uni/infra/nprof-{}_leafProf.json'.format(Switch_Prof), data,Role)
#T14 Switch profile modified to attach AAEP
    def IntP2AAEP(self,Int_Prof,AAEP):
        Role="T14: Attaching the interface profile:{} and AAEP {}".format(Int_Prof,AAEP) 
        data={ "infraAttEntityP":{"attributes":{"dn":"uni/infra/attentp-"+AAEP+"_aaep","name":AAEP+"_aaep","rn":"attentp-"+AAEP+"_aaep","status":"created,modified"},"children":[]  } }
        return self.POST('/api/node/mo/uni/infra/nprof-"+Int_Prof+"_leafProf.json'.format(Int_Prof), data,Role)
#T15 Create LLDP interface policy
    def LLDP(self,LLDP_ON):
        Role="T15: Creating LLDP profile."
        data = {"lldpIfPol":{"attributes":{"dn":"uni/infra/lldpIfP-"+LLDP_ON+"_lldplfPol","name":LLDP_ON+"_lldplfPol","rn":"lldpIfP-"+LLDP_ON+"_lldplfPol","status":"created,modified"},"children":[] } }
        return self.POST('/api/node/mo/uni/infra/lldpIfP-{}_lldplfPol.json'.format(LLDP_ON), data,Role)
#T16 Create L2 VLAN scope local policy
    def VLAN_SC_L(self,VSCOPEL):
        Role="T16: Creating L2 VLAN scope profile."
        data= { "l2IfPol":{ "attributes":{ "dn":"uni/infra/l2IfP-"+VSCOPEL+"_vlanScope","name":VSCOPEL+"_vlanScope", 
                             "vlanScope":"portlocal","rn":"l2IfP-"+VSCOPEL+"_vlanScope","status":"created,modified"},"children":[]}}
        return self.POST('/api/node/mo/uni/infra/l2IfP-{}_vlanScope.json'.format(VSCOPEL), data,Role)
#T17 Create the policy group and assign AAEP,LLDP and L2VLAN scope to policy group
    def POLICY_GP(self,POLICY,VSCOPEL,LLDP_ON,AAEP):
        Role="T17: Attaching the policy group:{} and AAEP {}".format(POLICY,AAEP) 
        data = {"infraAccPortGrp":{"attributes":{"dn":"uni/infra/funcprof/accportgrp-"+POLICY+"_polGrp","status":"created,modified"},
              "children":[{"infraRsL2IfPol":{"attributes":{ "tnL2IfPolName":VSCOPEL+"_vlanScope"},"children":[]}},
                          { "infraRsLldpIfPol":{"attributes":{"tnLldpIfPolName":LLDP_ON+"_lldplfPol"},"children":[] }},
                          { "infraRsAttEntP":{"attributes":{"tDn":"uni/infra/attentp-"+AAEP+"_aaep","status":"created,modified"},"children":[]}}
                         ] }}
        return self.POST('/api/node/mo/uni/infra/funcprof/accportgrp-{}_polGrp.json'.format(POLICY), data,Role)
#T18 Assign policy group to interface profile
    def GPolicy2IntP(self,Int_Prof,POLICY,port):
        Role="T18: Policy Group:{} and interface profile {}".format(POLICY,Int_Prof)
        data = {"infraRsAccBaseGrp":{"attributes":{ "tDn":"uni/infra/funcprof/accportgrp-"+POLICY+"_polGrp"},"children":[] } }
        return self.POST('/api/node/mo/uni/infra/accportprof-{}_intProf/hports-{}_port{}-typ-range/rsaccBaseGrp.json'.format(Int_Prof,Int_Prof,port), data,Role)
#T19 Create L2 BD domain.    
    def bd_L2(self,Tname,BD):
        Role="T19:{}-L2 BD domain(Flood/Unicast disabled):".format(BD)
        data = {"fvBD":{"attributes":{"dn":"uni/tn-"+Tname+"/BD-"+BD+"_bd","arpFlood":"true","unicastRoute":"false","unkMacUcastAct":"flood","status":"created,modified"},"children":[]}}
        return self.POST('/api/mo/uni/tn-{}/BD-{}_bd.json'.format(Tname,BD), data,Role)

#T20 Create L3OUT BGP and Remote AS.
    def L3OUT_BGPRAS(self,Tname,VRF,L3OUT_NAME,L3OUT_DOMAIN,L3OUT_SUBNETS,Node_ID,PORT,SVI_VLAN,SVI_PRI_IP,MTU,BGP_Peer_IP,ROUTER_ID,REMOTE_ASN):
        Role="T20:{}-L3 domain_BGP Configure Remote AS:".format(L3OUT_NAME)
        data = {"l3extOut":{"attributes":{"dn":"uni/tn-"+Tname+"/out-"+L3OUT_NAME,"name":L3OUT_NAME,"rn":"out-"+L3OUT_NAME,"status":"created,modified"},
               "children":[
               {"bgpExtP":{"attributes":{"dn":"uni/tn-"+Tname+"/out-"+L3OUT_NAME+"/bgpExtP","rn":"bgpExtP","status":"created,modified"},"children":[]}},
               {"l3extInstP":{"attributes":{"dn":"uni/tn-"+Tname+"/out-"+L3OUT_NAME+"/instP-"+L3OUT_SUBNETS,"name":L3OUT_SUBNETS,"rn":"instP-"+L3OUT_SUBNETS,"status":"created,modified"},"children":[{"l3extSubnet":{"attributes":{"dn":"uni/tn-"+Tname+"/out-"+L3OUT_NAME+"/instP-"+L3OUT_SUBNETS+"/extsubnet-[0.0.0.0/0]","ip":"0.0.0.0/0","status":"created,modified"},"children":[]}}]}},
               {"l3extLNodeP":{"attributes":{"dn":"uni/tn-"+Tname+"/out-"+L3OUT_NAME+"/lnodep-"+L3OUT_NAME+"_nodeProfile","name":L3OUT_NAME+"_nodeProfile","status":"created,modified"},
               "children":[{"l3extLIfP":{"attributes":{"dn":"uni/tn-"+Tname+"/out-"+L3OUT_NAME+"/lnodep-"+L3OUT_NAME+"_nodeProfile/lifp-"+L3OUT_NAME+"_interfaceProfile","name":L3OUT_NAME+"_interfaceProfile","status":"created,modified"},
               "children":[{"l3extRsPathL3OutAtt":{"attributes":{"dn":"uni/tn-"+Tname+"/out-"+L3OUT_NAME+"/lnodep-"+L3OUT_NAME+"_nodeProfile/lifp-"+L3OUT_NAME+"_interfaceProfile/rspathL3OutAtt-[topology/pod-1/paths-"+Node_ID+"/pathep-[eth"+PORT+"]]","tDn":"topology/pod-1/paths-"+Node_ID+"/pathep-[eth"+PORT+"]","addr":SVI_PRI_IP,"ifInstT":"ext-svi","mtu":MTU,"encap":"vlan-"+SVI_VLAN,"status":"created","rn":"rspathL3OutAtt-[topology/pod-1/paths-"+Node_ID+"/pathep-[eth"+PORT+"]]"},
               "children":[{"bgpPeerP":{"attributes":{"dn":"uni/tn-"+Tname+"/out-"+L3OUT_NAME+"/lnodep-"+L3OUT_NAME+"_nodeProfile/lifp-"+L3OUT_NAME+"_interfaceProfile/rspathL3OutAtt-[topology/pod-1/paths-"+Node_ID+"/pathep-[eth"+PORT+"]]/peerP-["+BGP_Peer_IP+"]","addr":BGP_Peer_IP,"status":"created,modified"},
               "children":[{"bgpAsP":{"attributes":{"dn":"uni/tn-"+Tname+"/out-"+L3OUT_NAME+"/lnodep-"+L3OUT_NAME+"_nodeProfile/lifp-"+L3OUT_NAME+"_interfaceProfile/rspathL3OutAtt-[topology/pod-1/paths-"+Node_ID+"/pathep-[eth"+PORT+"]]/peerP-["+BGP_Peer_IP+"]/as","asn":REMOTE_ASN,"status":"created,modified"},
               "children":[]  }}]}}]}}]}},
               {"l3extRsNodeL3OutAtt":{"attributes":{"dn":"uni/tn-"+Tname+"/out-"+L3OUT_NAME+"/lnodep-"+L3OUT_NAME+"_nodeProfile/rsnodeL3OutAtt-[topology/pod-1/node-"+Node_ID+"]","tDn":"topology/pod-1/node-"+Node_ID,"rtrId":ROUTER_ID,"rtrIdLoopBack":"false","status":"created,modified"},"children":[]}}]}},
               {"l3extRsEctx":{"attributes":{"tnFvCtxName":VRF+"_vrf","status":"created,modified"},"children":[]}},{"l3extRsL3DomAtt":{"attributes":{"tDn":"uni/l3dom-"+L3OUT_DOMAIN,"status":"created,modified"},"children":[]}}]}}
        return self.POST('/api/node/mo/uni/tn-{}/out-{}.json'.format(Tname,L3OUT_NAME), data,Role)

#T21 Create L3OUT BGP Configure Local AS..
    def L3OUT_BGPLAS(self,Tname,L3OUT_NAME,Node_ID,PORT,BGP_Peer_IP,LOCAL_ASN):
        Role="T21:{}-L3OUT_BGP Configure Local AS:".format(L3OUT_NAME)
        data = {"bgpLocalAsnP":{"attributes":{"dn":"uni/tn-"+Tname+"/out-"+L3OUT_NAME+"/lnodep-"+L3OUT_NAME+"_nodeProfile/lifp-"+L3OUT_NAME+"_interfaceProfile/rspathL3OutAtt-[topology/pod-1/paths-"+Node_ID+"/pathep-[eth"+PORT+"]]/peerP-["+BGP_Peer_IP+"]/localasn","rn":"localasn","localAsn":LOCAL_ASN,"status":"created,modified"},"children":[]}}
        return self.POST('/api/node/mo/uni/tn-{}/out-{}/lnodep-{}_nodeProfile/lifp-{}_interfaceProfile/rspathL3OutAtt-[topology/pod-1/paths-{}/pathep-[eth{}]]/peerP-[{}]/localasn.json'.format(Tname,L3OUT_NAME,L3OUT_NAME,L3OUT_NAME,Node_ID,PORT,BGP_Peer_IP),data,Role)
  #T22 Create L3OUT Secondary IP address..  
    def L3OUT_SEC_IP(self,Tname,L3OUT_NAME,Node_ID,PORT,SVI_SEC_IP):
        Role="T22:{}-L3OUT_Configure the secondary IP:".format(L3OUT_NAME)
        data = {"l3extIp":{"attributes":{"addr":SVI_SEC_IP,"status":"created"},"children":[]}}  
        return self.POST('/api/node/mo/uni/tn-{}/out-{}/lnodep-{}_nodeProfile/lifp-{}_interfaceProfile/rspathL3OutAtt-[topology/pod-1/paths-{}/pathep-[eth{}]].json'.format(Tname,L3OUT_NAME,L3OUT_NAME,L3OUT_NAME,Node_ID,PORT),data,Role)
def main():
    import apic_cfg as cfg
    client = Client(cfg.host, cfg.usr, cfg.pwd)
    print("\n Authenication in to the controller: {}\n".format(cfg.host))
    client.login()
    t1=client.tenant(cfg.tn,cfg.vrf,cfg.bd)
    #t2=client.bd_Subnet(cfg.tn,cfg.bd,cfg.subnet,cfg.scope)
    #t3=client.app_profile(cfg.tn,cfg.app)
    #t4=client.epg(cfg.tn,cfg.bd,cfg.app,cfg.epg)
    #t5=client.Static_vlan(cfg.vname,cfg.vlanid)
    #t6=client.PhysDomain(cfg.phydomain,cfg.vname)
    #t7=client.AttPhyEPG(cfg.tn,cfg.phydomain,cfg.app,cfg.epg)
    #t8=client.EpgStaticPort(cfg.tn,cfg.app,cfg.epg,cfg.LEAF_ID_FROM,cfg.LEAF_ID_TO,cfg.port,cfg.vlanid,cfg.Mode)
    #t9=client.AAEP(cfg.aaep)
    #t10=client.AAEPPhy(cfg.aaep,cfg.phydomain)
    #t11=client.Switch_pro(cfg.Switch_Prof,cfg.LEAF_ID_FROM,cfg.LEAF_ID_TO)
    #t12=client.Interface_pro(cfg.Int_Prof,cfg.port)
    #t13=client.IntP2SWP(cfg.Int_Prof,cfg.Switch_Prof)
    #t14=client.IntP2AAEP(cfg.Int_Prof,cfg.aaep)
    #t15=client.LLDP(cfg.lldp)
    #t16=client.VLAN_SC_L(cfg.vlanscope)
    #t17=client.POLICY_GP(cfg.gp_policy,cfg.vlanscope,cfg.lldp,cfg.aaep)
    #t18=client.GPolicy2IntP(cfg.Int_Prof,cfg.gp_policy,cfg.port)
    #t19=client.bd_L2(cfg.tn,cfg.bd)
    t20=client.L3OUT_BGPRAS(cfg.tn,cfg.vrf,cfg.L3OUT_NAME,cfg.L3OUT_DOMAIN,cfg.EXTERNAL_SUBNETS_NAME,cfg.Node_ID,cfg.PORT,cfg.SVI_VLAN,cfg.SVI_PRI_IP,cfg.MTU,cfg.BGP_Peer_IP,cfg.ROUTER_ID,cfg.REMOTE_ASN)
    t21=client.L3OUT_BGPLAS(cfg.tn,cfg.L3OUT_NAME,cfg.Node_ID,cfg.PORT,cfg.BGP_Peer_IP,cfg.LOCAL_ASN)
    t22=client.L3OUT_SEC_IP(cfg.tn,cfg.L3OUT_NAME,cfg.Node_ID,cfg.PORT,cfg.SVI_SEC_IP)
    
if __name__ == '__main__':
    main()
