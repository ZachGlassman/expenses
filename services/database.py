VALID_PATHS = ['transaction_types', 'transactions']

class Database(object):
    """accessfirebase"""
    def __init__(self, firebase):
        self.db = firebase.database()
        self._user = None

    @property
    def user(self):
        return self._user

    @user.setter
    def user(self, value):
        self._user = value 

    def _validate(self):
        return self._user is not None

    def put(self, path, data, auth):
        """put data in user folder in database"""
        assert path in VALID_PATHS
        return self.db.child(path).push(data, auth)

    def get(self, path, type_=None):
        if type_ is None:
            items = self.db.child(path).get()
        else:
            items = self.db.child(path).order_by_child(type_).get()
        try:
            return [item.val() for item in items.each()]
        except TypeError:
            return []
    