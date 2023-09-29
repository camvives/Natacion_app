"""Create database and all tables to run the app"""

import sqlite3

conn = sqlite3.connect('database.db')
print("Connected to database successfully")

conn.execute("""
    CREATE TABLE IF NOT EXISTS Nadadores (
        Id INTEGER PRIMARY KEY,
        Idclub INTEGER,
        IdCategoria INTEGER,
        NombreApellido TEXT,
        Sexo TEXT,
        FOREIGN KEY (Idclub) REFERENCES Clubes(Id),
        FOREIGN KEY (idCategoria) REFERENCES Categorias(Id)
    )
""")

# Create the Categorias table
conn.execute("""
    CREATE TABLE IF NOT EXISTS Categorias (
        Id INTEGER PRIMARY KEY,
        descripcion TEXT
    )
""")

# Create the Clubes table
conn.execute("""
    CREATE TABLE IF NOT EXISTS Clubes (
        Id INTEGER PRIMARY KEY,
        descripcion TEXT
    )
""")

# Create the Nadadores_Pruebas table
conn.execute("""
    CREATE TABLE IF NOT EXISTS Nadadores_Pruebas (
        IdNadador INTEGER,
        IdPrueba INTEGER,
        Fecha TEXT,
        TiempoPreInscripcion TEXT,
        TiempoCompeticion TEXT,
        PRIMARY KEY (IdNadador, IdPrueba),
        FOREIGN KEY (IdNadador) REFERENCES Nadadores(Id),
        FOREIGN KEY (IdPrueba) REFERENCES Pruebas(IdPrueba)
    )
""")

# Create the Pruebas table
conn.execute("""
    CREATE TABLE IF NOT EXISTS Pruebas (
        IdPrueba INTEGER PRIMARY KEY,
        descripcion TEXT
    )
""")

print("Tables created successfully!")

conn.close()
