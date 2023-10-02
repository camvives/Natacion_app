"""Flask routes"""
import sqlite3
import datetime
from flask import Flask
from flask import render_template
from flask import request

app = Flask(__name__)

@app.route("/")
def home():
    """Home page route"""
    return render_template("home.html")

@app.route("/enternew")
def enternew():
    """Route to form used to add a new swimmer to the database"""

    con = sqlite3.connect("database.db")
    con.row_factory = sqlite3.Row

    cur = con.cursor()

    cur.execute("SELECT * FROM Categorias")
    categorias = cur.fetchall()
    cur.execute("SELECT * FROM Clubes")
    clubes = cur.fetchall()
    cur.execute("SELECT * FROM Pruebas")
    pruebas = cur.fetchall()

    con.close()

    return render_template("nadador.html", categorias=categorias, clubes=clubes, pruebas=pruebas)


@app.route("/addrec", methods = ['POST', 'GET'])
def addrec():
    """Route to add a new record (INSERT) swimmer data to the database"""
    # Data will be available from POST submitted by the form
    if request.method == 'POST':
        try:
            name = request.form['nombap']
            sex = request.form['Sexo']
            cat = int(request.form['Cat'])
            club = int(request.form['Club'])
            pruebas = request.form.getlist('prueba[]')
            mm_values = request.form.getlist('mm[]')
            ss_values = request.form.getlist('ss[]')
            sss_values = request.form.getlist('sss[]')

            # Format times with leading zeros
            mm_values = [f'{int(mm):02d}' for mm in mm_values]
            ss_values = [f'{int(ss):02d}' for ss in ss_values]
            sss_values = [f'{int(sss):03d}' for sss in sss_values]
            times = [f'{mm}:{ss}:{sss}' for mm, ss, sss in zip(mm_values, ss_values, sss_values)]

            current_date = datetime.date.today()
            date_string = current_date.strftime("%Y-%m-%d")

            #Connect to SQLite3 database and execute the INSERT
            with sqlite3.connect('database.db') as con:
                cur = con.cursor()
                cur.execute("""INSERT INTO Nadadores (NombreApellido, Sexo, IdCategoria, Idclub)
                            VALUES (?,?,?,?)""",(name, sex, cat, club))
                inserted_id = cur.lastrowid

                for (prueba, time) in zip(pruebas, times):
                    cur.execute("""INSERT INTO Nadadores_Pruebas
                                (IdNadador, IdPrueba, Fecha, TiempoPreInscripcion)
                                VALUES (?,?,?,?)""",
                                (inserted_id, int(prueba), date_string, time))

                con.commit()
                msg = "Registro añadido a la base de datos"
        except ConnectionAbortedError:
            con.rollback()
            msg = "Error in the INSERT"
            return render_template('result.html', msg=msg)
        finally:
            if con:
                con.close()

        # Send the transaction message to result.html
        return render_template('result.html', msg=msg)

# Route to SELECT all data from the database and display in a table
@app.route('/list')
def list_nadadores():
    """Show list of swimmers and personal info"""
    try:
        # Connect to the SQLite3 database and
        # SELECT all Rows from the Nadadores table.
        con = sqlite3.connect("database.db")
        con.row_factory = sqlite3.Row

        cur = con.cursor()
        cur.execute(""" SELECT n.Id, n.Sexo, n.NombreApellido, c.descripcion as Club,
                        cat.descripcion as Categoria FROM Nadadores n
                        INNER JOIN Clubes c on n.IdClub = c.Id
                        INNER JOIN Categorias cat on n.IdCategoria = cat.Id""")

        rows = cur.fetchall()
    except sqlite3.Error as error:
        print("Database error:", error)
        rows = []  # Initialize an empty result in case of an error.
    finally:
        if con:
            con.close()

    # Send the results of the SELECT (whether it's data or an empty list) to the list.html page
    return render_template("list.html", rows=rows)


@app.route("/view", methods=['POST', 'GET'])
def view():
    """Shows the personal information of the swimmer and the events in which he/she will compete"""
    try:
        # Use the hidden input value of 'id' from the request to get the rowid
        id_nadador = request.form.get('id')

        # Connect to the database and SELECT a specific rowid
        con = sqlite3.connect("database.db")
        con.row_factory = sqlite3.Row

        cur = con.cursor()
        cur.execute("""SELECT n.Id, n.Sexo, n.NombreApellido, c.descripcion as Club,
                        cat.descripcion as Categoria FROM Nadadores n
                        INNER JOIN Clubes c on n.IdClub = c.Id
                        INNER JOIN Categorias cat on n.IdCategoria = cat.Id  
                        WHERE n.Id = ?""", (id_nadador, ))

        row = cur.fetchone()
        cur.execute("""SELECT np.TiempoPreInscripcion,
                        CASE 
							WHEN TiempoCompeticion IS NULL THEN 'Aún no registrado'
							ELSE TiempoCompeticion
						END AS TiempoCompeticion,
                                p.descripcion 
                    FROM Nadadores_Pruebas np
                    INNER JOIN Pruebas p on np.IdPrueba = p.IdPrueba
                    WHERE np.IdNadador = ?""", (id_nadador, ))
        pruebas = cur.fetchall()
    except ConnectionAbortedError:
        row = None
    finally:
        con.close()

    return render_template("view.html", row=row, pruebas=pruebas)

# Route that will SELECT a specific row in the database then load an Edit form
@app.route("/edit", methods=['POST','GET'])
def edit():
    """Edit swimmer information"""
    if request.method == 'POST':
        try:
            # Use the hidden input value of id from the form to get the rowid
            id_nadador = request.form.get('id')
            # Connect to the database and SELECT a specific rowid
            con = sqlite3.connect("database.db")
            con.row_factory = sqlite3.Row

            cur = con.cursor()
            cur.execute(""" SELECT * FROM Nadadores n
                            WHERE n.Id = ?""",(id_nadador, ) )
            row = cur.fetchone()

            cur.execute(""" SELECT * FROM Nadadores_Pruebas np
                            INNER JOIN Pruebas p on np.IdPrueba = p.IdPrueba
                            WHERE np.IdNadador = ?""",(id_nadador, ))
            pruebas_nadador = cur.fetchall()

            cur.execute("SELECT * FROM Categorias")
            categorias = cur.fetchall()
            cur.execute("SELECT * FROM Clubes")
            clubes = cur.fetchall()
            cur.execute("SELECT * FROM Pruebas")
            pruebas = cur.fetchall()


        except sqlite3.Error:
            row = None
        finally:
            con.close()

        # Send the specific record of data to edit.html
        return render_template("edit.html",row=row, categorias=categorias,
                               clubes=clubes, pruebas=pruebas,
                               pruebas_nadador=pruebas_nadador)


@app.route("/editrec", methods=['POST','GET'])
def editrec():
    """Route used to execute the UPDATE statement on a specific record in the database"""
    # Data will be available from POST submitted by the form
    if request.method == 'POST':
        try:
            # Use the hidden input value of id from the form to get the rowid
            id_nadador = request.form.get('id')
            name = request.form['nombap']
            sex = request.form['Sexo']
            cat = int(request.form['Cat'])
            club = int(request.form['Club'])
            pruebas = request.form.getlist('prueba[]')
            mm_values = request.form.getlist('mm[]')
            ss_values = request.form.getlist('ss[]')
            sss_values = request.form.getlist('sss[]')

            # Format times with leading zeros
            mm_values = [f'{int(mm):02d}' for mm in mm_values]
            ss_values = [f'{int(ss):02d}' for ss in ss_values]
            sss_values = [f'{int(sss):03d}' for sss in sss_values]
            times = [f'{mm}:{ss}:{sss}' for mm, ss, sss in zip(mm_values, ss_values, sss_values)]

            current_date = datetime.date.today()
            date_string = current_date.strftime("%Y-%m-%d")

            # UPDATE a specific record in the database based on the rowid
            with sqlite3.connect('database.db') as con:
                cur = con.cursor()
                cur.execute("DELETE FROM Nadadores_Pruebas WHERE IdNadador = ?", (id_nadador, ))
                cur.execute("""UPDATE Nadadores SET NombreApellido = ?, Sexo = ?,
                            IdCategoria = ?, Idclub = ? WHERE Id = ?""",
                            (name, sex, cat, club, id_nadador))

                for (prueba, time) in zip(pruebas, times):
                    cur.execute("""INSERT INTO Nadadores_Pruebas
                                (IdNadador, IdPrueba, Fecha, TiempoPreInscripcion)
                                VALUES (?,?,?,?)""",
                                (id_nadador, int(prueba), date_string, time))

                con.commit()
        except sqlite3.Error:
            con.rollback()

        finally:
            con.close()

        return list_nadadores()


@app.route("/delete", methods=['POST','GET'])
def delete():
    """Delete a Nadador from database"""
    if request.method == 'POST':
        try:
             # Use the hidden input value of id from the form to get the rowid
            id_nadador = request.form.get('rowId')
            print(id_nadador)
            # Connect to the database and DELETE a specific record based on rowid
            with sqlite3.connect('database.db') as con:
                cur = con.cursor()
                cur.execute("DELETE FROM nadadores_pruebas WHERE IdNadador= ?",(id_nadador, ))
                cur.execute("DELETE FROM nadadores WHERE Id=?",(id_nadador, ))

                con.commit()
        except ConnectionAbortedError:
            con.rollback()

        finally:
            con.close()

    return list_nadadores()

if __name__ == "__main__":
    app.run(debug=True)
 