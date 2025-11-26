import traceback
from datetime import datetime, timezone
from PyQt6.QtWidgets import (
    QMessageBox, QWidget, QVBoxLayout,
    QPushButton, QTableWidget, QTableWidgetItem, QDialog,
    QFormLayout, QHBoxLayout, QSpinBox, QDateTimeEdit, QDoubleSpinBox,
)
from PyQt6.QtCore import Qt, QDate, QDateTime, QTime
from OracleDB import OracleDB

# ---------- Dialogo para agregar/editar Funcion ----------
class FuncionDialog(QDialog):
    def __init__(self, db: OracleDB, funcion=None, parent=None):
        super().__init__(parent)
        self.db = db
        self.funcion = funcion
        self.setWindowTitle("Función" + (" - Editar" if funcion else " - Nueva"))
        self.build_ui()

    def build_ui(self):
        layout = QFormLayout(self)

        self.hora_inicio = QDateTimeEdit()
        self.hora_inicio.setCalendarPopup(True)
        self.hora_inicio.setDateTime(QDateTime.currentDateTime())

        self.hora_fin = QDateTimeEdit()
        self.hora_fin.setCalendarPopup(True)
        self.hora_fin.setDateTime(QDateTime.currentDateTime())

        self.precio = QDoubleSpinBox()
        self.precio.setRange(0.01, 9999.99)
        self.precio.setDecimals(2)
        self.precio.setValue(100.00)

        self.id_pelicula = QSpinBox()
        # QSpinBox usa int de 32 bits; evitar overflow (PyQt6 lanza OverflowError si el max es mayor a 2147483647)
        self.id_pelicula.setRange(1, 2147483647)

        self.id_sala = QSpinBox()
        self.id_sala.setRange(1, 999999)

        layout.addRow("Hora inicio:", self.hora_inicio)
        layout.addRow("Hora fin:", self.hora_fin)
        layout.addRow("Precio:", self.precio)
        layout.addRow("ID Película:", self.id_pelicula)
        layout.addRow("ID Sala:", self.id_sala)

        btns = QHBoxLayout()
        save_btn = QPushButton("Guardar")
        save_btn.clicked.connect(self.save)
        cancel_btn = QPushButton("Cancelar")
        cancel_btn.clicked.connect(self.reject)
        btns.addWidget(save_btn)
        btns.addWidget(cancel_btn)
        layout.addRow(btns)

        if self.funcion:
            fid, hinicio, hfin, prec, idpel, idsala = self.funcion
            # Asegurar que asignamos QDateTime al widget (no datetime de Python)
            try:
                if isinstance(hinicio, datetime):
                    qd = QDate(hinicio.year, hinicio.month, hinicio.day)
                    qt = QTime(hinicio.hour, hinicio.minute, hinicio.second)
                    self.hora_inicio.setDateTime(QDateTime(qd, qt))
            except Exception:
                pass
            try:
                if isinstance(hfin, datetime):
                    qd2 = QDate(hfin.year, hfin.month, hfin.day)
                    qt2 = QTime(hfin.hour, hfin.minute, hfin.second)
                    self.hora_fin.setDateTime(QDateTime(qd2, qt2))
            except Exception:
                pass
            self.precio.setValue(float(prec))
            self.id_pelicula.setValue(int(idpel))
            self.id_sala.setValue(int(idsala))

    def save(self):
        prec = self.precio.value()
        idpel = self.id_pelicula.value()
        idsala = self.id_sala.value()

        cur = None
        try:
            # Convertir a datetime Python con compatibilidad PyQt6
            try:
                hinicio = self.hora_inicio.dateTime().toPyDateTime()
            except AttributeError:
                dt1 = self.hora_inicio.dateTime()
                hinicio = datetime(dt1.date().year(), dt1.date().month(), dt1.date().day(), dt1.time().hour(), dt1.time().minute(), dt1.time().second())
            try:
                hfin = self.hora_fin.dateTime().toPyDateTime()
            except AttributeError:
                dt2 = self.hora_fin.dateTime()
                hfin = datetime(dt2.date().year(), dt2.date().month(), dt2.date().day(), dt2.time().hour(), dt2.time().minute(), dt2.time().second())

            if hinicio >= hfin:
                QMessageBox.warning(self, "Validación", "La hora de inicio debe ser antes de la hora de fin.")
                return
            cur = self.db.cursor()
            if self.funcion:
                fid = self.funcion[0]
                cur.execute("""UPDATE Funcion SET hora_inicio=:1, hora_fin=:2, precio=:3, id_pelicula=:4, id_sala=:5
                              WHERE id_funcion=:6""", [hinicio, hfin, prec, idpel, idsala, fid])
            else:
                fid = self.db.nextval("seq_funcion")
                cur.execute("""INSERT INTO Funcion (id_funcion, hora_inicio, hora_fin, precio, id_pelicula, id_sala)
                              VALUES (:1,:2,:3,:4,:5,:6)""", [fid, hinicio, hfin, prec, idpel, idsala])
            self.db.commit()
            self.accept()
        except Exception as e:
            self.db.rollback()
            QMessageBox.critical(self, "Error BD", f"Error al guardar:\n{e}")
        finally:
            if cur:
                try:
                    cur.close()
                except Exception:
                    pass

# ---------- Widget de Funciones ----------
class FuncionesWidget(QWidget):
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
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["ID", "Hora inicio", "Hora fin", "Precio", "ID Película", "ID Sala", "Título Película"])

        layout.addLayout(btn_layout)
        layout.addWidget(self.table)

        self.btn_add.clicked.connect(self.add_funcion)
        self.btn_edit.clicked.connect(self.edit_funcion)
        self.btn_delete.clicked.connect(self.delete_funcion)
        self.btn_refresh.clicked.connect(self.load_data)

    def load_data(self):
        try:
            cur = self.db.cursor()
            cur.execute("""
                SELECT f.id_funcion, f.hora_inicio, f.hora_fin, f.precio, f.id_pelicula, f.id_sala, p.titulo
                FROM Funcion f
                LEFT JOIN Pelicula p ON f.id_pelicula = p.id_pelicula
                ORDER BY f.hora_inicio DESC
            """)
            rows = cur.fetchall()
            cur.close()
        except Exception as e:
            QMessageBox.critical(self, "Error BD", f"No se pudieron cargar las funciones:\n{e}")
            return

        self.table.setRowCount(len(rows))
        for r, row in enumerate(rows):
            for c, val in enumerate(row):
                display_val = ""
                if val is not None:
                    if isinstance(val, datetime):
                        # Si no tiene zona horaria asumimos que es UTC
                        if val.tzinfo is None:
                            val = val.replace(tzinfo=timezone.utc)
                        # Convertir a zona horaria local y formatear
                        display_val = val.astimezone().strftime('%Y-%m-%d %H:%M')
                    else:
                        display_val = str(val)

                item = QTableWidgetItem(display_val)
                item.setFlags(item.flags() ^ Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(r, c, item)

    def selected_id(self):
        sel = self.table.currentRow()
        if sel < 0:
            return None
        item = self.table.item(sel, 0)
        return int(item.text()) if item else None

    def add_funcion(self):
        try:
            dlg = FuncionDialog(self.db, parent=self)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo abrir el diálogo de Función:\n{e}\n{traceback.format_exc()}")
            return
        if dlg.exec():
            self.load_data()

    def edit_funcion(self):
        fid = self.selected_id()
        if fid is None:
            QMessageBox.information(self, "Seleccionar", "Selecciona una función para editar.")
            return
        try:
            cur = self.db.cursor()
            cur.execute("""SELECT id_funcion, hora_inicio, hora_fin, precio, id_pelicula, id_sala
                          FROM Funcion WHERE id_funcion = :1""", [fid])
            row = cur.fetchone()
            cur.close()
        except Exception as e:
            QMessageBox.critical(self, "Error BD", str(e))
            return
        if row:
            try:
                dlg = FuncionDialog(self.db, funcion=row, parent=self)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo abrir el diálogo de edición:\n{e}\n{traceback.format_exc()}")
                return
            if dlg.exec():
                self.load_data()

    def delete_funcion(self):
        fid = self.selected_id()
        if fid is None:
            QMessageBox.information(self, "Seleccionar", "Selecciona una función para eliminar.")
            return
        if QMessageBox.question(self, "Confirmar", f"¿Eliminar función ID {fid}?") != QMessageBox.StandardButton.Yes:
            return
        try:
            cur = self.db.cursor()
            cur.execute("DELETE FROM Funcion WHERE id_funcion = :1", [fid])
            self.db.commit()
            cur.close()
            self.load_data()
        except Exception as e:
            self.db.rollback()
            QMessageBox.critical(self, "Error BD", f"No se pudo eliminar:\n{e}")