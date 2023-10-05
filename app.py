"""Flask routes to run application"""
import sqlite3
from collections import defaultdict
from flask import Flask, render_template, request, redirect, url_for
from models import Nadador, NadadorPrueba
from utils import convert_timestamp, order_swimmers_comp
from database import (
    add_nadador,
    get_categorias,
    get_clubes,
    get_pruebas,
    get_nadadores_info,
    get_nadador_info,
    get_nadador_pruebas,
    update_nadador_info,
    delete_and_insert_nadador_pruebas,
    delete_nadador,
    get_all_pruebas_grouped,
    get_nadadores_prueba,
    update_nadador_pruebas,
    get_ordered_swimmers
)
app = Flask(__name__)

@app.route("/")
def home():
    """Home page route"""
    return render_template("home.html")

@app.route("/enternew")
def enternew():
    """Route to form used to add a new swimmer to the database"""
    categorias = get_categorias()
    clubes = get_clubes()
    pruebas = get_pruebas()

    return render_template("nadador.html", categorias=categorias, clubes=clubes, pruebas=pruebas)

@app.route("/addrec", methods=['POST'])
def addrec():
    """Adds a new swimmer to database"""
    try:
        nomb = request.form['nombap']
        sexo = request.form['Sexo']
        cat = int(request.form['Cat'])
        club = int(request.form['Club'])
        pruebas = request.form.getlist('prueba[]')
        mm_values = request.form.getlist('mm[]')
        ss_values = request.form.getlist('ss[]')
        sss_values = request.form.getlist('sss[]')

        times = convert_timestamp(mm_values, ss_values, sss_values)

        nadador = Nadador(nomb, sexo, cat, club)
        nadador.pruebas = [
            NadadorPrueba(int(prueba), time)
            for prueba, time in zip(pruebas, times)
        ]
        msg = add_nadador(nadador)
        print(msg)
    except sqlite3.Error as err:
        msg = f"Error in the INSERT: {str(err)}"
    return render_template('result.html', msg=msg)

@app.route('/list')
def list_nadadores():
    """Show list of swimmers and personal info"""
    rows = get_nadadores_info()
    return render_template("list.html", rows=rows)

@app.route("/view", methods=['POST'])
def view():
    """Shows the personal information of the swimmer and the events in which he/she will compete"""
    id_nadador = request.form.get('id')
    print(id_nadador)
    nadador = get_nadador_info(id_nadador)
    pruebas = get_nadador_pruebas(id_nadador)
    return render_template("view.html", nadador=nadador, pruebas=pruebas)

@app.route("/edit", methods=['POST'])
def edit():
    """Edit form for swimmer information"""
    try:
        id_nadador = request.form.get('id')
        nadador_info = get_nadador_info(id_nadador)
        pruebas_nadador = get_nadador_pruebas(id_nadador)
        categorias = get_categorias()
        clubes = get_clubes()
        pruebas = get_pruebas()
    except sqlite3.Error as err:
        print("Error:", err)
    return render_template("edit.html", nadador=nadador_info, categorias=categorias,
                           clubes=clubes, pruebas=pruebas,
                           pruebas_nadador=pruebas_nadador)

@app.route("/editrec", methods=['POST'])
def editrec():
    """Updates swimmer information"""
    try:
        id_nadador = request.form.get('id')
        name = request.form['nombap']
        sex = request.form['Sexo']
        cat = int(request.form['Cat'])
        club = int(request.form['Club'])
        pruebas = request.form.getlist('prueba[]')
        mm_values = request.form.getlist('mm[]')
        ss_values = request.form.getlist('ss[]')
        sss_values = request.form.getlist('sss[]')

        times = convert_timestamp(mm_values, ss_values, sss_values)

        update_nadador_info(id_nadador, name, sex, cat, club)
        delete_and_insert_nadador_pruebas(id_nadador, list(zip(pruebas, times)))

    except sqlite3.Error as err:
        print("Error:", err)
    return redirect(url_for('list_nadadores'))

@app.route("/delete", methods=['POST'])
def delete():
    """Delete a Nadador from the database"""
    try:
        id_nadador = request.form.get('rowId')
        delete_nadador(id_nadador)
    except sqlite3.Error as err:
        print("Error:", err)
    return redirect(url_for('list_nadadores'))

@app.route('/ordercomp')
def orden_competitivo():
    """Shows list of events to sort or view (competitive)"""
    pruebas = get_all_pruebas_grouped()

    return render_template("competitivo.html", pruebas=pruebas)


@app.route('/ordercomp/<int:id_prueba>/<int:id_categoria>/<string:sexo>', methods=['POST'])
def ordercomp(id_prueba, id_categoria, sexo):
    """Asign a pool number and a lane number for each swimmer in an event"""
    nadadores_prueba = list(get_nadadores_prueba(id_prueba, id_categoria, sexo))
    nadadores_ordenados = order_swimmers_comp(nadadores_prueba)

    update_nadador_pruebas(nadadores_ordenados)

    return viewordercomp(id_prueba, id_categoria, sexo)

@app.route('/viewordercomp/<int:id_prueba>/<int:id_categoria>/<string:sexo>', methods=['POST'])
def viewordercomp(id_prueba, id_categoria, sexo):
    """Show list of pools and lanes for an event"""

    nadadores_prueba = list(get_ordered_swimmers(id_prueba, id_categoria, sexo))

    # Create a defaultdict with the default value as a list
    grouped_sublists = defaultdict(list)

    for sublist in nadadores_prueba:
        key = sublist[-2]
        grouped_sublists[key].append(sublist)

    result = list(grouped_sublists.values())

    piletas = []
    for pileta in result:
        pileta.sort(key=get_orden)
        piletas.append(pileta)

    piletas.reverse()
    return render_template("piletas_pruebas.html", piletas=piletas)

def get_orden(row):
    """Returns orden of swimmer"""
    return row['Orden']

if __name__ == "__main__":
    app.run(debug=True)
