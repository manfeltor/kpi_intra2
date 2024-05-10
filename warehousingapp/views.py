from django.shortcuts import render
import pyodbc
from .authdata import server, db, user, passw

def connect_prim(serv, database, usr, passw):

    connection = pyodbc.connect(f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={serv};DATABASE={database};UID={usr};PWD={passw}')

    cursor = connection.cursor()

    cursor.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'CLIENTES'")

    rows = cursor.fetchall()

    cursor.close()
    connection.close()

    print(type(rows))
    print(rows)

    return None