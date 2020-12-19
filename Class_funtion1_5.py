import requests
import json
from string import Template
requests.urllib3.disable_warnings()

class AuthenticationError(Exception):
    pass
class Client:
    def __init__(self, host, usr, pwd):
        #self.jar = requests.cookies.RequestsCookieJar()
        self.host = host
        self.usr = usr
        self.pwd = pwd
        self.client = requests.Session() 
    
    def POST(self, url, data,Role):
        response= self.client.post('https://%s%s' % (self.host, url),data=json.dumps(data),timeout=5,verify=False)
        resp=response.text
        if 'error' in resp:
          print(">>>{}: Already created or config issue..HTTP Code{}\n".format(Role,response))
          print(">>> Please fix the issue on Error code:{}\n".format(resp))
        else:
          print("\n***{}: Created Successfully # HTTP_code>>>>{}\n".format(Role,response))
        return response
        
    def get(self, url):
        print("getting into the controller:{}".format(url))
        r=self.client.get('https://%s%s' % (self.host, url),timeout=5,verify=False)
        print("get response {}".format(r))
        return r
    def login(self):
        data = {"aaaUser": {"attributes": {"name": self.usr, "pwd": self.pwd}}}
        res= self.client.post('https://%s/api/aaaLogin.json' % (self.host),data=json.dumps(data),timeout=5,verify=False)
        print(res)
        if res.status_code != 200 or 'error' in res.json()['imdata'][0]:
            raise AuthenticationError

    def tenant(self,Tname,VRF,BD):
        Role='tenant:{},VRF:{},L3_BD:{}'.format(Tname,VRF,BD)
        print("\nCreating the tenant:{}\n".format(Tname))
        data = { "fvTenant":{"attributes":{"dn":"uni/tn-"+Tname,"status":"created,modified"},"children":[
               {"fvBD":{"attributes":{"dn":"uni/tn-"+Tname+"/BD-"+BD+"_bd","name":BD+"_bd","arpFlood":"true","unicastRoute":"true","rn":"BD-"+BD+"_bd","status":"created,modified"},
               "children":[{"fvRsCtx":{"attributes":{"tnFvCtxName":VRF+"_vrf","status":"created,modified"},"children":[]   }}]}},
               {"fvCtx":{"attributes":{"dn":"uni/tn-"+Tname+"/ctx-"+VRF+"_vrf","name": VRF+"_vrf","rn":"ctx-"+VRF+"_vrf","status":"created,modified"},"children":[]
              }}]}}
        return self.POST('/api/mo/uni/tn-{}.json'.format(Tname), data,Role)
    
    def bd_Subnet(self,Tname,BD,Subnet,Scope):
        Role='tenant:{},BD:{}'.format(Tname,BD,Subnet)
        print("\nCreating the L3 BD:{}\n".format(Scope))
        scope_list = ['public', 'shared','private']
        if Scope in scope_list:
           data = {"fvSubnet": {"attributes": {"dn": "uni/tn-"+Tname+"/BD-"+BD+"_bd/subnet-["+Subnet+"]", "ctrl": "", "ip": Subnet, "rn": "subnet-["+Subnet+"]","scope":Scope, "status": "created,modified"},"children": [] } }
        else:
           data = {"fvSubnet": {"attributes": {"dn": "uni/tn-"+Tname+"/BD-"+BD+"_bd/subnet-["+Subnet+"]", "ctrl": "", "ip": Subnet, "rn": "subnet-["+Subnet+"]", "status": "created"},"children": [] } }
        return self.POST('/api/node/mo/uni/tn-{}/BD-{}_bd/subnet-[{}].json'.format(Tname,BD,Subnet), data,Role)
        #'https://{}/api/node/mo/uni/tn-{}/BD-{}_bd/subnet-[{}].json'
    
    def bd_L2(self,Tname,BD):
        Role="{}-L2 BD domain(Flood/Unicast disabled):".format(BD)
        data = {"fvBD":{"attributes":{"dn":"uni/tn-"+Tname+"/BD-"+BD+"_bd","arpFlood":"true","unicastRoute":"false","unkMacUcastAct":"flood","status":"created,modified"},"children":[]}}
        return self.POST('/api/mo/uni/tn-{}/BD-{}_bd.json'.format(Tname,BD), data,Role)

    def app_profile(self,Tname,APP):
        Role="{}-Application profile:".format(APP)
        data = {"fvAp":{"attributes":{"dn":"uni/tn-"+Tname+"/ap-"+APP+"_ap","name":APP+"_ap","rn":"ap-"+APP+"_ap","status":"created"},"children":[] }}
        return self.POST('/api/mo/uni/tn-{}/ap-{}_ap.json'.format(Tname,APP), data,Role)

    def epg(self,Tname,BD,APP,EPG):
        Role="EPG:{}".format(EPG)
        data = {"fvAEPg":{"attributes":{"dn":"uni/tn-"+Tname+"/ap-"+APP+"_ap/epg-"+EPG+"_epg","name":EPG+"_epg","rn":"epg-"+EPG+"_epg","status":"created"},
        "children":[{"fvRsBd":{"attributes":{"tnFvBDName":BD+"_bd","status":"created,modified"},"children":[] }}]}}
        return self.POST('/api/mo/uni/tn-{}/ap-{}_ap.json'.format(Tname,APP), data,Role)
 
def main():
    import apic_cfg as cfg
    client = Client(cfg.host, cfg.usr, cfg.pwd)
    print("\nAuthenication in to the controller: {}\n".format(cfg.host))
    client.login()
    t1=client.tenant(cfg.tn,cfg.vrf,cfg.bd)
    t2=client.bd_Subnet(cfg.tn,cfg.bd,cfg.subnet,cfg.scope)
    t3=client.app_profile(cfg.tn,cfg.app)
    t4=client.epg(cfg.tn,cfg.bd,cfg.app,cfg.epg)
    #t2=client.bd_L2(cfg.tn,cfg.bd)

if __name__ == '__main__':
    main()
