from flask import Flask, render_template, request, redirect, session, flash, url_for
import os
import pyrebase
from services import Database, Authorization
from models import Transaction
from datetime import datetime
from functools import wraps

app = Flask(__name__)

app.secret_key = os.environ['secret_key']

CONFIG_NAMES = ['apiKey', 'authDomain', 'databaseURL',
                'storageBucket', 'storageBucket',
                'messagingSenderId']

firebase = pyrebase.initialize_app({key:os.environ[key] for key in CONFIG_NAMES})

db = Database(firebase)
auth = Authorization(firebase)

@app.context_processor
def is_logged_in():
    return dict(is_logged_in='username' in session)

def login_required(f):
    @wraps(f)
    def func(*args, **kwargs):
        if not auth.is_logged_in():
            try:
                session.pop('username')
            except KeyError:
                pass
            finally:
                auth.user = None
            return redirect(url_for('index', next=request.url))
        return f(*args, **kwargs)
    return func

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        auth.log_in(username, password)
        if auth.is_logged_in():
            session['username'] = username
    return render_template('index.html')

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    if request.method == 'POST':
        session.pop('username')
        auth.user = None
    return render_template('index.html')

@app.route('/types')
@login_required
def transaction_types():
    tacts = db.get('transaction_types')
    return render_template('types.html', types=tacts)

class Field(object):
    def __init__(self, fname, name, type_, editable):
        self.fname = fname 
        self.name = name 
        self.type = type_
        self.editable = editable

    def to_dict(self):
        return dict(fname=self.fname, 
                    name=self.name, 
                    type=self.type, 
                    editable=self.editable)

@app.route('/new_transaction', methods=['GET', 'POST'])
@login_required
def new_transaction():
    transaction_name = 'Transaction Name'
    fields = [Field('field_0', 'name', 'string', False), 
              Field('field_1', 'date', 'date', False), 
              Field('field_2', 'cost', 'number', False)]

    if request.method == 'POST':
        n_fields = int(len(request.form)/2)
        transaction_name = request.form.get('transaction_name')
        for k,v in request.form.items():
            try:
                if int(k.split('_')[-1]) > 2 and k.split('_')[0] != 'type':
                    if v == '':
                        v = 'enter name'
                    new_field = Field(k, v, request.form['type_{}'.format(k)], True)
                    fields.append(new_field)
            except ValueError:
                pass
        fields.append(Field('field_{}'.format(n_fields), 'enter name', 'string', True))
    if transaction_name == 'Transaction Name':
        flash('Need to edit transaction name')
    
    return render_template('new_transaction.html',
                           transaction_name=transaction_name,
                           fields=[i.to_dict() for i in fields])

@app.route('/add_transaction', methods=['POST'])
@login_required
def add_transaction():
    transaction_name = request.form.get('transaction_name')
    if transaction_name == 'Transaction Name':
        return redirect('/new_transaction') 
    fields = [Field('field_0', 'name', 'string', False), 
              Field('field_1', 'date', 'date', False), 
              Field('field_2', 'cost', 'number', False)]

    for k,v in request.form.items():
        try:
            if int(k.split('_')[-1]) > 2 and k.split('_')[0] != 'type':
                if v == '':
                    v = 'enter name'
                new_field = Field(k, v, request.form['type_{}'.format(k)], True)
                fields.append(new_field)
        except ValueError:
            pass
    payload = Transaction(transaction_name)
    for field in fields:
        payload.add_property(field.name, field.type)
    db.put('transaction_types', payload.to_json(), auth.get_auth())
    return redirect('/types')
     
if __name__ == '__main__':
    app.run(port=33507)
