from pyroute2.ndb.rtnl_object import RTNL_Object
from pyroute2.common import basestring
from pyroute2.netlink.rtnl.ifinfmsg import ifinfmsg


class Interface(RTNL_Object):

    table = 'interfaces'
    summary = '''
              SELECT
                  f_target, f_index, f_IFLA_IFNAME,
                  f_IFLA_ADDRESS, f_flags
              FROM
                  interfaces
              '''
    summary_header = ('target', 'index', 'ifname', 'lladdr', 'flags')

    def __init__(self, schema, key):
        self.event_map = {ifinfmsg: "load_rtnlmsg"}
        super(Interface, self).__init__(schema, key, ifinfmsg)

    def complete_key(self, key):
        if isinstance(key, dict):
            ret_key = key
        else:
            ret_key = {'target': 'localhost'}

        if isinstance(key, basestring):
            ret_key['IFLA_IFNAME'] = key
        elif isinstance(key, int):
            ret_key['index'] = key

        fetch = []
        for name in self.kspec:
            if name not in ret_key:
                fetch.append('f_%s' % name)

        if fetch:
            keys = []
            values = []
            for name, value in ret_key.items():
                keys.append('f_%s = %s' % (name, self.schema.plch))
                values.append(value)
            spec = (self
                    .schema
                    .execute('SELECT %s FROM interfaces WHERE %s' %
                             (' , '.join(fetch), ' AND '.join(keys)),
                             values)
                    .fetchone())
            for name, value in zip(fetch, spec):
                ret_key[name[2:]] = value

        return ret_key
