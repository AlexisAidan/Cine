from datetime import datetime
from PyQt6.QtWidgets import (
    QMessageBox, QPushButton, QDialog, QLineEdit,
    QFormLayout, QHBoxLayout, QDateEdit, QSpinBox,
    QTableWidget, QTableWidgetItem, QWidget, QVBoxLayout,
)
from PyQt6.QtCore import QDate, Qt
from OracleDB import OracleDB

# ---------- Dialogo para agregar/editar Pelicula ----------
class PeliculaDialog(QDialog):
    def __init__(self, db: OracleDB, pelicula=None, parent=None):
        super().__init__(parent)
        self.db = db
        self.pelicula = pelicula  # None = nuevo
        self.setWindowTitle("Película" + (" - Editar" if pelicula else " - Nuevo"))
        self.build_ui()

    def build_ui(self):
        layout = QFormLayout(self)

        self.titulo = QLineEdit()
        self.sinopsis = QLineEdit()
        self.duracion = QSpinBox()
        self.duracion.setRange(1, 999)
        self.idioma = QLineEdit()
        self.clasificacion = QLineEdit()
        self.fecha_estreno = QDateEdit()
        self.fecha_estreno.setCalendarPopup(True)
        self.fecha_estreno.setDate(QDate.currentDate())

        layout.addRow("Título:", self.titulo)
        layout.addRow("Sinopsis:", self.sinopsis)
        layout.addRow("Duración (min):", self.duracion)
        layout.addRow("Idioma:", self.idioma)
        layout.addRow("Clasificación:", self.clasificacion)
        layout.addRow("Fecha estreno:", self.fecha_estreno)

        btns = QHBoxLayout()
        save_btn = QPushButton("Guardar")
        save_btn.clicked.connect(self.save)
        cancel_btn = QPushButton("Cancelar")
        cancel_btn.clicked.connect(self.reject)
        btns.addWidget(save_btn)
        btns.addWidget(cancel_btn)
        layout.addRow(btns)

        if self.pelicula:
            # pelicula is a tuple/dict with values - adapt depending on how caller provides it
            # Expecting: (id_pelicula, titulo, sinopsis, duracion_min, idioma, clasificacion, fecha_estreno)
            pid, t, s, d, idi, clas, fe = self.pelicula
            self.titulo.setText(str(t or ""))
            self.sinopsis.setText(str(s or ""))
            self.duracion.setValue(int(d or 1))
            self.idioma.setText(str(idi or ""))
            self.clasificacion.setText(str(clas or ""))
            # fecha_estreno puede venir como datetime.date o datetime
            try:
                # datetime.date
                y = getattr(fe, 'year', None)
                m = getattr(fe, 'month', None)
                d = getattr(fe, 'day', None)
                if y and m and d:
                    self.fecha_estreno.setDate(QDate(y, m, d))
            except Exception:
                pass

    def save(self):
        t = self.titulo.text().strip()
        if not t:
            QMessageBox.warning(self, "Validación", "El título es obligatorio.")
            return
        sinopsis = self.sinopsis.text().strip()
        dur = self.duracion.value()
        idioma = self.idioma.text().strip() or None
        clas = self.clasificacion.text().strip() or None
        # Convertir fecha a tipo Python con compatibilidad PyQt6
        cur = None
        try:
            qd = self.fecha_estreno.date()
            try:
                fe = qd.toPyDate()  # PyQt6
            except AttributeError:
                # Fallback por si no existe toPyDate
                fe = datetime(qd.year(), qd.month(), qd.day()).date()
            cur = self.db.cursor()
            if self.pelicula:
                pid = self.pelicula[0]
                # Usar binds posicionales para concordar con la lista de parámetros
                cur.execute("""
                    UPDATE Pelicula
                    SET titulo = :1,
                        sinopsis = :2,
                        duracion_min = :3,
                        idioma = :4,
                        clasificacion = :5,
                        fecha_estreno = :6
                    WHERE id_pelicula = :7
                """, [t, sinopsis, dur, idioma, clas, fe, pid])
            else:
                pid = self.db.nextval("seq_pelicula")
                cur.execute("""
                    INSERT INTO Pelicula
                    (id_pelicula, titulo, sinopsis, duracion_min, idioma, clasificacion, fecha_estreno)
                    VALUES (:1,:2,:3,:4,:5,:6,:7)
                """, [pid, t, sinopsis, dur, idioma, clas, fe])
            self.db.commit()
            self.accept()
        except Exception as e:
            if self.db.conn:
                self.db.rollback()
            QMessageBox.critical(self, "Error BD", f"Ocurrió un error al guardar:\n{e}")
        finally:
            if cur:
                cur.close()

# ---------- Widget principal de listado de peliculas ----------
class PeliculasWidget(QWidget):
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
        self.table.setHorizontalHeaderLabels(["ID", "Título", "Sinopsis", "Duración", "Idioma", "Clasif.", "Fecha estreno"])

        layout.addLayout(btn_layout)
        layout.addWidget(self.table)

        self.btn_add.clicked.connect(self.add_pelicula)
        self.btn_edit.clicked.connect(self.edit_pelicula)
        self.btn_delete.clicked.connect(self.delete_pelicula)
        self.btn_refresh.clicked.connect(self.load_data)

    def load_data(self):
        try:
            cur = self.db.cursor()
            cur.execute("""
                SELECT id_pelicula, titulo, sinopsis, duracion_min, idioma, clasificacion, fecha_estreno
                FROM Pelicula
                ORDER BY id_pelicula
            """)
            rows = cur.fetchall()
            cur.close()
        except Exception as e:
            QMessageBox.critical(self, "Error BD", f"No se pudieron cargar las películas:\n{e}")
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

    def add_pelicula(self):
        dlg = PeliculaDialog(self.db, parent=self)
        if dlg.exec():
            self.load_data()

    def edit_pelicula(self):
        pid = self.selected_id()
        if pid is None:
            QMessageBox.information(self, "Seleccionar", "Selecciona una película para editar.")
            return
        try:
            cur = self.db.cursor()
            cur.execute("""
                SELECT id_pelicula, titulo, sinopsis, duracion_min, idioma, clasificacion, fecha_estreno
                FROM Pelicula WHERE id_pelicula = :1
            """, [pid])
            row = cur.fetchone()
            cur.close()
        except Exception as e:
            QMessageBox.critical(self, "Error BD", str(e))
            return
        if row:
            dlg = PeliculaDialog(self.db, pelicula=row, parent=self)
            if dlg.exec():
                self.load_data()

    def delete_pelicula(self):
        pid = self.selected_id()
        if pid is None:
            QMessageBox.information(self, "Seleccionar", "Selecciona una película para eliminar.")
            return
        if QMessageBox.question(self, "Confirmar", f"Eliminar película ID {pid}?") != QMessageBox.StandardButton.Yes:
            return
        try:
            cur = self.db.cursor()
            cur.execute("DELETE FROM Pelicula WHERE id_pelicula = :1", [pid])
            self.db.commit()
            cur.close()
            self.load_data()
        except Exception as e:
            self.db.rollback()
            QMessageBox.critical(self, "Error BD", f"No se pudo eliminar:\n{e}")