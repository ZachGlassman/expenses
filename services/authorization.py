from flask import flash
from requests.exceptions import HTTPError

class Authorization(object):
    """accessfirebase"""
    def __init__(self, firebase):
        self.firebase = firebase.auth()
        self.user = None

    def log_in(self, uname, pwd):
        try:
            self.user = self.firebase.sign_in_with_email_and_password(uname, pwd)
        except HTTPError:
            flash('invalid username or password')

    def is_logged_in(self):
        return self.user is not None

    def get_auth(self):
        return self.user['idToken']