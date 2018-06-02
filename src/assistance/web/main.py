# -*- coding: utf-8 -*-
from flask import Flask, render_template, flash, request, url_for, session, jsonify, redirect
import os
import json
from wtforms import Form, TextField, IntegerField, TextAreaField, validators, StringField, SubmitField

from assistance.model.model import Model

dbname=os.environ["DBNAME"]
user=os.environ["USER"]
host=os.environ["HOST"]
password=os.environ["PASSWORD"]
client_id = os.environ['OIDC_CLIENT_ID']
client_secret = os.environ['OIDC_CLIENT_SECRET']
token_url = os.environ['OIDC_HOST'] + '/oauth2/token'
authorize_url = os.environ['OIDC_HOST'] + '/oauth2/auth'

model = Model(dbname, user, host, password)

### oauth ###

from werkzeug import security
from flask_oauthlib.client import OAuth
oauth = OAuth()
oidc = oauth.remote_app(
    'oidc',
    consumer_key=client_id,
    consumer_secret=client_secret,
    request_token_params={'state': lambda: security.gen_salt(10)},
    base_url='http://localhost:5001/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url=token_url,
    authorize_url=authorize_url
)

@oidc.tokengetter
def get_github_oauth_token():
    return session.get('oidc_token')


class DniForm(Form):
    dni = TextField('DNI:', validators=[validators.required()])

class CompensatorioForm(Form):
    compensatorios = IntegerField('Compensatorios:', validators=[validators.required()])
    id = TextField('ID:', validators=[validators.required()])
    dni = TextField('DNI:', validators=[validators.required()])


app = Flask(__name__)
app.secret_key = 'development'
#app.config.from_object(__name__)

@app.route('/authorized')
def authorized():
    resp = oidc.authorized_response()
    if resp is None or resp.get('access_token') is None:
        return 'Access denied: reason=%s error=%s resp=%s' % (
            request.args['error'],
            request.args['error_description'],
            resp
        )
    session['oidc_token'] = (resp['access_token'], '')
    me = oidc.get('user')
    return jsonify({'status':'OK'})

@app.route('/login')
def login():
    return oidc.authorize(callback=url_for('authorized', _external=True))

@app.route('/logout')
def logout():
    session.pop('oidc_token', None)
    return redirect(url_for('index'))



@app.route("/")
def index():
    if 'oidc_token' not in session:
        return redirect(url_for('login'))
    return render_template ('index.html', title="Inicio")


@app.route('/prueba/', methods=['GET', 'POST'])
def prueba():
    if 'oidc_token' not in session:
        return redirect(url_for('login'))

    return render_template ('prueba.html', title="Pruebaaaa")

@app.route('/compensatorios/', methods=['GET', 'POST'])
def compensatorios():
    if 'oidc_token' not in session:
        return redirect(url_for('login'))

    formDNI=DniForm(request.form)
    formCompensatorio=CompensatorioForm(request.form)
    persona=""
    if request.method == "POST":
        formulario=request.form["nombre-formulario"]
        if formulario == "buscador":
            print("Ingreso a formulario buscador ----------------")
            if formDNI.validate():
                print("Se busca a la persona con DNI: ", request.form["dni"])
                persona = model.busqueda_dni(request.form["dni"])
        if formulario == "actualizador":
            print("Ingreso a formulario actualizador ----------------")
            if formCompensatorio.validate():
                print("Se requieren agregar: ",request.form["compensatorios"]," compensatorios.")
                print("Para el usuario con id: ",request.form["id"])
                model.actualizarCompensatorios(request.form["id"], request.form["compensatorios"])
            persona = model.busqueda_dni(request.form["dni"])
    return render_template ('compensatorios.html',title="Compensatorios",persona=persona,formDNI=formDNI, formCompensatorio=formCompensatorio)

@app.route('/aca/', methods=['GET', 'POST'])
def aca():
    if 'oidc_token' not in session:
        return redirect(url_for('login'))

    return render_template ('aca.html', title="Ausentes con Aviso")

