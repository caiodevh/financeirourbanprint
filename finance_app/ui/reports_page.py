from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


class ReportsPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)

        filter_form = QFormLayout()
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate())
        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate())
        self.search_cliente = QLineEdit()
        self.filter_tipo = QComboBox()
        self.filter_tipo.addItems(["Todos", "Venda", "Gasto", "Custo Operacional"])

        filter_form.addRow("Data inicial", self.start_date)
        filter_form.addRow("Data final", self.end_date)
        filter_form.addRow("Buscar cliente", self.search_cliente)
        filter_form.addRow("Tipo", self.filter_tipo)

        actions = QHBoxLayout()
        self.apply_filter_btn = QPushButton("Aplicar Filtros")
        self.export_csv_btn = QPushButton("Exportar CSV")
        self.export_pdf_period_btn = QPushButton("PDF 7 dias")
        self.export_pdf_30_btn = QPushButton("PDF 30 dias")
        self.export_pdf_geral_btn = QPushButton("PDF Geral")
        self.backup_btn = QPushButton("Backup Banco")
        self.delete_btn = QPushButton("Apagar Selecionado")

        for btn in [
            self.apply_filter_btn,
            self.export_csv_btn,
            self.export_pdf_period_btn,
            self.export_pdf_30_btn,
            self.export_pdf_geral_btn,
            self.backup_btn,
            self.delete_btn,
        ]:
            actions.addWidget(btn)

        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["ID", "Data", "Tipo", "Categoria", "Descrição", "Valor"])
        self.table.horizontalHeader().setStretchLastSection(True)

        layout.addLayout(filter_form)
        layout.addLayout(actions)
        layout.addWidget(QLabel("Histórico Financeiro"))
        layout.addWidget(self.table)

    def update_table(self, data: list[dict]) -> None:
        self.table.setRowCount(0)
        tipo_filter = self.filter_tipo.currentText()
        for row in data:
            if tipo_filter != "Todos" and row["tipo"] != tipo_filter:
                continue
            idx = self.table.rowCount()
            self.table.insertRow(idx)
            values = [
                str(row["id"]),
                row["data"],
                row["tipo"],
                row["categoria"],
                row["descricao"],
                f"R$ {row['valor']:.2f}",
            ]
            for col, value in enumerate(values):
                item = QTableWidgetItem(value)
                if col == 5:
                    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.table.setItem(idx, col, item)

    def selected_record(self) -> tuple[str, int] | None:
        row = self.table.currentRow()
        if row < 0:
            return None
        record_id = int(self.table.item(row, 0).text())
        tipo = self.table.item(row, 2).text()
        map_table = {"Venda": "vendas", "Gasto": "gastos", "Custo Operacional": "custos_operacionais"}
        return map_table[tipo], record_id

    @staticmethod
    def confirm_delete() -> bool:
        result = QMessageBox.question(
            None,
            "Confirmação",
            "Deseja realmente apagar o registro selecionado?",
            QMessageBox.Yes | QMessageBox.No,
        )
        return result == QMessageBox.Yes
