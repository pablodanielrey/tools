# -*- coding: utf-8 -*-
from flask import Flask, render_template, flash, request
import os
import json
from wtforms import Form, TextField, IntegerField, TextAreaField, validators, StringField, SubmitField
import psycopg2
import psycopg2.extras

dbname=os.environ["DBNAME"]
user=os.environ["USER"]
host=os.environ["HOST"]
password=os.environ["PASSWORD"]

######################## Clase de Formulario ###################################
class DniForm(Form):
    dni = TextField('DNI:', validators=[validators.required()])

class CompensatorioForm(Form):
    compensatorios = IntegerField('Compensatorios:', validators=[validators.required()])
    id = TextField('ID:', validators=[validators.required()])
    dni = TextField('DNI:', validators=[validators.required()])

################################################################################
######################## Busqueda ##############################################
def busqueda_dni(dni):
    try:
        connect_str = "dbname=%s user=%s host=%s password=%s" %(dbname, user, host, password)
        conn = psycopg2.connect(connect_str)
        try:
            cursor = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
            try:
                cursor.execute("SELECT dni, u.id, lastname, name, c.stock from profile.users u left outer join assistance.justification_compensatory_stock c on (u.id = c.user_id) where dni = %s", (dni,))
                persona = cursor.fetchone()
            finally:
                cursor.close()
        finally:
            conn.close()
    except Exception as e:
        print("Falla de conexion., Nombre de Base de datos, usuario o contrasenia?")
        print(e)
        persona="error"
    return persona
################################################################################
######################## ACtualizador ##########################################
def actualizarCompensatorios(id, compensatorios):
    try:
        connect_str = "dbname=%s user=%s host=%s password=%s" %(dbname, user, host, password)
        conn = psycopg2.connect(connect_str)
        try:
            cursor = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
            #cursor.execute("SELECT dni, u.id, lastname, name, c.stock from profile.users u left outer join assistance.justification_compensatory_stock c on (u.id = c.user_id) where user_id = %s", (id,))
            try:
                cursor.execute("SELECT stock from assistance.justification_compensatory_stock where user_id = %s", (id,))
                if cursor.fetchone() == None:
                    print("Creando entrada para usuario.")
                    cursor.execute("INSERT INTO assistance.justification_compensatory_stock (user_id, stock) VALUES (%s,%s)", (id, compensatorios))
                else:
                    print("Actualizando Usuario")
                    cursor.execute("UPDATE assistance.justification_compensatory_stock SET stock = stock + %s WHERE user_id = %s", (compensatorios, id))
                conn.commit()
                print("Se actualizaron los compensatorios del usuario.")
            finally:
                cursor.close()
        finally:
            conn.close()
    except Exception as e:
        print("Falla de conexion.")
        print(e)
        persona="error"
    return None
################################################################################

######################## Crea instancia de aplicacion ##########################
app = Flask(__name__)
app.config.from_object(__name__)
################################################################################
######################## Ruta por defecto / ####################################
@app.route("/")
def index():
    return render_template ('index.html', title="Inicio")
################################################################################
######################## PRUEBA ################################################
@app.route('/prueba/', methods=['GET', 'POST'])
def prueba():
    return render_template ('prueba.html', title="Pruebaaaa")
################################################################################
######################## Compensatorios ########################################
@app.route('/compensatorios/', methods=['GET', 'POST'])
def compensatorios():
    formDNI=DniForm(request.form)
    formCompensatorio=CompensatorioForm(request.form)
    persona=""
    if request.method == "POST":
        formulario=request.form["nombre-formulario"]
        if formulario == "buscador":
            print("Ingreso a formulario buscador ----------------")
            if formDNI.validate():
                print("Se busca a la persona con DNI: ", request.form["dni"])
                persona=busqueda_dni(request.form["dni"])
        if formulario == "actualizador":
            print("Ingreso a formulario actualizador ----------------")
            if formCompensatorio.validate():
                print("Se requieren agregar: ",request.form["compensatorios"]," compensatorios.")
                print("Para el usuario con id: ",request.form["id"])
                actualizarCompensatorios(request.form["id"], request.form["compensatorios"])
            persona=busqueda_dni(request.form["dni"])
    return render_template ('compensatorios.html',title="Compensatorios",persona=persona,formDNI=formDNI, formCompensatorio=formCompensatorio)
################################################################################
######################## Ausentes con Aviso ####################################
@app.route('/aca/', methods=['GET', 'POST'])
def aca():
    return render_template ('aca.html', title="Ausentes con Aviso")
################################################################################

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80,debug=True)
