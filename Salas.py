from PyQt6.QtWidgets import (
    QMessageBox, QWidget, QVBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QHBoxLayout,
    QDialog, QLineEdit, QFormLayout
)
from OracleDB import OracleDB
from PyQt6.QtCore import Qt

# ---------- Dialogo para agregar/editar Sala ----------
class SalaDialog(QDialog):
    def __init__(self, db: OracleDB, sala=None, parent=None):
        super().__init__(parent)
        self.db = db
        self.sala = sala
        self.setWindowTitle("Sala" + (" - Editar" if sala else " - Nueva"))
        self.build_ui()

    def build_ui(self):
        layout = QFormLayout(self)
        self.nombre = QLineEdit()
        self.descripcion = QLineEdit()

        layout.addRow("Nombre:", self.nombre)
        layout.addRow("Descripción ubicación:", self.descripcion)

        btns = QHBoxLayout()
        save_btn = QPushButton("Guardar")
        save_btn.clicked.connect(self.save)
        cancel_btn = QPushButton("Cancelar")
        cancel_btn.clicked.connect(self.reject)
        btns.addWidget(save_btn)
        btns.addWidget(cancel_btn)
        layout.addRow(btns)

        if self.sala:
            sid, nom, desc = self.sala
            self.nombre.setText(str(nom or ""))
            self.descripcion.setText(str(desc or ""))

    def save(self):
        nom = self.nombre.text().strip()
        if not nom:
            QMessageBox.warning(self, "Validación", "El nombre es obligatorio.")
            return
        desc = self.descripcion.text().strip() or None

        try:
            cur = self.db.cursor()
            if self.sala:
                sid = self.sala[0]
                cur.execute("UPDATE Sala SET nombre = :1, descripcion_ubicacion = :2 WHERE id_sala = :3",
                           [nom, desc, sid])
            else:
                sid = self.db.nextval("seq_sala")
                cur.execute("INSERT INTO Sala (id_sala, nombre, descripcion_ubicacion) VALUES (:1,:2,:3)",
                           [sid, nom, desc])
            self.db.commit()
            self.accept()
        except Exception as e:
            self.db.rollback()
            QMessageBox.critical(self, "Error BD", f"Error al guardar:\n{e}")
        finally:
            cur.close()

# ---------- Widget de Salas ----------
class SalasWidget(QWidget):
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
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["ID", "Nombre", "Descripción"])

        layout.addLayout(btn_layout)
        layout.addWidget(self.table)

        self.btn_add.clicked.connect(self.add_sala)
        self.btn_edit.clicked.connect(self.edit_sala)
        self.btn_delete.clicked.connect(self.delete_sala)
        self.btn_refresh.clicked.connect(self.load_data)

    def load_data(self):
        try:
            cur = self.db.cursor()
            cur.execute("SELECT id_sala, nombre, descripcion_ubicacion FROM Sala ORDER BY id_sala")
            rows = cur.fetchall()
            cur.close()
        except Exception as e:
            QMessageBox.critical(self, "Error BD", f"No se pudieron cargar las salas:\n{e}")
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

    def add_sala(self):
        dlg = SalaDialog(self.db, parent=self)
        if dlg.exec():
            self.load_data()

    def edit_sala(self):
        sid = self.selected_id()
        if sid is None:
            QMessageBox.information(self, "Seleccionar", "Selecciona una sala para editar.")
            return
        try:
            cur = self.db.cursor()
            cur.execute("SELECT id_sala, nombre, descripcion_ubicacion FROM Sala WHERE id_sala = :1", [sid])
            row = cur.fetchone()
            cur.close()
        except Exception as e:
            QMessageBox.critical(self, "Error BD", str(e))
            return
        if row:
            dlg = SalaDialog(self.db, sala=row, parent=self)
            if dlg.exec():
                self.load_data()

    def delete_sala(self):
        sid = self.selected_id()
        if sid is None:
            QMessageBox.information(self, "Seleccionar", "Selecciona una sala para eliminar.")
            return
        if QMessageBox.question(self, "Confirmar", f"¿Eliminar sala ID {sid}?") != QMessageBox.StandardButton.Yes:
            return
        try:
            cur = self.db.cursor()
            cur.execute("DELETE FROM Sala WHERE id_sala = :1", [sid])
            self.db.commit()
            cur.close()
            self.load_data()
        except Exception as e:
            self.db.rollback()
            QMessageBox.critical(self, "Error BD", f"No se pudo eliminar:\n{e}")