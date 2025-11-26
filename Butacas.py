from PyQt6.QtWidgets import (
    QMessageBox, QWidget, QVBoxLayout,
    QPushButton, QTableWidget, QTableWidgetItem, QDialog, QLineEdit,
    QFormLayout, QHBoxLayout, QSpinBox
)

from PyQt6.QtCore import Qt
from OracleDB import OracleDB

# ---------- Dialogo para agregar/editar Butaca ----------
class ButacaDialog(QDialog):
    def __init__(self, db: OracleDB, butaca=None, parent=None):
        super().__init__(parent)
        self.db = db
        self.butaca = butaca
        self.setWindowTitle("Butaca" + (" - Editar" if butaca else " - Nueva"))
        self.build_ui()

    def build_ui(self):
        layout = QFormLayout(self)
        self.fila = QLineEdit()
        self.numero = QSpinBox()
        self.numero.setRange(1, 999)
        self.tipo = QLineEdit()
        self.tipo.setPlaceholderText("Ej: normal, VIP, discapacitado")
        self.id_sala = QSpinBox()
        self.id_sala.setRange(1, 999999)

        layout.addRow("Fila:", self.fila)
        layout.addRow("Número:", self.numero)
        layout.addRow("Tipo:", self.tipo)
        layout.addRow("ID Sala:", self.id_sala)

        btns = QHBoxLayout()
        save_btn = QPushButton("Guardar")
        save_btn.clicked.connect(self.save)
        cancel_btn = QPushButton("Cancelar")
        cancel_btn.clicked.connect(self.reject)
        btns.addWidget(save_btn)
        btns.addWidget(cancel_btn)
        layout.addRow(btns)

        if self.butaca:
            bid, fila, num, tipo, sala = self.butaca
            self.fila.setText(str(fila or ""))
            self.numero.setValue(int(num or 1))
            self.tipo.setText(str(tipo or ""))
            self.id_sala.setValue(int(sala))

    def save(self):
        fila = self.fila.text().strip() or None
        num = self.numero.value()
        tipo = self.tipo.text().strip() or None
        sala = self.id_sala.value()

        try:
            cur = self.db.cursor()
            if self.butaca:
                bid = self.butaca[0]
                cur.execute("""UPDATE Butaca SET fila=:1, numero_butaca=:2, tipo_butaca=:3, id_sala=:4
                              WHERE id_butaca=:5""", [fila, num, tipo, sala, bid])
            else:
                bid = self.db.nextval("seq_butaca")
                cur.execute("""INSERT INTO Butaca (id_butaca, fila, numero_butaca, tipo_butaca, id_sala)
                              VALUES (:1,:2,:3,:4,:5)""", [bid, fila, num, tipo, sala])
            self.db.commit()
            self.accept()
        except Exception as e:
            self.db.rollback()
            QMessageBox.critical(self, "Error BD", f"Error al guardar:\n{e}")
        finally:
            cur.close()

# ---------- Widget de Butacas ----------
class ButacasWidget(QWidget):
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
        self.table.setHorizontalHeaderLabels(["ID", "Fila", "Número", "Tipo", "ID Sala"])

        layout.addLayout(btn_layout)
        layout.addWidget(self.table)

        self.btn_add.clicked.connect(self.add_butaca)
        self.btn_edit.clicked.connect(self.edit_butaca)
        self.btn_delete.clicked.connect(self.delete_butaca)
        self.btn_refresh.clicked.connect(self.load_data)

    def load_data(self):
        try:
            cur = self.db.cursor()
            cur.execute("""SELECT id_butaca, fila, numero_butaca, tipo_butaca, id_sala
                          FROM Butaca ORDER BY id_sala, fila, numero_butaca""")
            rows = cur.fetchall()
            cur.close()
        except Exception as e:
            QMessageBox.critical(self, "Error BD", f"No se pudieron cargar las butacas:\n{e}")
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

    def add_butaca(self):
        dlg = ButacaDialog(self.db, parent=self)
        if dlg.exec():
            self.load_data()

    def edit_butaca(self):
        bid = self.selected_id()
        if bid is None:
            QMessageBox.information(self, "Seleccionar", "Selecciona una butaca para editar.")
            return
        try:
            cur = self.db.cursor()
            cur.execute("""SELECT id_butaca, fila, numero_butaca, tipo_butaca, id_sala
                          FROM Butaca WHERE id_butaca = :1""", [bid])
            row = cur.fetchone()
            cur.close()
        except Exception as e:
            QMessageBox.critical(self, "Error BD", str(e))
            return
        if row:
            dlg = ButacaDialog(self.db, butaca=row, parent=self)
            if dlg.exec():
                self.load_data()

    def delete_butaca(self):
        bid = self.selected_id()
        if bid is None:
            QMessageBox.information(self, "Seleccionar", "Selecciona una butaca para eliminar.")
            return
        if QMessageBox.question(self, "Confirmar", f"¿Eliminar butaca ID {bid}?") != QMessageBox.StandardButton.Yes:
            return
        try:
            cur = self.db.cursor()
            cur.execute("DELETE FROM Butaca WHERE id_butaca = :1", [bid])
            self.db.commit()
            cur.close()
            self.load_data()
        except Exception as e:
            self.db.rollback()
            QMessageBox.critical(self, "Error BD", f"No se pudo eliminar:\n{e}")
