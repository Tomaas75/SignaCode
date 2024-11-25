from flask import Flask, request, session, render_template, redirect, url_for
from decimal import Decimal
from conexion import crear_conexion
import mysql.connector
from mysql.connector import Error
import bcrypt
from datetime import datetime 

app = Flask(__name__)
app.secret_key = 'secreto_cajero'  # Necesario para manejar sesiones en Flask

def crear_conexion():
    """Crea una conexión con la base de datos MySQL y la retorna si es exitosa."""
    try:
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


app = Flask(__name__)
app.secret_key = 'secreto_cajero'

# Clase que representa una cuenta bancaria
class Cuenta:
    def __init__(self, numero_cuenta, contrasena, saldo_inicial, nombre_usuario, correo, edad, tipo_documento, numero_telefono, numero_documento):
        self.numero_cuenta = numero_cuenta
        self.contrasena = contrasena
        self.saldo = Decimal(saldo_inicial)
        self.puntos_vivecolombia = 0
        self.nombre_usuario = nombre_usuario
        self.correo = correo
        self.edad = edad
        self.tipo_documento = tipo_documento
        self.numero_telefono = numero_telefono
        self.numero_documento = numero_documento
        self.historial_transacciones = []  # Lista para guardar las transacciones

    def autenticar(self, contrasena):
        return self.contrasena == contrasena

    def consultar_saldo(self):
        return self.saldo

    def retirar(self, monto):
        if monto <= self.saldo:
            self.saldo -= monto
            # Guardamos la transacción en el historial
            self.historial_transacciones.append(f"Retiro de {monto} en saldo.")
            return True
        return False

    def transferir(self, cuenta_destino, monto):
        if monto <= self.saldo:
            self.saldo -= monto
            cuenta_destino.saldo += monto
            # Guardamos las transacciones en el historial
            self.historial_transacciones.append(f"Transferencia de {monto} a cuenta {cuenta_destino.numero_cuenta}.")
            return True
        return False

    def consultar_puntos(self):
        return self.puntos_vivecolombia

    def canjear_puntos(self, puntos):
        if puntos <= self.puntos_vivecolombia:
            self.puntos_vivecolombia -= puntos
            return True
        return False

    def obtener_historial(self):
        return self.historial_transacciones

# Banco que maneja todas las cuentas
class Banco:
    def __init__(self):
        self.cuentas = {}

    def crear_cuenta(self, numero_cuenta, contrasena, saldo_inicial, nombre_usuario, correo, edad, tipo_documento, numero_telefono, numero_documento):
        if numero_cuenta in self.cuentas:
            raise ValueError("La cuenta ya existe.")
        cuenta = Cuenta(numero_cuenta, contrasena, saldo_inicial, nombre_usuario, correo, edad, tipo_documento, numero_telefono, numero_documento)
        self.cuentas[numero_cuenta] = cuenta

    def autenticar(self, numero_cuenta, contrasena):
        cuenta = self.cuentas.get(numero_cuenta)
        if cuenta and cuenta.autenticar(contrasena):
            return cuenta
        return None

# Crear una instancia del Banco
banco = Banco()

# Ruta para la página principal (redirige a home)
@app.route('/')
def index():
    return redirect(url_for('home'))  # Redirige a la página de inicio (home)

# Ruta para la página de inicio (home)
@app.route('/home')
def home():
    # Si el usuario ya está autenticado, redirige a la página de bienvenida
    if 'numero_cuenta' in session:
        return redirect(url_for('bienvenida'))  # Redirige a bienvenida si está autenticado
    return render_template('home.html')  # Página de inicio donde puedes iniciar sesión
    
@app.route('/bienvenida')
def bienvenida():
    if 'numero_cuenta' not in session:
        return redirect(url_for('home'))  # Redirige si no está autenticado

    numero_cuenta = session['numero_cuenta']
    
    conexion = crear_conexion()
    if conexion:
        try:
            cursor = conexion.cursor()
            query = """
                SELECT contrasena, saldo_inicial, nombre_usuario, correo, edad, tipo_documento, 
                numero_telefono, numero_documento 
                FROM cuentas 
                WHERE numero_cuenta = %s
            """
            cursor.execute(query, (numero_cuenta,))
            cuenta = cursor.fetchone()
            
            if cuenta:
                # Convertir el resultado en un diccionario
                cuenta_data = {
                    'nombre_usuario': cuenta[2],
                    'correo': cuenta[3],
                    'edad': cuenta[4],
                    'tipo_documento': cuenta[5],
                    'numero_telefono': cuenta[6],
                    'numero_documento': cuenta[7]
                }

                # Pasar los datos a la plantilla
                return render_template('index.html', cuenta=cuenta_data)
            else:
                session.pop('numero_cuenta', None)
                return redirect(url_for('home'))
        except mysql.connector.Error as err:
            return render_template('home.html', mensaje="Error al recuperar los datos.")
        finally:
            cursor.close()
            conexion.close()

    return redirect(url_for('home'))

# Ruta para iniciar sesión
@app.route('/crear_cuenta', methods=['GET', 'POST'])
def crear_cuenta():
    if request.method == 'POST':
        # Obtener datos del formulario
        numero_cuenta = request.form['numero_cuenta']
        contrasena = request.form['contrasena']
        saldo_inicial = request.form['saldo_inicial']
        nombre_usuario = request.form['nombre_completo']
        correo = request.form['correo_electronico']
        edad = request.form['edad']
        tipo_documento = request.form['tipo_documento']
        numero_telefono = request.form['numero_telefono']
        numero_documento = request.form['numero_documento']

        # Hashear la contraseña antes de guardarla
        contrasena_hash = bcrypt.hashpw(contrasena.encode('utf-8'), bcrypt.gensalt())

        # Crear conexión con la base de datos
        conexion = crear_conexion()
        if conexion:
            try:
                cursor = conexion.cursor()

                # Verificar si el numero_cuenta ya existe en la base de datos
                query_verificacion_cuenta = "SELECT COUNT(*) FROM cuentas WHERE numero_cuenta = %s"
                cursor.execute(query_verificacion_cuenta, (numero_cuenta,))
                resultado_cuenta = cursor.fetchone()

                # Verificar si el numero_documento ya existe en la base de datos
                query_verificacion_documento = "SELECT COUNT(*) FROM cuentas WHERE numero_documento = %s"
                cursor.execute(query_verificacion_documento, (numero_documento,))
                resultado_documento = cursor.fetchone()

                # Verificar si el correo ya existe en la base de datos
                query_verificacion_correo = "SELECT COUNT(*) FROM cuentas WHERE correo = %s"
                cursor.execute(query_verificacion_correo, (correo,))
                resultado_correo = cursor.fetchone()

                # Verificar si el numero_telefono ya existe en la base de datos
                query_verificacion_telefono = "SELECT COUNT(*) FROM cuentas WHERE numero_telefono = %s"
                cursor.execute(query_verificacion_telefono, (numero_telefono,))
                resultado_telefono = cursor.fetchone()

                # Si el número de cuenta ya existe, mostrar mensaje de error
                if resultado_cuenta[0] > 0:
                    return render_template('crear_cuenta.html', mensaje="La cuenta ya existe. Intenta con otro número de cuenta.")
                
                # Si el número de documento ya existe, mostrar mensaje de error
                if resultado_documento[0] > 0:
                    return render_template('crear_cuenta.html', mensaje="El número de documento ya está registrado. Intenta con otro número de documento.")
                
                # Si el correo ya está registrado, mostrar mensaje de error
                if resultado_correo[0] > 0:
                    return render_template('crear_cuenta.html', mensaje="El correo electrónico ya está registrado. Intenta con otro correo.")
                
                # Si el número de teléfono ya está registrado, mostrar mensaje de error
                if resultado_telefono[0] > 0:
                    return render_template('crear_cuenta.html', mensaje="El número de teléfono ya está registrado. Intenta con otro número.")

                # Si la cuenta, número de documento, correo y número de teléfono no existen, insertar los nuevos datos con la contraseña hasheada
                query = """
                    INSERT INTO cuentas (numero_cuenta, contrasena, saldo_inicial, nombre_usuario, correo, edad, tipo_documento, numero_telefono, numero_documento)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                valores = (numero_cuenta, contrasena_hash, saldo_inicial, nombre_usuario, correo, edad, tipo_documento, numero_telefono, numero_documento)
                cursor.execute(query, valores)
                conexion.commit()

                return render_template('crear_cuenta.html', mensaje="Cuenta creada exitosamente.")

            except mysql.connector.Error as err:
                return render_template('crear_cuenta.html', mensaje="Error al crear la cuenta.")
            finally:
                cursor.close()
                conexion.close()
        else:
            return render_template('crear_cuenta.html', mensaje="No se pudo conectar a la base de datos.")
    
    return render_template('crear_cuenta.html')

# Ruta para iniciar sesión
@app.route('/iniciar_sesion', methods=['GET', 'POST'])
def iniciar_sesion():
    if request.method == 'POST':
        numero_cuenta = request.form['numero_cuenta']
        contrasena = request.form['contrasena']

        # Crear conexión con la base de datos
        conexion = crear_conexion()
        if conexion:
            try:
                cursor = conexion.cursor()
                # Consultar la base de datos para obtener el hash de la contraseña
                query = "SELECT contrasena, saldo_inicial, nombre_usuario, correo, edad, tipo_documento, numero_telefono, numero_documento FROM cuentas WHERE numero_cuenta = %s"
                cursor.execute(query, (numero_cuenta,))
                cuenta = cursor.fetchone()

                if cuenta and bcrypt.checkpw(contrasena.encode('utf-8'), cuenta[0].encode('utf-8')):  # Comparar el hash
                    # Guardar la cuenta completa en la sesión
                    session['numero_cuenta'] = numero_cuenta
                    session['nombre_usuario'] = cuenta[2]
                    session['saldo_inicial'] = cuenta[1]
                    session['correo'] = cuenta[3]
                    session['edad'] = cuenta[4]
                    session['tipo_documento'] = cuenta[5]
                    session['numero_telefono'] = cuenta[6]
                    session['numero_documento'] = cuenta[7]

                    print(f"Sesión iniciada para: {numero_cuenta}")  # Mensaje de depuración
                    return redirect(url_for('bienvenida'))  # Redirige a la página de bienvenida
                else:
                    return render_template('iniciar_sesion.html', mensaje="Autenticación fallida.")
            except mysql.connector.Error as err:
                return render_template('iniciar_sesion.html', mensaje="Error al iniciar sesión.")
            finally:
                cursor.close()
                conexion.close()
        else:
            return render_template('iniciar_sesion.html', mensaje="No se pudo conectar a la base de datos.")
    
    return render_template('iniciar_sesion.html')


# Ruta para consultar saldo
@app.route('/consultar_saldo')
def consultar_saldo():
    if 'numero_cuenta' not in session:
        return redirect(url_for('home'))  # Si no está logueado, redirigir a inicio de sesión
    
    numero_cuenta = session['numero_cuenta']
    
    # Obtener saldo desde la base de datos
    conexion = crear_conexion()
    if conexion:
        cursor = conexion.cursor()
        query = "SELECT saldo_inicial FROM cuentas WHERE numero_cuenta = %s"
        cursor.execute(query, (numero_cuenta,))
        saldo = cursor.fetchone()
        cursor.close()
        conexion.close()

        if saldo:
            return render_template('consultar_saldo.html', saldo=saldo[0])  # Mostrar saldo
        else:
            return render_template('consultar_saldo.html', mensaje="Cuenta no encontrada.")
    
    return render_template('consultar_saldo.html', mensaje="Error al consultar el saldo.")

# Ruta para retirar dinero
# Ruta para retirar dinero
@app.route('/retirar', methods=['GET', 'POST'])
def retirar():
    if 'numero_cuenta' not in session:
        return redirect(url_for('home'))  # Si no está logueado, redirigir a inicio de sesión
    
    numero_cuenta = session['numero_cuenta']
    
    # Crear conexión con la base de datos
    conexion = crear_conexion()
    if conexion:
        try:
            cursor = conexion.cursor()
            # Obtener los datos de la cuenta desde la base de datos
            query = "SELECT saldo_inicial FROM cuentas WHERE numero_cuenta = %s"
            cursor.execute(query, (numero_cuenta,))
            saldo = cursor.fetchone()
            
            if saldo:
                saldo_actual = Decimal(saldo[0])  # Convertir saldo a Decimal
                
                if request.method == 'POST':
                    monto = Decimal(request.form['monto'])
                    
                    # Verificar si el monto es menor o igual al saldo disponible
                    if monto <= saldo_actual:
                        # Realizar el retiro
                        nuevo_saldo = saldo_actual - monto
                        
                        # Actualizar el saldo en la base de datos
                        query_update = "UPDATE cuentas SET saldo_inicial = %s WHERE numero_cuenta = %s"
                        cursor.execute(query_update, (nuevo_saldo, numero_cuenta))
                        conexion.commit()

                        # Registrar la transacción en la base de datos
                        query_transaccion = """
                            INSERT INTO transacciones (numero_cuenta, tipo, monto, fecha)
                            VALUES (%s, 'retiro', %s, %s)
                        """
                        fecha = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        cursor.execute(query_transaccion, (numero_cuenta, monto, fecha))
                        conexion.commit()

                        return render_template('retirar.html', mensaje="Retiro realizado con éxito.", saldo=nuevo_saldo)
                    else:
                        return render_template('retirar.html', mensaje="Saldo insuficiente.", saldo=saldo_actual)
                else:
                    return render_template('retirar.html', saldo=saldo_actual)
            else:
                return render_template('retirar.html', mensaje="Cuenta no encontrada.")
        
        except mysql.connector.Error as err:
            return render_template('retirar.html', mensaje="Retiro exitoso.")
        
        finally:
            cursor.close()
            conexion.close()
    
    return render_template('retirar.html', mensaje="No se pudo conectar a la base de datos.")


# Ruta para consultar puntos ViveColombia
@app.route('/consultar_puntos')
def consultar_puntos():
    if 'numero_cuenta' not in session:
        return redirect(url_for('home'))  # Redirige si no está autenticado

    numero_cuenta = session['numero_cuenta']
    
    # Crear conexión a la base de datos
    conexion = crear_conexion()
    if conexion:
        try:
            cursor = conexion.cursor()
            query = """
                SELECT puntos
                FROM cuentas
                WHERE numero_cuenta = %s
            """
            cursor.execute(query, (numero_cuenta,))
            cuenta = cursor.fetchone()

            if cuenta:
                puntos_vivecolombia = cuenta[0]  # Obtener los puntos
                return render_template('consultar_puntos.html', puntos=puntos_vivecolombia)
            else:
                return render_template('home.html', mensaje="No se encontró la cuenta.")
        except mysql.connector.Error as err:
            print(f"Error al recuperar los puntos: {err}")
            return render_template('home.html', mensaje="Error al recuperar los puntos.")
        finally:
            cursor.close()
            conexion.close()

    return redirect(url_for('home'))

@app.route('/transferir', methods=['GET', 'POST'])
def transferir():
    if 'numero_cuenta' not in session:
        return redirect(url_for('home'))  # Si no está logueado, redirigir a inicio de sesión
    
    numero_cuenta = session['numero_cuenta']
    
    if request.method == 'POST':
        # Obtener los datos del formulario de transferencia
        numero_cuenta_destino = request.form['numero_cuenta_destino']
        monto = Decimal(request.form['monto'])
        
        # Crear conexión a la base de datos
        conexion = crear_conexion()
        if conexion:
            cursor = conexion.cursor()
            # Verificar si la cuenta destino existe
            query_destino = "SELECT saldo_inicial FROM cuentas WHERE numero_cuenta = %s"
            cursor.execute(query_destino, (numero_cuenta_destino,))
            cuenta_destino = cursor.fetchone()

            if cuenta_destino:
                # Actualizar el saldo de la cuenta origen (retiro)
                query_retirar = "UPDATE cuentas SET saldo_inicial = saldo_inicial - %s WHERE numero_cuenta = %s"
                cursor.execute(query_retirar, (monto, numero_cuenta))

                # Actualizar el saldo de la cuenta destino (ingreso)
                query_ingresar = "UPDATE cuentas SET saldo_inicial = saldo_inicial + %s WHERE numero_cuenta = %s"
                cursor.execute(query_ingresar, (monto, numero_cuenta_destino))

                # Obtener los saldos finales de ambas cuentas
                cursor.execute("SELECT saldo_inicial FROM cuentas WHERE numero_cuenta = %s", (numero_cuenta,))
                saldo_final_emisor = cursor.fetchone()[0]

                cursor.execute("SELECT saldo_inicial FROM cuentas WHERE numero_cuenta = %s", (numero_cuenta_destino,))
                saldo_final_receptor = cursor.fetchone()[0]

                # Registrar la transacción en la tabla de transacciones
                fecha_transaccion = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                query_insert_transaccion = """
                    INSERT INTO transacciones (tipo_transaccion, fecha, cuenta_origen, cuenta_destino, monto, saldo_final_emisor, saldo_final_receptor)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(query_insert_transaccion, (
                    'retiro',  # tipo de transacción para la cuenta origen
                    fecha_transaccion,
                    numero_cuenta,  # cuenta origen
                    numero_cuenta_destino,  # cuenta destino
                    monto,  # monto transferido
                    saldo_final_emisor,  # saldo final de la cuenta emisor
                    saldo_final_receptor  # saldo final de la cuenta receptor
                ))

                # Insertar un 'ingreso' en la cuenta destino
                cursor.execute(query_insert_transaccion, (
                    'ingreso',  # tipo de transacción para la cuenta destino
                    fecha_transaccion,
                    numero_cuenta_destino,  # cuenta origen (es la cuenta destino)
                    numero_cuenta,  # cuenta destino (es la cuenta origen)
                    monto,  # monto transferido
                    saldo_final_emisor,  # saldo final de la cuenta emisor
                    saldo_final_receptor  # saldo final de la cuenta receptor
                ))

                conexion.commit()
                cursor.close()
                conexion.close()

                return render_template('transferir.html', mensaje="Transferencia realizada con éxito.")
            else:
                cursor.close()
                conexion.close()
                return render_template('transferir.html', mensaje="Cuenta destino no encontrada.")
    
    # Si es un GET, mostrar el formulario de transferencia
    return render_template('transferir.html')


# Ruta para ver el historial de transacciones
@app.route('/historial_transacciones')
def historial_transacciones():
    if 'numero_cuenta' not in session:
        return redirect(url_for('home'))  # Redirige si no está autenticado

    numero_cuenta = session['numero_cuenta']

    conexion = crear_conexion()
    if conexion:
        try:
            cursor = conexion.cursor()
            query = """
                SELECT tipo_transaccion, fecha, cuenta_origen, cuenta_destino, monto, saldo_final_emisor, saldo_final_receptor
                FROM transacciones 
                WHERE cuenta_origen = %s OR cuenta_destino = %s
                ORDER BY fecha DESC
            """
            cursor.execute(query, (numero_cuenta, numero_cuenta))
            transacciones = cursor.fetchall()

            # Si no hay transacciones, se puede agregar un mensaje o manejarlo adecuadamente
            if not transacciones:
                return render_template('historial_transacciones.html', mensaje="No hay transacciones registradas.")

            # Convertir las transacciones en un diccionario para facilitar el acceso
            historial = [
                {
                    'tipo': trans[0],
                    'fecha': trans[1],
                    'cuenta_origen': trans[2],
                    'cuenta_destino': trans[3],
                    'monto': trans[4],
                    'saldo_final_emisor': trans[5],
                    'saldo_final_receptor': trans[6] if trans[6] is not None else 'N/A'  # Maneja valores None
                }
                for trans in transacciones
            ]

            return render_template('historial_transacciones.html', historial=historial)
        except mysql.connector.Error as err:
            print(f"Error al recuperar el historial: {err}")
            return render_template('home.html', mensaje="Error al recuperar el historial.")
        finally:
            cursor.close()
            conexion.close()

    return redirect(url_for('home'))

@app.route('/canjear_puntos', methods=['GET', 'POST'])
def canjear_puntos():
    if 'numero_cuenta' not in session:
        return redirect(url_for('home'))  # Si no está autenticado, redirigir a inicio de sesión
    
    numero_cuenta = session['numero_cuenta']
    
    # Lógica para el canje de puntos
    if request.method == 'POST':
        puntos_a_canjear = int(request.form['puntos'])  # Suponiendo que el formulario tiene un campo "puntos"
        
        # Obtener cuenta desde la base de datos
        conexion = crear_conexion()
        if conexion:
            cursor = conexion.cursor()
            try:
                query = "SELECT puntos FROM cuentas WHERE numero_cuenta = %s"
                cursor.execute(query, (numero_cuenta,))
                cuenta = cursor.fetchone()
                
                if cuenta:
                    puntos_disponibles = cuenta[0]
                    if puntos_a_canjear <= puntos_disponibles:
                        # Actualizar la cantidad de puntos en la base de datos
                        query_update = "UPDATE cuentas SET puntos = puntos - %s WHERE numero_cuenta = %s"
                        cursor.execute(query_update, (puntos_a_canjear, numero_cuenta))
                        conexion.commit()
                        
                        # Retornar un mensaje de éxito
                        return render_template('canjear_puntos.html', mensaje=f"Has canjeado {puntos_a_canjear} puntos.", puntos_disponibles=puntos_disponibles)
                    else:
                        # Si no tiene suficientes puntos
                        return render_template('canjear_puntos.html', mensaje="No tienes suficientes puntos para canjear.", puntos_disponibles=puntos_disponibles)
                else:
                    return render_template('canjear_puntos.html', mensaje="Cuenta no encontrada.")
            except Exception as e:
                return render_template('canjear_puntos.html', mensaje=f"Error al procesar la solicitud: {str(e)}")
            finally:
                cursor.close()  # Asegurarse de cerrar el cursor
                conexion.close()  # Asegurarse de cerrar la conexión

    # Si es un GET, simplemente mostrar el formulario para canjear puntos
    conexion = crear_conexion()
    if conexion:
        cursor = conexion.cursor()
        try:
            query = "SELECT puntos FROM cuentas WHERE numero_cuenta = %s"
            cursor.execute(query, (numero_cuenta,))
            cuenta = cursor.fetchone()
            
            if cuenta:
                puntos_disponibles = cuenta[0]
                return render_template('canjear_puntos.html', puntos_disponibles=puntos_disponibles)
            else:
                return render_template('canjear_puntos.html', mensaje="Cuenta no encontrada.")
        finally:
            cursor.close()  # Cerrar el cursor después de la consulta
            conexion.close()  # Cerrar la conexión a la base de datos

    return render_template('canjear_puntos.html', mensaje="Error al obtener los puntos.")


# Ruta para ingresar dinero
@app.route('/ingresar', methods=['GET', 'POST'])
def ingresar():
    if 'numero_cuenta' not in session:
        return redirect(url_for('home'))  # Si no está logueado, redirigir a inicio de sesión
    
    numero_cuenta = session['numero_cuenta']
    
    # Crear conexión con la base de datos
    conexion = crear_conexion()
    if conexion:
        try:
            cursor = conexion.cursor()
            # Obtener los datos de la cuenta desde la base de datos
            query = "SELECT saldo_inicial FROM cuentas WHERE numero_cuenta = %s"
            cursor.execute(query, (numero_cuenta,))
            saldo = cursor.fetchone()
            
            if saldo:
                saldo_actual = Decimal(saldo[0])  # Convertir saldo a Decimal
                print(f"Saldo actual de la cuenta {numero_cuenta}: {saldo_actual}")
                
                if request.method == 'POST':
                    monto = Decimal(request.form['monto'])
                    print(f"Monto recibido para ingresar: {monto}")
                    
                    if monto > 0:
                        # Realizar el ingreso
                        nuevo_saldo = saldo_actual + monto
                        
                        # Actualizar el saldo en la base de datos
                        query_update = "UPDATE cuentas SET saldo_inicial = %s WHERE numero_cuenta = %s"
                        cursor.execute(query_update, (nuevo_saldo, numero_cuenta))
                        conexion.commit()
                        print(f"Saldo actualizado a {nuevo_saldo} para la cuenta {numero_cuenta}")
                        
                        # Registrar la transacción en la base de datos
                        query_transaccion = """
                            INSERT INTO transacciones (tipo_transaccion, fecha, cuenta_origen, cuenta_destino, monto, saldo_final_emisor, saldo_final_receptor)
                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """
                        fecha = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        cursor.execute(query_transaccion, (
                            'ingreso',  # tipo de transacción
                            fecha,  # fecha y hora de la transacción
                            numero_cuenta,  # cuenta origen (es la misma cuenta para ingreso)
                            numero_cuenta,  # cuenta destino (es la misma cuenta para ingreso)
                            monto,  # monto transferido
                            nuevo_saldo,  # saldo final de la cuenta emisor (que es la misma cuenta)
                            nuevo_saldo  # saldo final de la cuenta receptor (que es la misma cuenta)
                        ))
                        conexion.commit()

                        return render_template('ingresar.html', mensaje="Ingreso realizado con éxito.", saldo=nuevo_saldo)
                    else:
                        return render_template('ingresar.html', mensaje="El monto debe ser mayor que cero.", saldo=saldo_actual)
                else:
                    return render_template('ingresar.html', saldo=saldo_actual)
            else:
                return render_template('ingresar.html', mensaje="Cuenta no encontrada.")
        
        except mysql.connector.Error as err:
            # Mostrar detalles del error
            print(f"Error de MySQL: {err}")
            return render_template('ingresar.html', mensaje=f"Error al procesar el ingreso: {err}")
        
        finally:
            cursor.close()
            conexion.close()
    
    return render_template('ingresar.html', mensaje="No se pudo conectar a la base de datos.")


# Ruta para cerrar sesión
@app.route('/cerrar_sesion', methods=['POST'])
def cerrar_sesion():
    session.pop('numero_cuenta', None)  # Elimina el número de cuenta de la sesión
    return redirect(url_for('home'))  # Redirige a la página de inicio (home)

# Ruta para transferir dinero


if __name__ == '__main__':
    app.run(debug=True)
