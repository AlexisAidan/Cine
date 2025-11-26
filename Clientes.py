from PyQt6.QtWidgets import (
    QMessageBox, QWidget, QVBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QDialog, QLineEdit, QFormLayout, QHBoxLayout
)
from PyQt6.QtCore import Qt
from OracleDB import OracleDB

# ---------- Dialogo para agregar/editar Cliente ----------
class ClienteDialog(QDialog):
    def __init__(self, db: OracleDB, cliente=None, parent=None):
        super().__init__(parent)
        self.db = db
        self.cliente = cliente
        self.setWindowTitle("Cliente" + (" - Editar" if cliente else " - Nuevo"))
        self.build_ui()

    def build_ui(self):
        layout = QFormLayout(self)
        self.nombre = QLineEdit()
        self.apellido = QLineEdit()
        self.correo = QLineEdit()
        self.telefono = QLineEdit()

        layout.addRow("Nombre:", self.nombre)
        layout.addRow("Apellido:", self.apellido)
        layout.addRow("Correo:", self.correo)
        layout.addRow("Teléfono:", self.telefono)

        btns = QHBoxLayout()
        save_btn = QPushButton("Guardar")
        save_btn.clicked.connect(self.save)
        cancel_btn = QPushButton("Cancelar")
        cancel_btn.clicked.connect(self.reject)
        btns.addWidget(save_btn)
        btns.addWidget(cancel_btn)
        layout.addRow(btns)

        if self.cliente:
            cid, nom, ape, corr, tel = self.cliente
            self.nombre.setText(str(nom or ""))
            self.apellido.setText(str(ape or ""))
            self.correo.setText(str(corr or ""))
            self.telefono.setText(str(tel or ""))

    def save(self):
        nom = self.nombre.text().strip()
        ape = self.apellido.text().strip()
        corr = self.correo.text().strip()
        if not nom or not ape or not corr:
            QMessageBox.warning(self, "Validación", "Nombre, apellido y correo son obligatorios.")
            return
        tel = self.telefono.text().strip() or None

        try:
            cur = self.db.cursor()
            if self.cliente:
                cid = self.cliente[0]
                cur.execute("""UPDATE Cliente SET nombre=:1, apellido=:2, correo=:3, telefono=:4
                              WHERE id_cliente=:5""", [nom, ape, corr, tel, cid])
            else:
                # Dejar que la BD asigne el ID mediante trigger
                cur.execute("""INSERT INTO Cliente (nombre, apellido, correo, telefono)
                              VALUES (:1,:2,:3,:4)""", [nom, ape, corr, tel])
            self.db.commit()
            self.accept()
        except Exception as e:
            self.db.rollback()
            QMessageBox.critical(self, "Error BD", f"Error al guardar:\n{e}")
        finally:
            cur.close()

# ---------- Widget de Clientes ----------
class ClientesWidget(QWidget):
    def __init__(self, db: OracleDB, parent=None):
        super().__init__(parent)
        self.db = db
        self.build_ui()
        self.load_data()

    def build_ui(self):
        layout = QVBoxLayout(self)
        btn_layout = QHBoxLayout()
        self.btn_add = QPushButton("Agregar")
        self.btn_edit = QPushButton("Editar")
        self.btn_delete = QPushButton("Eliminar")
        self.btn_refresh = QPushButton("Refrescar")
        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_edit)
        btn_layout.addWidget(self.btn_delete)
        btn_layout.addWidget(self.btn_refresh)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Nombre", "Apellido", "Correo", "Teléfono"])

        layout.addLayout(btn_layout)
        layout.addWidget(self.table)

        self.btn_add.clicked.connect(self.add_cliente)
        self.btn_edit.clicked.connect(self.edit_cliente)
        self.btn_delete.clicked.connect(self.delete_cliente)
        self.btn_refresh.clicked.connect(self.load_data)

    def load_data(self):
        try:
            cur = self.db.cursor()
            cur.execute("""SELECT id_cliente, nombre, apellido, correo, telefono
                          FROM Cliente ORDER BY id_cliente""")
            rows = cur.fetchall()
            cur.close()
        except Exception as e:
            QMessageBox.critical(self, "Error BD", f"No se pudieron cargar los clientes:\n{e}")
            return

        self.table.setRowCount(len(rows))
        for r, row in enumerate(rows):
            for c, val in enumerate(row):
                item = QTableWidgetItem(str(val) if val is not None else "")
                item.setFlags(item.flags() ^ Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(r, c, item)

    def selected_id(self):
        sel = self.table.currentRow()
        if sel < 0:
            return None
        item = self.table.item(sel, 0)
        return int(item.text()) if item else None

    def add_cliente(self):
        dlg = ClienteDialog(self.db, parent=self)
        if dlg.exec():
            self.load_data()

    def edit_cliente(self):
        cid = self.selected_id()
        if cid is None:
            QMessageBox.information(self, "Seleccionar", "Selecciona un cliente para editar.")
            return
        try:
            cur = self.db.cursor()
            cur.execute("""SELECT id_cliente, nombre, apellido, correo, telefono
                          FROM Cliente WHERE id_cliente = :1""", [cid])
            row = cur.fetchone()
            cur.close()
        except Exception as e:
            QMessageBox.critical(self, "Error BD", str(e))
            return
        if row:
            dlg = ClienteDialog(self.db, cliente=row, parent=self)
            if dlg.exec():
                self.load_data()

    def delete_cliente(self):
        cid = self.selected_id()
        if cid is None:
            QMessageBox.information(self, "Seleccionar", "Selecciona un cliente para eliminar.")
            return
        if QMessageBox.question(self, "Confirmar", f"¿Eliminar cliente ID {cid}?") != QMessageBox.StandardButton.Yes:
            return
        try:
            cur = self.db.cursor()
            cur.execute("DELETE FROM Cliente WHERE id_cliente = :1", [cid])
            self.db.commit()
            cur.close()
            self.load_data()
        except Exception as e:
            self.db.rollback()
            QMessageBox.critical(self, "Error BD", f"No se pudo eliminar:\n{e}")