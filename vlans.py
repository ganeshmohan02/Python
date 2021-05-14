import tarfile
from collections import defaultdict
from pyaci.core import aciClassMetas
# from pprint import pprint
import json


class Fabric:

    def __init__(self, dc_name, config_file):
        self.dc_name = dc_name
        self.config_file = config_file

    @staticmethod
    def _get_dn(_class, attributes, parent_dn):
        if attributes.get('dn', '') != '':
            return attributes['dn']
        if parent_dn == '':
            return
        rn_template = aciClassMetas.get(_class, {}).get('rnFormat')
        if rn_template is None:
            return
        rn = rn_template.format(**attributes)
        return f'{parent_dn}/{rn}'

    def _read_mos(self, subtree, mos, parent_dn=''):
        for _class, body in subtree.items():
            record = body['attributes']
            dn = self._get_dn(_class, record, parent_dn)
            if dn is None:
                continue

            # Update indexes
            record['dn'] = dn
            mos.by_dn[dn] = record
            mos.by_class[_class].append(dn)

            # Iterate child subtrees
            for child in body.get('children', []):
                self._read_mos(child, mos, parent_dn=dn)

    def extract_config(self):
        with tarfile.open(name=self.config_file, mode='r:gz') as tar:
            mos = MOs(self.dc_name)
            for fi in tar:
                if fi.isfile() and fi.name.endswith('.json'):
                    f = tar.extractfile(fi)
                    data = json.loads(f.read())
                    self._read_mos(data, mos)
        return mos


class MOs:

    def __init__(self, dc_name):
        self.dc_name = dc_name
        self.by_dn = {}
        self.by_class = defaultdict(list)

    def get_by_class(self, _class):
        return self.by_class.get(_class)

    def get_by_dn(self, dn):
        return self.by_dn.get(dn)

    def get_pool_dn(self, dom_dn):
        pool_rs_dn = f'{dom_dn}/rsvlanNs'
        pool_rs = self.get_by_dn(pool_rs_dn)
        if pool_rs is None:
            return
        return pool_rs['tDn']

    def get_vlans(self, pool_dn):
        vlans = set()
        if pool_dn is None:
            return vlans
        for block_dn in self.get_by_class('fvnsEncapBlk'):
            if not block_dn.startswith(pool_dn):
                continue
            block = self.get_by_dn(block_dn)
            _from = int(block['from'].split('-')[1])
            _to = int(block['to'].split('-')[1])
            vlans.update(set(range(_from, _to + 1)))
        return vlans

    def check_vlan_mappings(self):
        doms_by_epg = defaultdict(lambda: {'doms': [], 'overlapping': set()})

        for dom_att_dn in self.get_by_class('fvRsDomAtt'):
            epg_dn = '/'.join(dom_att_dn.split('/')[:4])
            dom_dn = self.get_by_dn(dom_att_dn).get('tDn')
            # Ignore everything except physical and VMM
            if not dom_dn[4:8] in ['phys', 'vmmp']:
                continue
            doms_by_epg[epg_dn]['doms'].append(dom_dn)

        for epg_dn, metadata in doms_by_epg.items():
            if len(metadata['doms']) <= 1:
                continue
            for dom_dn1 in metadata['doms']:
                for dom_dn2 in metadata['doms']:
                    if dom_dn1 == dom_dn2:
                        continue
                    pool_dn1 = self.get_pool_dn(dom_dn1)
                    pool_dn2 = self.get_pool_dn(dom_dn2)
                    if pool_dn1 == pool_dn2 or pool_dn1 is None:
                        continue
                    vlans1 = self.get_vlans(pool_dn1)
                    vlans2 = self.get_vlans(pool_dn2)
                    metadata['overlapping'].update(vlans1.intersection(vlans2))
            if len(metadata['overlapping']) > 0:
                count = len(metadata['overlapping'])
                print(f'{epg_dn}, {count}')


fabrics = [
    Fabric('gtn', 'gtn/GTN-ce2_defaultOneTime-2020-11-17T17-00-27.tar.gz'),
    Fabric('b12', 'b12/B12-ce2_defaultOneTime-2020-11-17T20-00-55.tar.gz'),
    Fabric('det', 'det/DET-ce2_defaultOneTime-2020-11-17T17-08-11.tar.gz'),
    Fabric('nlv', 'nlv/NLV-ce2_defaultOneTime-2020-11-17T12-07-26.tar.gz'),
]


def main():
    for fabric in fabrics:
        mos = fabric.extract_config()
        print(fabric.dc_name)
        mos.check_vlan_mappings()


if __name__ == '__main__':
    main()
