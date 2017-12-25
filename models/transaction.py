class Transaction(object):
    def __init__(self, name, **kwargs):
        self._name = name 
        self._props = {}

    def add_property(self,key, prop):
        self._props[key] = prop

    def to_json(self):
        payload = dict(name_=self._name)
        for k,v in self._props.items():
            payload[k] = v
        return payload