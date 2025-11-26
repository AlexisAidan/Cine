from datetime import datetime
from PyQt6.QtWidgets import (
    QMessageBox, QWidget, QVBoxLayout,
    QPushButton, QTableWidget, QTableWidgetItem, QHBoxLayout
)
from PyQt6.QtCore import Qt
from OracleDB import OracleDB

# ---------- Widget para ver pagos ----------
class PagosWidget(QWidget):
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
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID Pago", "Fecha", "Monto", "Método", "Cliente"])

        layout.addLayout(btn_layout)
        layout.addWidget(self.table)

        self.btn_refresh.clicked.connect(self.load_data)

    def load_data(self):
        try:
            cur = self.db.cursor()
            cur.execute("""
                SELECT
                    p.id_pago,
                    p.fecha_pago,
                    p.monto,
                    p.metodo_pago,
                    c.nombre || ' ' || c.apellido AS cliente
                FROM Pago p
                JOIN Cliente c ON p.id_cliente = c.id_cliente
                ORDER BY p.fecha_pago DESC
            """)
            rows = cur.fetchall()
            cur.close()
        except Exception as e:
            QMessageBox.critical(self, "Error BD", f"No se pudieron cargar los pagos:\n{e}")
            return

        self.table.setRowCount(len(rows))
        for r, row in enumerate(rows):
            for c, val in enumerate(row):
                item = QTableWidgetItem(str(val) if val is not None else "")
                item.setFlags(item.flags() ^ Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(r, c, item)

        self.table.resizeColumnsToContents()