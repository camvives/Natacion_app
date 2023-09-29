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
            sex = int(request.form['Sexo'])
            cat = int(request.form['Cat'])
            club = int(request.form['Club'])
            pruebas = request.form.getlist('prueba[]')
            mm_values = request.form.getlist('mm[]')
            ss_values = request.form.getlist('ss[]')
            sss_values = request.form.getlist('sss[]')

            # Format times with leading zeros
            mm_values = [f'{int(mm):02d}' for mm in mm_values]
            ss_values = [f'{int(ss):02d}' for ss in ss_values]
            sss_values = [f'{int(sss):02d}' for sss in sss_values]
            times = [f'{mm}:{ss}:{sss}' for mm, ss, sss in zip(mm_values, ss_values, sss_values)]

            current_date = datetime.date.today()
            date_string = current_date.strftime("%Y-%m-%d")

            print(date_string)

            #Connect to SQLite3 database and execute the INSERT
            with sqlite3.connect('database.db') as con:
                cur = con.cursor()
                cur.execute("INSERT INTO Nadadores (NombreApellido, Sexo, IdCategoria, Idclub) VALUES (?,?,?,?)",(name, sex, cat, club))
                inserted_id = cur.lastrowid
                
                for (prueba, time) in enumerate(zip(pruebas, times)):
                    cur.execute("""INSERT INTO Nadadores_Pruebas (IdNadador, IdPrueba, Fecha, TiempoPreInscripcion)
                                VALUES (?,?,?,?)""", (inserted_id, int(prueba), date_string, time[1]))
                                
                con.commit()
                msg = "Record successfully added to database"
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
def list():
    # Connect to the SQLite3 datatabase and
    # SELECT rowid and all Rows from the students table.
    con = sqlite3.connect("database.db")
    con.row_factory = sqlite3.Row

    cur = con.cursor()
    cur.execute("SELECT rowid, * FROM students")

    rows = cur.fetchall()
    con.close()
    # Send the results of the SELECT to the list.html page
    return render_template("list.html",rows=rows)

# Route that will SELECT a specific row in the database then load an Edit form
@app.route("/edit", methods=['POST','GET'])
def edit():
    if request.method == 'POST':
        try:
            # Use the hidden input value of id from the form to get the rowid
            id = request.form['id']
            # Connect to the database and SELECT a specific rowid
            con = sqlite3.connect("database.db")
            con.row_factory = sqlite3.Row

            cur = con.cursor()
            cur.execute("SELECT rowid, * FROM students WHERE rowid = " + id)

            rows = cur.fetchall()
        except:
            id=None
        finally:
            con.close()
            # Send the specific record of data to edit.html
            return render_template("edit.html",rows=rows)

# Route used to execute the UPDATE statement on a specific record in the database
@app.route("/editrec", methods=['POST','GET'])
def editrec():
    # Data will be available from POST submitted by the form
    if request.method == 'POST':
        try:
            # Use the hidden input value of id from the form to get the rowid
            rowid = request.form['rowid']
            nm = request.form['nm']
            addr = request.form['add']
            city = request.form['city']
            zip = request.form['zip']

            # UPDATE a specific record in the database based on the rowid
            with sqlite3.connect('database.db') as con:
                cur = con.cursor()
                cur.execute("UPDATE students SET name='"+nm+"', addr='"+addr+"', city='"+city+"', zip='"+zip+"' WHERE rowid="+rowid)

                con.commit()
                msg = "Record successfully edited in the database"
        except:
            con.rollback()
            msg = "Error in the Edit: UPDATE students SET name="+nm+", addr="+addr+", city="+city+", zip="+zip+" WHERE rowid="+rowid

        finally:
            con.close()
            # Send the transaction message to result.html
            return render_template('result.html',msg=msg)

# Route used to DELETE a specific record in the database
@app.route("/delete", methods=['POST','GET'])
def delete():
    if request.method == 'POST':
        try:
             # Use the hidden input value of id from the form to get the rowid
            rowid = request.form['id']
            # Connect to the database and DELETE a specific record based on rowid
            with sqlite3.connect('database.db') as con:
                    cur = con.cursor()
                    cur.execute("DELETE FROM students WHERE rowid="+rowid)

                    con.commit()
                    msg = "Record successfully deleted from the database"
        except:
            con.rollback()
            msg = "Error in the DELETE"

        finally:
            con.close()
            # Send the transaction message to result.html
            return render_template('result.html',msg=msg)

if __name__ == "__main__":
    app.run(debug=True)
