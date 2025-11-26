from PyQt6.QtWidgets import (
    QMessageBox, QWidget, QVBoxLayout,
    QPushButton, QTableWidget, QTableWidgetItem, QDialog, QLineEdit,
    QFormLayout, QHBoxLayout
)
from PyQt6.QtCore import Qt
from OracleDB import OracleDB

# ---------- Dialogo para agregar/editar Empleado ----------
class EmpleadoDialog(QDialog):
    def __init__(self, db: OracleDB, empleado=None, parent=None):
        super().__init__(parent)
        self.db = db
        self.empleado = empleado
        self.setWindowTitle("Empleado" + (" - Editar" if empleado else " - Nuevo"))
        self.build_ui()

    def build_ui(self):
        layout = QFormLayout(self)
        self.usuario = QLineEdit()
        self.contrasena = QLineEdit()
        self.contrasena.setEchoMode(QLineEdit.EchoMode.Password)
        self.nombre = QLineEdit()
        self.apellido = QLineEdit()
        self.rol = QLineEdit()
        self.rol.setPlaceholderText("Ej: vendedor, gerente, admin")

        layout.addRow("Usuario:", self.usuario)
        layout.addRow("Contraseña:", self.contrasena)
        layout.addRow("Nombre:", self.nombre)
        layout.addRow("Apellido:", self.apellido)
        layout.addRow("Rol:", self.rol)

        btns = QHBoxLayout()
        save_btn = QPushButton("Guardar")
        save_btn.clicked.connect(self.save)
        cancel_btn = QPushButton("Cancelar")
        cancel_btn.clicked.connect(self.reject)
        btns.addWidget(save_btn)
        btns.addWidget(cancel_btn)
        layout.addRow(btns)

        if self.empleado:
            eid, usr, pwd, nom, ape, rol = self.empleado
            self.usuario.setText(str(usr or ""))
            self.nombre.setText(str(nom or ""))
            self.apellido.setText(str(ape or ""))
            self.rol.setText(str(rol or ""))
            # No mostramos la contraseña por seguridad

    def save(self):
        usr = self.usuario.text().strip()
        pwd = self.contrasena.text().strip()
        nom = self.nombre.text().strip()
        ape = self.apellido.text().strip()
        rol = self.rol.text().strip()

        if not usr or not nom or not ape or not rol:
            QMessageBox.warning(self, "Validación", "Usuario, nombre, apellido y rol son obligatorios.")
            return

        try:
            cur = self.db.cursor()
            if self.empleado:
                eid = self.empleado[0]
                if pwd:  # Solo actualizar contraseña si se proporciona una nueva
                    cur.execute("""UPDATE Empleado SET usuario=:1, contrasena=:2, nombre=:3, apellido=:4, rol=:5
                                  WHERE id_empleado=:6""", [usr, pwd, nom, ape, rol, eid])
                else:
                    cur.execute("""UPDATE Empleado SET usuario=:1, nombre=:2, apellido=:3, rol=:4
                                  WHERE id_empleado=:5""", [usr, nom, ape, rol, eid])
            else:
                if not pwd:
                    QMessageBox.warning(self, "Validación", "La contraseña es obligatoria para nuevos empleados.")
                    return
                eid = self.db.nextval("seq_empleado")
                cur.execute("""INSERT INTO Empleado (id_empleado, usuario, contrasena, nombre, apellido, rol)
                              VALUES (:1,:2,:3,:4,:5,:6)""", [eid, usr, pwd, nom, ape, rol])
            self.db.commit()
            self.accept()
        except Exception as e:
            self.db.rollback()
            QMessageBox.critical(self, "Error BD", f"Error al guardar:\n{e}")
        finally:
            cur.close()

# ---------- Widget de Empleados ----------
class EmpleadosWidget(QWidget):
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
        self.table.setHorizontalHeaderLabels(["ID", "Usuario", "Nombre", "Apellido", "Rol"])

        layout.addLayout(btn_layout)
        layout.addWidget(self.table)

        self.btn_add.clicked.connect(self.add_empleado)
        self.btn_edit.clicked.connect(self.edit_empleado)
        self.btn_delete.clicked.connect(self.delete_empleado)
        self.btn_refresh.clicked.connect(self.load_data)

    def load_data(self):
        try:
            cur = self.db.cursor()
            cur.execute("""SELECT id_empleado, usuario, contrasena, nombre, apellido, rol
                          FROM Empleado ORDER BY id_empleado""")
            rows = cur.fetchall()
            cur.close()
        except Exception as e:
            QMessageBox.critical(self, "Error BD", f"No se pudieron cargar los empleados:\n{e}")
            return

        self.table.setRowCount(len(rows))
        for r, row in enumerate(rows):
            # Mostrar solo ID, Usuario, Nombre, Apellido, Rol (sin contraseña)
            display_row = (row[0], row[1], row[3], row[4], row[5])
            for c, val in enumerate(display_row):
                item = QTableWidgetItem(str(val) if val is not None else "")
                item.setFlags(item.flags() ^ Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(r, c, item)

    def selected_id(self):
        sel = self.table.currentRow()
        if sel < 0:
            return None
        item = self.table.item(sel, 0)
        return int(item.text()) if item else None

    def add_empleado(self):
        dlg = EmpleadoDialog(self.db, parent=self)
        if dlg.exec():
            self.load_data()

    def edit_empleado(self):
        eid = self.selected_id()
        if eid is None:
            QMessageBox.information(self, "Seleccionar", "Selecciona un empleado para editar.")
            return
        try:
            cur = self.db.cursor()
            cur.execute("""SELECT id_empleado, usuario, contrasena, nombre, apellido, rol
                          FROM Empleado WHERE id_empleado = :1""", [eid])
            row = cur.fetchone()
            cur.close()
        except Exception as e:
            QMessageBox.critical(self, "Error BD", str(e))
            return
        if row:
            dlg = EmpleadoDialog(self.db, empleado=row, parent=self)
            if dlg.exec():
                self.load_data()

    def delete_empleado(self):
        eid = self.selected_id()
        if eid is None:
            QMessageBox.information(self, "Seleccionar", "Selecciona un empleado para eliminar.")
            return
        if QMessageBox.question(self, "Confirmar", f"¿Eliminar empleado ID {eid}?") != QMessageBox.StandardButton.Yes:
            return
        try:
            cur = self.db.cursor()
            cur.execute("DELETE FROM Empleado WHERE id_empleado = :1", [eid])
            self.db.commit()
            cur.close()
            self.load_data()
        except Exception as e:
            self.db.rollback()
            QMessageBox.critical(self, "Error BD", f"No se pudo eliminar:\n{e}")