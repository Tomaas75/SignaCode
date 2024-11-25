import mysql.connector
from mysql.connector import Error

def crear_conexion():
    """Crea una conexión con la base de datos MySQL y la retorna si es exitosa."""
    conexion = None  # Definimos la variable de la conexión fuera del bloque try
    try:
        # Establecer la conexión a la base de datos
        conexion = mysql.connector.connect(
            host="localhost",        # Dirección del servidor MySQL (usualmente localhost)
            user="root",             # Tu usuario de MySQL
            password="1234",         # Tu contraseña de MySQL
            database="mi_base_de_datos"  # El nombre de tu base de datos
        )

        # Verificar si la conexión fue exitosa
        if conexion.is_connected():
            print("Conexión exitosa a la base de datos")
            return conexion
        else:
            print("Error al conectar a la base de datos")
            return None
    except Error as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None
    finally:
        # Si la conexión falla, no es necesario cerrar, ya que nunca se abrió
        if conexion and conexion.is_connected():
            conexion.close()
            print("Conexión cerrada después de usarla.")
