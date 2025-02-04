"""Functions to operate database"""
import sqlite3
import datetime
from models import Nadador, NadadorPrueba, Prueba, Categoria

def connect_db():
    """Returns conection to database"""
    return sqlite3.connect("database.db")

def get_categorias():
    """Gets all categories"""
    con = connect_db()
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("SELECT * FROM Categorias")
    categorias = cur.fetchall()
    con.close()
    return categorias

def get_clubes():
    """Gets all clubs"""
    con = connect_db()
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("SELECT * FROM Clubes")
    clubes = cur.fetchall()
    con.close()
    return clubes

def get_pruebas():
    """Gets all events"""
    con = connect_db()
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("SELECT * FROM Pruebas ")
    pruebas = cur.fetchall()
    con.close()
    return pruebas

def add_nadador(nadador):
    """Adds new swimmer to database"""
    try:
        with connect_db() as con:
            cur = con.cursor()
            cur.execute(
                """INSERT INTO Nadadores (NombreApellido, Sexo, IdCategoria, Idclub)
                VALUES (?,?,?,?)""",
                (nadador.nombre_apellido, nadador.sexo, nadador.id_categoria, nadador.id_club)
            )
            inserted_id = cur.lastrowid

            for prueba in nadador.pruebas:
                cur.execute(
                    """INSERT INTO Nadadores_Pruebas
                    (IdNadador, IdPrueba, Fecha, TiempoPreInscripcion)
                    VALUES (?,?,?,?)""",
                    (inserted_id, prueba.id_prueba, prueba.fecha, prueba.tiempo_preinscripcion)
                )

            con.commit()
            return "Registro añadido a la base de datos"
    except sqlite3.Error as err:
        return f"Error en el INSERT: {str(err)}"

def get_nadadores_info():
    """Gets all swimmers personal information"""
    try:
        con = connect_db()
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("""SELECT n.Id, n.Sexo, n.IdCategoria, n.IdClub,
                        n.NombreApellido, c.descripcion as Club,
                        cat.descripcion as Categoria FROM Nadadores n
                        LEFT JOIN Clubes c on n.IdClub = c.Id
                        LEFT JOIN Categorias cat on n.IdCategoria = cat.Id""")
        rows = cur.fetchall()
        nadador_list = []
        for row in rows:
            nadador = Nadador(row['NombreApellido'], row['Sexo'], row['IdCategoria'], row['IdClub'])
            nadador.id_nadador = row['Id']
            nadador.club = row["Club"]
            nadador.categoria = row["Categoria"]
            nadador_list.append(nadador)
    except sqlite3.Error as err:
        print("Database error:", err)
        nadador_list = []
    finally:
        con.close()
    return nadador_list

def get_nadador_info(id_nadador):
    """Get one swimmer personal info as a Nadador object"""
    try:
        con = connect_db()
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("""SELECT n.Id, n.Sexo, n.IdCategoria, n.IdClub,
                        n.NombreApellido, c.descripcion as Club,
                        cat.descripcion as Categoria FROM Nadadores n
                        LEFT JOIN Clubes c on n.IdClub = c.Id
                        LEFT JOIN Categorias cat on n.IdCategoria = cat.Id
                        WHERE n.Id = ?""", (id_nadador, ))
        row = cur.fetchone()
        if row:
            nadador = Nadador(row['NombreApellido'], row['Sexo'], row['IdCategoria'], row['IdClub'])
            nadador.id_nadador = row['Id']
            nadador.categoria = row['Categoria']
            nadador.club = row['Club']
        else:
            nadador = None
    except sqlite3.Error as err:
        print("Database error:", err)
        nadador = None
    finally:
        con.close()
    return nadador

def get_nadador_pruebas(id_nadador):
    """Gets the events in which the swimmer is registered as NadadorPrueba objects"""
    try:
        con = connect_db()
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("""SELECT np.IdPrueba, np.TiempoPreInscripcion,
                        CASE 
                            WHEN np.TiempoCompeticion IS NULL THEN 'Aún no registrado'
                            ELSE np.TiempoCompeticion
                        END AS TiempoCompeticion,
                                p.descripcion 
                    FROM Nadadores_Pruebas np
                    INNER JOIN Pruebas p on np.IdPrueba = p.IdPrueba
                    WHERE np.IdNadador = ?""", (id_nadador,))
        rows = cur.fetchall()
        nadador_pruebas = []
        for row in rows:
            nadador_prueba = NadadorPrueba(row['IdPrueba'], row['TiempoPreInscripcion'])
            nadador_prueba.id_nadador = id_nadador
            nadador_prueba.tiempo_competencia = row['TiempoCompeticion']
            nadador_prueba.descripcion = row['descripcion']
            nadador_pruebas.append(nadador_prueba)
    except sqlite3.Error as err:
        print("Database error:", err)
        nadador_pruebas = []
    finally:
        con.close()
    return nadador_pruebas

def update_nadador_info(id_nadador, name, sex, cat, club):
    """Updates the swimmer personal info"""
    try:
        con = connect_db()
        con.execute("""UPDATE Nadadores SET NombreApellido = ?, Sexo = ?,
                        IdCategoria = ?, Idclub = ? WHERE Id = ?""",
                    (name, sex, cat, club, id_nadador))
        con.commit()
    except sqlite3.Error as err:
        print("Database error:", err)
        con.rollback()
    finally:
        con.close()

def insert_nadador_pruebas_if_not_exists(id_nadador, pruebas):
    """Inserts new events for a specific swimmer if they don't already exist"""
    try:
        con = connect_db()

        cur = con.cursor()
        cur.execute("SELECT IdPrueba FROM Nadadores_Pruebas WHERE IdNadador = ?", (id_nadador,))
        existing_pruebas = [row[0] for row in cur.fetchall()]
        id_pruebas = [int(prueba[0]) for prueba in pruebas]
        print(id_pruebas)

        for existing_prueba in existing_pruebas:
            print(existing_prueba)
            if existing_prueba in id_pruebas:
                con.execute("DELETE FROM Nadadores_Pruebas WHERE IdNadador = ? AND IdPrueba = ?",
                            (id_nadador, existing_prueba))

        for prueba, time in pruebas:
            con.execute("""INSERT OR IGNORE INTO Nadadores_Pruebas
                        (IdNadador, IdPrueba, TiempoPreInscripcion, Fecha)
                        VALUES (?,?,?,?)""",
                        (id_nadador, int(prueba), time, datetime.date.today().strftime("%Y-%m-%d")))

        con.commit()
    except sqlite3.Error as err:
        print("Database error:", err)
        con.rollback()
    finally:
        con.close()

def delete_nadador(id_nadador):
    """Delete swimmer and all the events related"""
    try:
        with connect_db() as con:
            cur = con.cursor()
            cur.execute("DELETE FROM nadadores_pruebas WHERE IdNadador=?", (id_nadador,))
            cur.execute("DELETE FROM nadadores WHERE Id=?", (id_nadador,))
            con.commit()
    except sqlite3.Error as err:
        print("Database error:", err)
        con.rollback()

def get_all_pruebas_grouped():
    """Gets all the events crossed with category and gender"""
    try:
        con = connect_db()
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("""SELECT p.IdPrueba, p.descripcion as Prueba,
                        count(*) AS NumeroNadadores, count(np.Orden) as Orden, 
                        count(np.OrdenRec) as OrdenRec, p.cantNadadores
                        FROM Pruebas p
                        INNER JOIN Nadadores_Pruebas np on p.IdPrueba = np.IdPrueba
                        GROUP BY p.IdPrueba
                    ORDER BY NumeroNadadores DESC;
                    """)
        rows = cur.fetchall()
    except sqlite3.Error as err:
        print("Database error:", err)
        rows = []
    finally:
        con.close()
    return rows

def get_nadadores_prueba(id_prueba):
    """Get all swimmers for a specific event"""
    try:
        con = connect_db()
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("""SELECT np.IdNadador, np.IdPrueba, np.TiempoPreInscripcion,
                        np.Pileta, np.Orden
                        FROM Nadadores_Pruebas np
                        INNER JOIN Nadadores n on n.Id = np.IdNadador
                        WHERE IdPrueba = ?
                        ORDER BY np.TiempoPreInscripcion
                    """, (id_prueba,))
        rows = cur.fetchall()
    except sqlite3.Error as err:
        print("Database error:", err)
        rows = []
    finally:
        con.close()
    return rows

def get_nadadores_prueba_rec(id_prueba):
    """Get all swimmers for a specific event with random order"""
    try:
        con = connect_db()
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("""SELECT np.IdNadador, np.IdPrueba, np.TiempoPreInscripcion,
                        np.PiletaRec, np.OrdenRec
                        FROM Nadadores_Pruebas np
                        INNER JOIN Nadadores n on n.Id = np.IdNadador
                        WHERE IdPrueba = ? 
                        ORDER BY RANDOM()
                    """, (id_prueba,))
        rows = cur.fetchall()
    except sqlite3.Error as err:
        print("Database error:", err)
        rows = []
    finally:
        con.close()
    return rows

def update_cant_nadadores(id_prueba, cant_nad):
    """Update the number of swimmers in an event when the order is generated"""
    try:
        con = connect_db()
        con.execute("UPDATE Pruebas SET cantNadadores = ? WHERE IdPrueba = ?",
                    (cant_nad, id_prueba))
        con.commit()
    except sqlite3.Error as err:
        print("Database error:", err)
        con.rollback()
    finally:
        con.close()

def update_nadador_pruebas(nadador_pruebas, id_prueba):
    """Update pool and order values for nadador_pruebas rows"""
    try:
        con = connect_db()
        for row in nadador_pruebas:
            con.execute("""UPDATE Nadadores_Pruebas SET Orden = ?, Pileta = ?
                        WHERE IdNadador = ? and IdPrueba = ?""",
                        (row[-1], row[-2], row[0], id_prueba))

        con.commit()
    except sqlite3.Error as err:
        print("Database error:", err)
        con.rollback()
    finally:
        con.close()

def update_nadador_pruebas_rec(nadador_pruebas, id_prueba):
    """Update pool and order values for nadador_pruebas rows"""
    try:
        con = connect_db()
        for row in nadador_pruebas:
            con.execute("""UPDATE Nadadores_Pruebas SET OrdenRec = ?, PiletaRec = ?
                        WHERE IdNadador = ? and IdPrueba = ?""",
                        (row[-1], row[-2], row[0], id_prueba))
        con.commit()
    except sqlite3.Error as err:
        print("Database error:", err)
        con.rollback()
    finally:
        con.close()

def get_ordered_swimmers(id_prueba):
    """Get all sorted swimmers for a specific event"""
    try:
        con = connect_db()
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("""SELECT np.IdNadador, np.TiempoCompeticion, n.NombreApellido,
                        c.descripcion as Club,
                        np.TiempoPreInscripcion, np.Pileta, np.Orden
                        FROM Nadadores_Pruebas np
                        INNER JOIN Nadadores n on n.Id = np.IdNadador
                        INNER JOIN Clubes c ON n.IdClub = c.Id
                        WHERE np.IdPrueba = ?
                        ORDER BY np.Pileta DESC
                    """, (id_prueba, ))
        rows = cur.fetchall()
    except sqlite3.Error as err:
        print("Database error:", err)
        rows = []
    finally:
        con.close()
    return rows

def get_ordered_swimmers_rec(id_prueba):
    """Get all sorted swimmers for a specific event"""
    try:
        con = connect_db()
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("""SELECT n.NombreApellido, np.TiempoPreInscripcion, c.descripcion as Club,
                        np.PiletaRec, np.OrdenRec as Orden
                        FROM Nadadores_Pruebas np
                        INNER JOIN Nadadores n on n.Id = np.IdNadador
                        INNER JOIN Clubes c ON n.IdClub = c.Id
                        WHERE np.IdPrueba = ? 
                        ORDER BY np.PiletaRec DESC
                    """, (id_prueba, ))
        rows = cur.fetchall()
    except sqlite3.Error as err:
        print("Database error:", err)
        rows = []
    finally:
        con.close()
    return rows

def get_one_prueba(id_prueba):
    """Get one event by id"""
    try:
        con = connect_db()
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("""SELECT *
                        FROM Pruebas
                        WHERE IdPrueba = ?""", (id_prueba, ))
        row = cur.fetchone()
        if row:
            prueba = Prueba(row['Descripcion'])
            prueba.id_prueba = row['IdPrueba']
        else:
            prueba = None
    except sqlite3.Error as err:
        print("Database error:", err)
        prueba = None
    finally:
        con.close()
    return prueba

def get_one_categoria(id_categoria):
    """Get one category by id"""
    try:
        con = connect_db()
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("""SELECT *
                        FROM Categorias
                        WHERE Id = ?""", (id_categoria, ))
        row = cur.fetchone()
        if row:
            categoria = Categoria(row['Descripcion'])
            categoria.id_categoria = row['Id']
        else:
            categoria = None
    except sqlite3.Error as err:
        print("Database error:", err)
        categoria = None
    finally:
        con.close()
    return categoria

def insert_comp_time(id_prueba, id_nadador, tiempo):
    """Insert the competitive time for a swimmer in an event"""
    try:
        con = connect_db()
        con.execute("""UPDATE Nadadores_Pruebas SET TiempoCompeticion = ?
                        WHERE IdNadador = ? and IdPrueba = ?""",
                        (tiempo, id_nadador, id_prueba))
        con.commit()
    except sqlite3.Error as err:
        print("Database error:", err)
        con.rollback()
    finally:
        con.close()

def del_comp_time(id_prueba, id_nadador):
    """Delete the competitive time for a swimmer in an event"""
    try:
        con = connect_db()
        con.execute("""UPDATE Nadadores_Pruebas SET TiempoCompeticion = NULL
                        WHERE IdNadador = ? and IdPrueba = ?""",
                        (id_nadador, id_prueba))
        con.commit()
    except sqlite3.Error as err:
        print("Database error:", err)
        con.rollback()
    finally:
        con.close()

def get_ranked_swimmers(id_prueba):
    """Get all ranked swimmers for a specific event based on cometition time"""
    try:
        con = connect_db()
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("""SELECT n.NombreApellido, np.TiempoCompeticion, c.descripcion as Club
                        FROM Nadadores_Pruebas np
                        INNER JOIN Nadadores n ON n.Id = np.IdNadador
                        INNER JOIN Clubes c ON n.IdClub = c.Id
                        WHERE np.IdPrueba = ? 
                        ORDER BY
                        CASE
                            WHEN np.TiempoCompeticion IS NULL THEN 1
                            ELSE 0
                        END,
                        np.TiempoCompeticion ASC;
                    """, (id_prueba,))
        rows = cur.fetchall()
    except sqlite3.Error as err:
        print("Database error:", err)
        rows = []
    finally:
        con.close()
    return rows

def get_top_3_swimmers(id_prueba):
    """Get TOP 3 swimmers for a specific event based on cometition time"""
    try:
        con = connect_db()
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("""SELECT n.NombreApellido, np.TiempoCompeticion, c.descripcion as Club
                        FROM Nadadores_Pruebas np
                        INNER JOIN Nadadores n ON n.Id = np.IdNadador
                        INNER JOIN Clubes c ON n.IdClub = c.Id
                        WHERE np.IdPrueba = ? 
                        ORDER BY
                        CASE
                            WHEN np.TiempoCompeticion IS NULL THEN 1
                            ELSE 0
                        END,
                        np.TiempoCompeticion ASC
						LIMIT 3;
                    """, (id_prueba,))
        rows = cur.fetchall()
    except sqlite3.Error as err:
        print("Database error:", err)
        rows = []
    finally:
        con.close()
    return rows

def get_pruebas_info():
    """Gets all events information"""
    try:
        con = connect_db()
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("""SELECT * FROM pruebas
                    ORDER BY IdPrueba DESC""")
        rows = cur.fetchall()
        pruebas_list = []
        for row in rows:
            prueba = Prueba(row['descripcion'])
            prueba.id_prueba = row["IdPrueba"]
            pruebas_list.append(prueba)
    except sqlite3.Error as err:
        print("Database error:", err)
        pruebas_list = []
    finally:
        con.close()
    return pruebas_list


def update_prueba(prueba):
    """Update event info"""
    try:
        con = connect_db()
        con.execute("""UPDATE Pruebas SET descripcion = ?
                        WHERE IdPrueba = ?""",
                        (prueba.descripcion, prueba.id_prueba))
        con.commit()
    except sqlite3.Error as err:
        print("Database error:", err)
        con.rollback()
    finally:
        con.close()

def del_prueba(id_prueba):
    """Delete event"""
    try:
        con = connect_db()
        con.execute("""DELETE FROM Pruebas
                        WHERE IdPrueba = ?""",
                        (id_prueba,))
        con.commit()
    except sqlite3.Error as err:
        print("Database error:", err)
        con.rollback()
    finally:
        con.close()

def insert_prueba(prueba):
    """Adds new event to database"""
    try:
        with connect_db() as con:
            cur = con.cursor()
            cur.execute(
                """INSERT INTO Pruebas(descripcion)
                VALUES (?)""",
                (prueba.descripcion,)
            )
            con.commit()
            print("Registro añadido a la base de datos")
    except sqlite3.Error as err:
        print(f"Error en el INSERT: {str(err)}")

def get_categorias_info():
    """Gets all categories information"""
    try:
        con = connect_db()
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("""SELECT * FROM categorias""")
        rows = cur.fetchall()
        categorias_list = []
        for row in rows:
            categoria = Categoria(row['descripcion'])
            categoria.id_categoria = row["Id"]
            categorias_list.append(categoria)
    except sqlite3.Error as err:
        print("Database error:", err)
        categorias_list = []
    finally:
        con.close()
    return categorias_list

def update_categoria(categoria):
    """Update category info"""
    print(categoria.id_categoria)
    try:
        con = connect_db()
        con.execute("""UPDATE Categorias SET descripcion = ?
                        WHERE Id = ?""",
                        (categoria.descripcion, categoria.id_categoria))
        con.commit()
    except sqlite3.Error as err:
        print("Database error:", err)
        con.rollback()
    finally:
        con.close()

def del_categoria(id_categoria):
    """Delete event"""
    try:
        con = connect_db()
        con.execute("""DELETE FROM Categorias
                        WHERE Id = ?""",
                        (id_categoria,))
        con.commit()
    except sqlite3.Error as err:
        print("Database error:", err)
        con.rollback()
    finally:
        con.close()

def insert_categoria(categoria):
    """Adds new category to database"""
    print(categoria.descripcion)
    try:
        with connect_db() as con:
            cur = con.cursor()
            cur.execute(
                """INSERT INTO Categorias(descripcion)
                VALUES (?)""",
                (categoria.descripcion,)
            )
            con.commit()
            print("Registro añadido a la base de datos")
    except sqlite3.Error as err:
        print(f"Error en el INSERT: {str(err)}")

def get_clubes_info():
    """Gets all clubs information"""
    try:
        con = connect_db()
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("""SELECT * FROM Clubes""")
        rows = cur.fetchall()
        clubes_list = []
        for row in rows:
            club = Categoria(row['descripcion'])
            club.id_club = row["Id"]
            clubes_list.append(club)
    except sqlite3.Error as err:
        print("Database error:", err)
        clubes_list = []
    finally:
        con.close()
    return clubes_list

def update_club(club):
    """Update club info"""
    try:
        con = connect_db()
        con.execute("""UPDATE Clubes SET descripcion = ?
                        WHERE Id = ?""",
                        (club.descripcion, club.id_club))
        con.commit()
    except sqlite3.Error as err:
        print("Database error:", err)
        con.rollback()
    finally:
        con.close()

def del_club(id_club):
    """Delete club"""
    try:
        con = connect_db()
        con.execute("""DELETE FROM Clubes
                        WHERE Id = ?""",
                        (id_club,))
        con.commit()
    except sqlite3.Error as err:
        print("Database error:", err)
        con.rollback()
    finally:
        con.close()

def insert_club(club):
    """Adds new category to database"""
    try:
        with connect_db() as con:
            cur = con.cursor()
            cur.execute(
                """INSERT INTO Clubes(descripcion)
                VALUES (?)""",
                (club.descripcion,)
            )
            con.commit()
            print("Registro añadido a la base de datos")
    except sqlite3.Error as err:
        print(f"Error en el INSERT: {str(err)}")

def get_club_swimmers_info(id_club):
    """Get all the swimmers and events where registered for a club"""
    try:
        con = connect_db()
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("""SELECT  p.IdPrueba,
                        n.NombreApellido, p.descripcion as 'Prueba',
                        np.Pileta as 'Serie', np.Orden as 'Andarivel'
                        FROM Nadadores n
                        INNER JOIN Nadadores_Pruebas np on n.Id = np.IdNadador
                        INNER JOIN Pruebas p on p.IdPrueba = np.IdPrueba 
                        WHERE n.Idclub = ?
                        ORDER BY p.IdPrueba, np.Pileta, np.Orden
                    """, (id_club,))
        rows = cur.fetchall()
    except sqlite3.Error as err:
        print("Database error:", err)
        rows = []
    finally:
        con.close()
    return rows

def get_club_swimmers_result(id_club):
    """Get all the swimmers and events with competition time for a club"""
    try:
        con = connect_db()
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("""SELECT
                        n.NombreApellido, p.descripcion as 'Prueba',
                        CASE 
                            WHEN np.TiempoPreInscripcion LIKE '99%' THEN NULL
                            ELSE np.TiempoPreInscripcion 
                        END AS 'Tiempo pre-clasificacion',  
                        np.TiempoCompeticion as 'Tiempo Torneo'
                        FROM Nadadores n
                        INNER JOIN Nadadores_Pruebas np on n.Id = np.IdNadador
                        INNER JOIN Pruebas p on p.IdPrueba = np.IdPrueba 
                        WHERE n.Idclub = ?
                        ORDER BY p.IdPrueba, n.NombreApellido
                    """, (id_club,))
        rows = cur.fetchall()
    except sqlite3.Error as err:
        print("Database error:", err)
        rows = []
    finally:
        con.close()
    return rows
