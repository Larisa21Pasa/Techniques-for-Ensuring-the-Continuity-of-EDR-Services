import sqlite3

# Conectare la baza de date (sau creare dacă nu există)
connection = sqlite3.connect('c2_server.db')

# Crearea unui cursor pentru a executa comenzi SQL
cursor = connection.cursor()


# Citirea datelor din tabel
cursor.execute('SELECT * FROM example')
rows = cursor.fetchall()
for row in rows:
    print(row)

# Închiderea conexiunii
connection.close()
