from flask import Flask, render_template, request, redirect, session, flash, url_for, jsonify
import os
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore, \
    UserMixin, RoleMixin, login_required
from services.plotting import generate_type_plot
from services.database import MongoDatabase
from models import Transaction
from datetime import datetime

app = Flask(__name__)


app.config['SECRET_KEY'] = os.environ['secret_key']
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.config['SECURITY_PASSWORD_SALT'] = os.environ['SALT']


db = MongoDatabase(os.environ["MONGODB_URI"])

db_ = SQLAlchemy(app)

roles_users = db_.Table('roles_users',
        db_.Column('user_id', db_.Integer(), db_.ForeignKey('user.id')),
        db_.Column('role_id', db_.Integer(), db_.ForeignKey('role.id')))

class Role(db_.Model, RoleMixin):
    id = db_.Column(db_.Integer(), primary_key=True)
    name = db_.Column(db_.String(80), unique=True)
    description = db_.Column(db_.String(255))

class User(db_.Model, UserMixin):
    id = db_.Column(db_.Integer, primary_key=True)
    email = db_.Column(db_.String(255), unique=True)
    password = db_.Column(db_.String(255))
    active = db_.Column(db_.Boolean())
    confirmed_at = db_.Column(db_.DateTime())
    roles = db_.relationship('Role', secondary=roles_users,
                            backref=db_.backref('users', lazy='dynamic'))

# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db_, User, Role)
security = Security(app, user_datastore)


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_.session.remove()

@app.route('/')
@login_required
def index():
    div = ''
    script = ''
    tacts = db.get_collection('transactions')
    div, script = generate_type_plot([(i['type_'], i['cost']) for i in tacts])
    return render_template('index.html', div=div, script=script)


@app.route('/types')
@login_required
def transaction_types():
    tacts = db.get_collection('transaction_types')
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
    db.put('transaction_types', payload.to_json())
    return redirect('/types')

def _validate(d):
    """validate that every value is non default"""
    return True

@app.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    """add some sort of specific transactions"""
    tacts = db.get_collection('transaction_types')
    select = tacts[0]
    if request.method == 'POST':
        select = [t for t in tacts if t['name_'] == request.form['select']][0]
    return render_template('add.html', 
                           tacts=[t['name_'] for t in tacts], 
                           selected=[k:v for k,v in select.items() if k != '_id')

@app.route('/add_final', methods=['POST'])
@login_required
def add_final():
    if _validate(request.form):
        payload = {k:v for k,v in request.form.items() if k != 'select'}
        flash(payload)
        payload['type_'] = request.form['select']
        db.put('transactions', payload)
        return redirect('/transactions')
    else:
        return jsonify({})

@app.route('/transactions')
@login_required
def transactions():
    tacts = db.get_collection('transactions')
    return render_template('transactions.html', tacts=tacts)

     
if __name__ == '__main__':
    app.run(port=33507)
