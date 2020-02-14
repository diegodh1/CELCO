"""
    Conexion a SQLServer con Python
    CRUD evitando inyecciones SQL
"""
import pyodbc
server = '192.168.1.7'
db_name = 'siprocava'
user = 'sa'
password = 'Cristiano1994'
try:
    conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=' +
                              server+';DATABASE='+db_name+';UID='+user+';PWD=' + password)
    print("Conexion realizada")
    # OK! conexion exitosa
except Exception as e:
    # Atrapar error
    print("Ocurrio un error al conectar a SQL Server: ", e)