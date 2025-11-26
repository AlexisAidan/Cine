from datetime import datetime, timezone
from PyQt6.QtWidgets import (
    QMessageBox, QWidget, QVBoxLayout,
    QPushButton, QTableWidget, QTableWidgetItem, QDialog, QLineEdit,
    QFormLayout, QHBoxLayout, QComboBox, QDoubleSpinBox,
    QListWidget, QListWidgetItem, QAbstractItemView
)
from PyQt6.QtCore import Qt
from OracleDB import OracleDB

# ---------- Dialog para vender boleto ----------
class VenderBoletoDialog(QDialog):
    def __init__(self, db: OracleDB, parent=None):
        super().__init__(parent)
        self.db = db
        self.setWindowTitle("Vender Boleto")
        self.setMinimumWidth(400)
        self.funcion_info = {}
        self.build_ui()
        self.cargar_combos()

    def build_ui(self):
        layout = QFormLayout(self)

        self.combo_cliente = QComboBox()
        self.combo_empleado = QComboBox()
        self.combo_funcion = QComboBox()

        # Permitir escribir/buscar en comboBox cliente, empleado, funcion
        self.combo_cliente.setEditable(True)
        self.combo_empleado.setEditable(True)
        self.combo_funcion.setEditable(True)

        # Campo de búsqueda de butacas
        self.buscar_butaca = QLineEdit()
        self.buscar_butaca.setPlaceholderText("Escribe para filtrar butacas...")

        # Lista de butacas con selección múltiple
        self.list_butacas = QListWidget()
        self.list_butacas.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)

        self.monto = QDoubleSpinBox()
        self.monto.setRange(0.00, 999999.99)
        self.monto.setDecimals(2)
        self.monto.setValue(0.00)
        self.monto.setReadOnly(True)

        self.metodo_pago = QComboBox()
        self.metodo_pago.addItems(["efectivo", "tarjeta_credito", "tarjeta_debito", "transferencia"])

        layout.addRow("Cliente:", self.combo_cliente)
        layout.addRow("Empleado:", self.combo_empleado)
        layout.addRow("Función:", self.combo_funcion)
        layout.addRow("Butacas:", self.buscar_butaca)
        layout.addRow("Disponibles:", self.list_butacas)
        layout.addRow("Monto:", self.monto)
        layout.addRow("Método de pago:", self.metodo_pago)

        btns = QHBoxLayout()
        vender_btn = QPushButton("Vender")
        vender_btn.clicked.connect(self.vender)
        cancel_btn = QPushButton("Cancelar")
        cancel_btn.clicked.connect(self.reject)
        btns.addWidget(vender_btn)
        btns.addWidget(cancel_btn)
        layout.addRow(btns)

    def cargar_combos(self):
        try:
            cur = self.db.cursor()

            # Cargar clientes
            cur.execute("SELECT id_cliente, nombre, apellido FROM Cliente ORDER BY nombre")
            clientes = cur.fetchall()
            for c in clientes:
                self.combo_cliente.addItem(f"{c[1]} {c[2]} (ID: {c[0]})", c[0])
            self.combo_cliente.setCurrentIndex(-1)

            # Cargar empleados
            cur.execute("SELECT id_empleado, nombre, apellido FROM Empleado ORDER BY nombre")
            empleados = cur.fetchall()
            for e in empleados:
                self.combo_empleado.addItem(f"{e[1]} {e[2]} (ID: {e[0]})", e[0])

            # Cargar funciones disponibles
            cur.execute("""
                SELECT f.id_funcion, p.titulo, f.hora_inicio, f.precio, f.id_sala
                FROM Funcion f
                JOIN Pelicula p ON f.id_pelicula = p.id_pelicula
                WHERE f.hora_inicio > SYSDATE
                ORDER BY f.hora_inicio
            """)
            funciones = cur.fetchall()
            self.funcion_info.clear()
            
            for f in funciones:
                fid, titulo, h_inicio, precio, id_sala = f
                
                fecha_str = ""
                if isinstance(h_inicio, datetime):
                    # Si no tiene zona horaria asumimos que es UTC
                    if h_inicio.tzinfo is None:
                        h_inicio = h_inicio.replace(tzinfo=timezone.utc)
                    # Convertir a zona horaria local y formatear
                    fecha_str = h_inicio.astimezone().strftime("%Y-%m-%d %H:%M")
                else:
                    fecha_str = str(h_inicio)

                self.combo_funcion.addItem(f"{titulo} - {fecha_str} (${precio})", fid)
                self.funcion_info[fid] = {"precio": float(precio), "id_sala": id_sala}

            # Cargar butacas según función seleccionada
            if self.combo_funcion.count() > 0:
                self.actualizar_butacas_y_monto()

            cur.close()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cargar datos:\n{e}")

        # Conectar cambios después de cargar
        self.combo_funcion.currentIndexChanged.connect(self.actualizar_butacas_y_monto)
        self.list_butacas.itemSelectionChanged.connect(self.actualizar_monto)
        self.buscar_butaca.textChanged.connect(self.filtrar_butacas)

    def actualizar_butacas_y_monto(self):
        # Cargar butacas disponibles para la función seleccionada
        self.list_butacas.clear()
        if self.combo_funcion.count() == 0:
            self.monto.setValue(0.00)
            return
        id_funcion = self.combo_funcion.currentData()
        info = self.funcion_info.get(id_funcion)
        if not info:
            self.monto.setValue(0.00)
            return
        id_sala = info["id_sala"]
        try:
            cur = self.db.cursor()
            # Butacas de la sala que no estén vendidas para esta función
            cur.execute(
                """
                SELECT b.id_butaca, b.fila, b.numero_butaca, NVL(b.tipo_butaca, 'normal') AS tipo
                FROM Butaca b
                WHERE b.id_sala = :1
                  AND NOT EXISTS (
                    SELECT 1 FROM Boleto bo
                    WHERE bo.id_butaca = b.id_butaca AND bo.id_funcion = :2
                  )
                ORDER BY b.fila, b.numero_butaca
                """,
                [id_sala, id_funcion]
            )
            for bid, fila, num, tipo in cur:
                texto = f"Fila {fila} #{num} ({tipo})"
                item = QListWidgetItem(texto)
                item.setData(Qt.ItemDataRole.UserRole, bid)
                self.list_butacas.addItem(item)
            cur.close()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudieron cargar butacas:\n{e}")

        # actualizar monto por si había selección previa
        self.actualizar_monto()
        # limpiar filtro
        self.buscar_butaca.clear()

    def filtrar_butacas(self):
        filtro = self.buscar_butaca.text().strip().lower()
        for i in range(self.list_butacas.count()):
            it = self.list_butacas.item(i)
            texto = it.data(Qt.ItemDataRole.DisplayRole)
            it.setHidden(filtro not in texto.lower())

    def actualizar_monto(self):
        if self.combo_funcion.count() == 0:
            self.monto.setValue(0.00)
            return
        id_funcion = self.combo_funcion.currentData()
        info = self.funcion_info.get(id_funcion)
        if not info:
            self.monto.setValue(0.00)
            return
        precio = info["precio"]
        cantidad = len(self.list_butacas.selectedItems())
        total = precio * cantidad
        self.monto.setValue(float(total))

    def vender(self):
        if self.combo_empleado.count() == 0:
            QMessageBox.warning(self, "Error", "No hay empleados registrados.")
            return
        if self.combo_funcion.count() == 0:
            QMessageBox.warning(self, "Error", "No hay funciones disponibles.")
            return
        if self.list_butacas.count() == 0:
            QMessageBox.warning(self, "Error", "No hay butacas disponibles para la función seleccionada.")
            return

        cliente_id = self.combo_cliente.currentData()
        if self.combo_cliente.currentIndex() == -1:
             cliente_id = self.get_usuario_generico()
             if not cliente_id:
                 return
        empleado_id = self.combo_empleado.currentData()
        id_funcion = self.combo_funcion.currentData()
        seleccion = self.list_butacas.selectedItems()
        if not seleccion:
            QMessageBox.warning(self, "Selecciona butacas", "Elige al menos una butaca.")
            return
        butaca_ids = [it.data(Qt.ItemDataRole.UserRole) for it in seleccion]
        monto = self.monto.value()
        metodo = self.metodo_pago.currentText()

        try:
            cur = self.db.cursor()
            fecha = datetime.now()

            # Verificar disponibilidad de cada butaca seleccionada (prevención)
            for bid in butaca_ids:
                cur.execute(
                    """
                    SELECT COUNT(*) FROM Boleto
                    WHERE id_funcion = :1 AND id_butaca = :2
                    """,
                    [id_funcion, bid]
                )
                count = cur.fetchone()[0]
                if count and int(count) > 0:
                    QMessageBox.warning(self, "Error", f"La butaca seleccionada (ID {bid}) ya fue vendida. Actualiza la lista e inténtalo de nuevo.")
                    cur.close()
                    return

            # Crear pago
            pago_id = self.db.nextval("seq_pago")
            cur.execute("""
                INSERT INTO Pago (id_pago, fecha_pago, monto, metodo_pago, id_cliente)
                VALUES (:1,:2,:3,:4,:5)
            """, [pago_id, fecha, monto, metodo, cliente_id])

            # Crear un boleto por cada butaca
            created_ids = []
            for bid in butaca_ids:
                boleto_id = self.db.nextval("seq_boleto")
                cur.execute(
                    """
                    INSERT INTO Boleto (id_boleto, id_butaca, id_funcion, id_empleado, id_pago, fecha_compra, precio_pagado)
                    VALUES (:1,:2,:3,:4,:5,:6,:7)
                    """,
                    [boleto_id, bid, id_funcion, empleado_id, pago_id, fecha, self.funcion_info[id_funcion]["precio"]]
                )
                created_ids.append(boleto_id)

            self.db.commit()
            cur.close()
            QMessageBox.information(self, "Éxito", f"Boletos vendidos: {len(created_ids)}\nID Pago: {pago_id}\nIDs Boletos: {', '.join(map(str, created_ids))}")
            self.accept()
        except Exception as e:
            self.db.rollback()
            QMessageBox.critical(self, "Error", f"No se pudo completar la venta:\n{e}")

    def get_usuario_generico(self):
        try:
            cur = self.db.cursor()
            # Buscar si ya existe
            cur.execute("SELECT id_cliente FROM Cliente WHERE nombre='Generico' AND apellido='Generico'")
            res = cur.fetchone()
            if res:
                cur.close()
                return res[0]
            
            # Si no existe, crearlo
            new_id = self.db.nextval("seq_cliente")
            cur.execute("""
                INSERT INTO Cliente (id_cliente, nombre, apellido, correo, telefono)
                VALUES (:1, 'Generico', 'Generico', 'generico@cine.com', NULL)
            """, [new_id])
            self.db.commit()
            cur.close()
            return new_id
        except Exception as e:
            self.db.rollback()
            QMessageBox.critical(self, "Error", f"No se pudo crear cliente genérico:\n{e}")
            return None

# ---------- Widget para ver boletos vendidos ----------
class BoletosWidget(QWidget):
    def __init__(self, db: OracleDB, parent=None):
        super().__init__(parent)
        self.db = db
        self.build_ui()
        self.load_data()

    def build_ui(self):
        layout = QVBoxLayout(self)

        btn_layout = QHBoxLayout()
        self.btn_refresh = QPushButton("Refrescar")
        btn_layout.addWidget(self.btn_refresh)
        btn_layout.addStretch()

        self.table = QTableWidget()
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels([
            "ID Boleto", "Fecha Compra", "Precio", "Película", "Función Inicio",
            "Sala", "Butaca", "Cliente", "Empleado", "ID Pago"
        ])

        layout.addLayout(btn_layout)
        layout.addWidget(self.table)

        self.btn_refresh.clicked.connect(self.load_data)

    def load_data(self):
        try:
            cur = self.db.cursor()
            cur.execute("""
                SELECT  b.id_boleto, b.fecha_compra, b.precio_pagado, p.titulo, f.hora_inicio, s.nombre,
                        bu.fila || '-' || bu.numero_butaca AS butaca,
                        c.nombre || ' ' || c.apellido AS cliente,
                        e.nombre || ' ' || e.apellido AS empleado, b.id_pago
                FROM Boleto b
                JOIN Funcion f ON b.id_funcion = f.id_funcion
                JOIN Pelicula p ON f.id_pelicula = p.id_pelicula
                JOIN Sala s ON f.id_sala = s.id_sala
                JOIN Butaca bu ON b.id_butaca = bu.id_butaca
                JOIN Pago pg ON b.id_pago = pg.id_pago
                JOIN Cliente c ON pg.id_cliente = c.id_cliente
                JOIN Empleado e ON b.id_empleado = e.id_empleado
                ORDER BY b.fecha_compra DESC
            """)
            rows = cur.fetchall()
            cur.close()
        except Exception as e:
            QMessageBox.critical(self, "Error BD", f"No se pudieron cargar los boletos:\n{e}")
            return

        self.table.setRowCount(len(rows))
        for r, row in enumerate(rows):
            for c, val in enumerate(row):
                item = QTableWidgetItem(str(val) if val is not None else "")
                item.setFlags(item.flags() ^ Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(r, c, item)

        self.table.resizeColumnsToContents()

