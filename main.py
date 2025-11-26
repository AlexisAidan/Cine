import sys
import traceback
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QMessageBox
)
from PyQt6.QtGui import QAction
from OracleDB import OracleDB
from Boletos import VenderBoletoDialog, BoletosWidget
from Peliculas import PeliculasWidget
from Funciones import FuncionesWidget
from Salas import SalasWidget
from Butacas import ButacasWidget
from Clientes import ClientesWidget
from Empleados import EmpleadosWidget
from Pagos import PagosWidget


# ---------- MainWindow con Menú completo ----------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = OracleDB(user="cine", password="CinePass2024!", host="localhost", port=1521, service="FREEPDB1")
        self.setWindowTitle("Punto de Venta - Cine")
        self.resize(1000, 700)
        self.current_widget = None
        self.build_menus()
        self.statusBar().showMessage("Desconectado")

    def build_menus(self):
        menubar = self.menuBar()

        # Archivo
        archivo = menubar.addMenu("Archivo")
        action_connect = QAction("Conectar", self)
        action_disconnect = QAction("Desconectar", self)
        action_exit = QAction("Salir", self)
        archivo.addAction(action_connect)
        archivo.addAction(action_disconnect)
        archivo.addSeparator()
        archivo.addAction(action_exit)
        action_connect.triggered.connect(self.connect_db)
        action_disconnect.triggered.connect(self.disconnect_db)
        action_exit.triggered.connect(self.close)

        # Ventas
        ventas = menubar.addMenu("Ventas")
        action_vender = QAction("Vender boleto", self)
        action_ver_boletos = QAction("Ver boletos", self)
        ventas.addAction(action_vender)
        ventas.addAction(action_ver_boletos)
        action_vender.triggered.connect(self.vender_boletos)
        action_ver_boletos.triggered.connect(self.ver_boletos)

        # Catálogo
        catalogo = menubar.addMenu("Catálogo")
        action_peliculas = QAction("Películas", self)
        action_funciones = QAction("Funciones", self)
        action_salas = QAction("Salas", self)
        action_butacas = QAction("Butacas", self)
        catalogo.addAction(action_peliculas)
        catalogo.addAction(action_funciones)
        catalogo.addAction(action_salas)
        catalogo.addAction(action_butacas)
        action_peliculas.triggered.connect(self.open_peliculas)
        action_funciones.triggered.connect(self.open_funciones)
        action_salas.triggered.connect(self.open_salas)
        action_butacas.triggered.connect(self.open_butacas)

        # Clientes / Empleados / Pagos
        gestion = menubar.addMenu("Gestión")
        action_clientes = QAction("Clientes", self)
        action_empleados = QAction("Empleados", self)
        action_pagos = QAction("Pagos", self)
        gestion.addAction(action_clientes)
        gestion.addAction(action_empleados)
        gestion.addAction(action_pagos)
        action_clientes.triggered.connect(self.open_clientes)
        action_empleados.triggered.connect(self.open_empleados)
        action_pagos.triggered.connect(self.open_pagos)

        # Reportes
        reportes = menubar.addMenu("Reportes")
        action_ventas_dia = QAction("Ventas del día", self)
        reportes.addAction(action_ventas_dia)
        action_ventas_dia.triggered.connect(self.reporte_ventas_dia)

    # ---------- Acciones de menú ----------
    def connect_db(self):
        try:
            self.db.connect()
            self.statusBar().showMessage("Conectado a " + self.db.dsn)
            QMessageBox.information(self, "Conexión", "Conectado a la base de datos.")
        except Exception as e:
            QMessageBox.critical(self, "Error conexión", f"No se pudo conectar:\n{e}\n{traceback.format_exc()}")

    def disconnect_db(self):
        try:
            self.db.disconnect()
            self.statusBar().showMessage("Desconectado")
            QMessageBox.information(self, "Desconexión", "Desconectado.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def set_central_widget(self, widget):
        if self.current_widget:
            self.current_widget.setParent(None)
        self.current_widget = widget
        self.setCentralWidget(self.current_widget)

    # ---------- Funciones (Slots) ----------
    def open_peliculas(self):
        if not self.ensure_connected(): return
        w = PeliculasWidget(self.db, parent=self)
        self.set_central_widget(w)

    def open_funciones(self):
        if not self.ensure_connected(): return
        w = FuncionesWidget(self.db, parent=self)
        self.set_central_widget(w)

    def open_salas(self):
        if not self.ensure_connected(): return
        w = SalasWidget(self.db, parent=self)
        self.set_central_widget(w)

    def open_butacas(self):
        if not self.ensure_connected(): return
        w = ButacasWidget(self.db, parent=self)
        self.set_central_widget(w)

    def open_clientes(self):
        if not self.ensure_connected(): return
        w = ClientesWidget(self.db, parent=self)
        self.set_central_widget(w)

    def open_empleados(self):
        if not self.ensure_connected(): return
        w = EmpleadosWidget(self.db, parent=self)
        self.set_central_widget(w)

    def open_pagos(self):
        if not self.ensure_connected(): return
        w = PagosWidget(self.db, parent=self)
        self.set_central_widget(w)

    def ver_boletos(self):
        if not self.ensure_connected(): return
        w = BoletosWidget(self.db, parent=self)
        self.set_central_widget(w)

    def vender_boletos(self):
        if not self.ensure_connected(): return
        dlg = VenderBoletoDialog(self.db, parent=self)
        dlg.exec()

    def reporte_ventas_dia(self):
        if not self.ensure_connected(): return
        try:
            cur = self.db.cursor()
            hoy = datetime.now().date()
            cur.execute("""
                SELECT SUM(monto) FROM Pago
                WHERE TRUNC(fecha_pago) = :1
            """, [hoy])
            total = cur.fetchone()[0] or 0
            cur.close()
            QMessageBox.information(self, "Ventas del día", f"Total vendido hoy: {total:.2f}")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def ensure_connected(self):
        if not self.db.conn:
            QMessageBox.warning(self, "No conectado", "Conéctate a la base de datos primero (Archivo → Conectar).")
            return False
        return True

    def closeEvent(self, event):
        try:
            self.db.disconnect()
        except:
            pass
        super().closeEvent(event)

# ---------- Ejecutar la app ----------
def main():
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
