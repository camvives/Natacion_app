"""Flask routes to run application"""
import sqlite3
from flask import Flask, render_template, request, redirect, url_for
from models import Nadador, NadadorPrueba, Prueba, Categoria
from utils import (
    convert_timestamp,
    order_swimmers_comp,
    order_pools,
    convert_one_timestamp
)
from database import (
    get_pruebas_info,
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
    get_ordered_swimmers,
    get_one_prueba,
    get_one_categoria,
    get_nadadores_prueba_rec,
    update_nadador_pruebas_rec,
    get_ordered_swimmers_rec,
    insert_comp_time,
    del_comp_time,
    get_ranked_swimmers,
    update_prueba,
    del_prueba,
    insert_prueba
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

@app.route('/orderrec')
def orden_recreativo():
    """Shows list of events to sort or view (recreative)"""
    pruebas = get_all_pruebas_grouped()

    return render_template("recreativo.html", pruebas=pruebas)


@app.route('/ordercomp/<int:id_prueba>/<int:id_categoria>/<string:sexo>', methods=['POST'])
def ordercomp(id_prueba, id_categoria, sexo):
    """Asign a pool number and a lane number for each swimmer in an event"""
    nadadores_prueba = list(get_nadadores_prueba(id_prueba, id_categoria, sexo))
    nadadores_ordenados = order_swimmers_comp(nadadores_prueba)

    update_nadador_pruebas(nadadores_ordenados)

    return viewordercomp(id_prueba, id_categoria, sexo)

@app.route('/orderrec/<int:id_prueba>/<int:id_categoria>/<string:sexo>', methods=['POST'])
def orderrec(id_prueba, id_categoria, sexo):
    """Asign randomly a pool number and a lane number for each swimmer in an event"""
    nadadores_prueba = list(get_nadadores_prueba_rec(id_prueba, id_categoria, sexo))
    nadadores_ordenados = order_swimmers_comp(nadadores_prueba)

    update_nadador_pruebas_rec(nadadores_ordenados)

    return vieworderrec(id_prueba, id_categoria, sexo)

@app.route('/viewordercomp/<int:id_prueba>/<int:id_categoria>/<string:sexo>', methods=['POST'])
def viewordercomp(id_prueba, id_categoria, sexo):
    """Show list of pools and lanes for an event"""

    nadadores_prueba = list(get_ordered_swimmers(id_prueba, id_categoria, sexo))
    piletas = order_pools(nadadores_prueba)
    prueba = get_one_prueba(id_prueba)
    categoria = get_one_categoria(id_categoria)

    return render_template("piletas_pruebas.html", piletas=piletas,
                           prueba=prueba, categoria=categoria, sexo=sexo,
                           tipo='Competitivo')

@app.route('/vieworderrec/<int:id_prueba>/<int:id_categoria>/<string:sexo>', methods=['POST'])
def vieworderrec(id_prueba, id_categoria, sexo):
    """Show list of pools and lanes for an event"""

    nadadores_prueba = list(get_ordered_swimmers_rec(id_prueba, id_categoria, sexo))
    piletas = order_pools(nadadores_prueba)
    prueba = get_one_prueba(id_prueba)
    categoria = get_one_categoria(id_categoria)

    return render_template("piletas_pruebas.html", piletas=piletas,
                           prueba=prueba, categoria=categoria, sexo=sexo,
                           tipo='Recreativo')


@app.route('/cargatime/<int:id_prueba>/<int:id_categoria>/<string:sexo>', methods=['POST'])
def cargatime(id_prueba, id_categoria, sexo):
    """Show list of pools and lanes for an event and let the user upload times"""

    nadadores_prueba = list(get_ordered_swimmers(id_prueba, id_categoria, sexo))
    piletas = order_pools(nadadores_prueba)
    prueba = get_one_prueba(id_prueba)
    categoria = get_one_categoria(id_categoria)

    return render_template("piletas_pruebas.html", piletas=piletas,
                           prueba=prueba, categoria=categoria, sexo=sexo,
                           tipo='Carga Tiempos')

@app.route('/insertNadTime', methods=['POST'])
def insert_nad_time():
    """Insert the competitive time for a swimmer in an event"""
    id_prueba = request.form.get('prueba')
    id_categoria = request.form.get('categoria')
    sexo = request.form.get('sexo')
    id_nadador = request.form.get('nadador')
    tiempo_mm = request.form.get('tiempo_mm')
    tiempo_ss = request.form.get('tiempo_ss')
    tiempo_sss = request.form.get('tiempo_sss')
    tiempo = convert_one_timestamp(tiempo_mm, tiempo_ss, tiempo_sss)

    insert_comp_time(id_prueba, id_nadador, tiempo)
    return cargatime(id_prueba, id_categoria, sexo)

@app.route('/delNadTime', methods=['POST'])
def del_nad_time():
    """Insert the competitive time for a swimmer in an event"""
    id_prueba = request.form.get('prueba')
    id_categoria = request.form.get('categoria')
    sexo = request.form.get('sexo')
    id_nadador = request.form.get('nadador')

    print(id_prueba, id_nadador)
    del_comp_time(id_prueba, id_nadador)
    return cargatime(id_prueba, id_categoria, sexo)

@app.route('/results', methods=['GET'])
def results():
    """Show list of events to access results of competition"""
    pruebas = get_all_pruebas_grouped()

    return render_template("resultados.html", pruebas=pruebas)

@app.route('/results/<int:id_prueba>/<int:id_categoria>/<string:sexo>', methods=['POST'])
def result_event(id_prueba, id_categoria, sexo):
    """Show swimmers rank based on event time"""

    nadadores_ranked = get_ranked_swimmers(id_prueba, id_categoria, sexo)
    prueba = get_one_prueba(id_prueba)
    categoria = get_one_categoria(id_categoria)

    return render_template("ranking.html", nadadores=nadadores_ranked,
                           prueba=prueba, categoria=categoria, sexo=sexo)


@app.route('/pruebas')
def list_pruebas():
    """Show list of events"""
    rows = get_pruebas_info()
    return render_template("pruebas.html", rows=rows)

@app.route('/editprueba', methods=['POST'])
def edit_prueba():
    """Update event info"""
    prueba = Prueba(request.form['edited_description'])
    prueba.id_prueba = request.form['id_edit']

    update_prueba(prueba)
    rows = get_pruebas_info()
    return render_template("pruebas.html", rows=rows)

@app.route('/deleteprueba', methods=['POST'])
def delete_prueba():
    """Update event info"""
    id_prueba = request.form.get('rowId')
    del_prueba(id_prueba)

    rows = get_pruebas_info()
    return render_template("pruebas.html", rows=rows)

@app.route('/addprueba', methods=['POST'])
def add_prueba():
    """Add an event"""
    prueba = Prueba(request.form['new_description'])
    insert_prueba(prueba)
    
    rows = get_pruebas_info()
    return render_template("pruebas.html", rows=rows)


if __name__ == "__main__":
    app.run(debug=True)
