"""Create database and all tables to run the app"""

import sqlite3

conn = sqlite3.connect('database.db')
print("Connected to database successfully")

conn.execute("""
        CREATE TABLE Categorias (
        Id INTEGER PRIMARY KEY,
        descripcion TEXT
    )
""")

conn.execute("""
        CREATE TABLE Clubes (
        Id INTEGER PRIMARY KEY,
        descripcion TEXT
    )
""")

conn.execute("""
        CREATE TABLE Pruebas (
        IdPrueba INTEGER PRIMARY KEY,
        descripcion TEXT
    )
""")

conn.execute("""
        CREATE TABLE "Nadadores" (
        "Id"	INTEGER,
        "Idclub"	INTEGER,
        "IdCategoria"	INTEGER,
        "NombreApellido"	TEXT,
        "Sexo"	TEXT,
        FOREIGN KEY("Idclub") REFERENCES "Clubes"("Id"),
        FOREIGN KEY("IdCategoria") REFERENCES "Categorias"("Id"),
        PRIMARY KEY("Id")
)
""")

conn.execute("""
    CREATE TABLE "Nadadores_Pruebas" (
	"IdNadador"	INTEGER,
	"IdPrueba"	INTEGER,
	"Fecha"	TEXT,
	"TiempoPreInscripcion"	TEXT,
	"TiempoCompeticion"	TEXT,
	"Orden"	INTEGER,
	"Pileta"	INTEGER,
	"OrdenRec"	INTEGER,
	"PiletaRec"	INTEGER,
	FOREIGN KEY("IdNadador") REFERENCES "Nadadores"("Id"),
	FOREIGN KEY("IdPrueba") REFERENCES "Pruebas"("IdPrueba"),
	PRIMARY KEY("IdNadador","IdPrueba")
)
""")

print("Tables created successfully!")

conn.close()
