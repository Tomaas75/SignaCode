import json
import os
from datetime import date

class Cuenta:
    def __init__(self, numero_cuenta, contrasena, saldo_inicial):
        self.numero_cuenta = numero_cuenta
        self.contrasena = contrasena
        self.saldo = saldo_inicial
        self.puntos_vive_colombia = 0
        self.retiros_diarios = 0
        self.ultima_fecha_retiro = date.today()

class Banco:
    file_path = 'cuentas.json'  # Ruta del archivo JSON
    tope_diario_retiros = 2000000  # Límite diario de retiros

    def __init__(self):
        self.cuentas = {}
        if os.path.exists(self.file_path):
            # Cargar datos desde el archivo JSON si existe
            with open(self.file_path, 'r') as file:
                self.cuentas = json.load(file)
        else:
            # Crear un nuevo diccionario si no existe el archivo
            self.cuentas = {}
            self.guardar_datos()

    def guardar_datos(self):
        # Guardar datos en el archivo JSON
        with open(self.file_path, 'w') as file:
            json.dump(self.cuentas, file, indent=4)

    def autenticar(self, numero_cuenta, contrasena):
        # Autenticar cuenta
        return numero_cuenta in self.cuentas and self.cuentas[numero_cuenta].contrasena == contrasena

    def crear_cuenta(self, numero_cuenta, contrasena, saldo_inicial):
        # Crear una nueva cuenta si no existe
        if numero_cuenta not in self.cuentas:
            self.cuentas[numero_cuenta] = Cuenta(numero_cuenta, contrasena, saldo_inicial)
            self.guardar_datos()
        else:
            raise Exception("La cuenta ya existe.")

    def consultar_saldo(self, numero_cuenta):
        # Consultar saldo de la cuenta
        return self.cuentas[numero_cuenta].saldo

    def retirar(self, numero_cuenta, monto):
        cuenta = self.cuentas[numero_cuenta]
        hoy = date.today()

        # Reiniciar los retiros diarios si es un nuevo día
        if cuenta.ultima_fecha_retiro < hoy:
            cuenta.retiros_diarios = 0
            cuenta.ultima_fecha_retiro = hoy

        # Verificar si el monto a retirar es permitido
        if cuenta.saldo >= monto and cuenta.retiros_diarios + monto <= self.tope_diario_retiros:
            cuenta.saldo -= monto
            cuenta.retiros_diarios += monto
            cuenta.puntos_vive_colombia += 100  # Asignar puntos ViveColombia
            self.guardar_datos()
            return f"Saldo actual: {cuenta.saldo}\nPuntos ViveColombia generados: 100\nPuntos ViveColombia actuales: {cuenta.puntos_vive_colombia}"
        else:
            raise Exception("Saldo insuficiente o monto supera el tope diario de retiros.")

    def transferir(self, cuenta_origen, cuenta_destino, monto):
        if cuenta_destino in self.cuentas:
            if self.cuentas[cuenta_origen].saldo >= monto:
                self.cuentas[cuenta_origen].saldo -= monto
                self.cuentas[cuenta_destino].saldo += monto
                self.cuentas[cuenta_origen].puntos_vive_colombia += 100  # Asignar puntos ViveColombia
                self.cuentas[cuenta_destino].puntos_vive_colombia += 100  # Asignar puntos ViveColombia
                self.guardar_datos()
                return (f"Saldo actual de cuenta origen: {self.cuentas[cuenta_origen].saldo}\n"
                        f"Puntos ViveColombia generados en cuenta origen: 100\n"
                        f"Puntos ViveColombia actuales en cuenta origen: {self.cuentas[cuenta_origen].puntos_vive_colombia}\n\n"
                        f"Saldo actual de cuenta destino: {self.cuentas[cuenta_destino].saldo}\n"
                        f"Puntos ViveColombia generados en cuenta destino: 100\n"
                        f"Puntos ViveColombia actuales en cuenta destino: {self.cuentas[cuenta_destino].puntos_vive_colombia}")
            else:
                raise Exception("Saldo insuficiente.")
        else:
            raise Exception("La cuenta destino no existe.")

    def consultar_puntos(self, numero_cuenta):
        # Consultar puntos ViveColombia
        return self.cuentas[numero_cuenta].puntos_vive_colombia

    def canjear_puntos(self, numero_cuenta, puntos):
        # Canjear puntos ViveColombia por saldo
        cuenta = self.cuentas[numero_cuenta]
        if cuenta.puntos_vive_colombia >= puntos:
            cuenta.puntos_vive_colombia -= puntos
            cuenta.saldo += puntos * 7  # Por cada punto, 7 unidades de saldo
            self.guardar_datos()
            return (f"Saldo actual: {cuenta.saldo}\n"
                    f"Puntos ViveColombia canjeados: {puntos}\n"
                    f"Puntos ViveColombia actuales: {cuenta.puntos_vive_colombia}")
        else:
            raise Exception("Puntos insuficientes.")
