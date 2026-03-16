from __future__ import annotations

from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)


class ExpensesPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        tabs = QTabWidget()
        tabs.addTab(self._create_expense_tab(), "Registrar Gastos")
        tabs.addTab(self._create_operational_tab(), "Custos Operacionais")
        layout.addWidget(tabs)

    def _create_expense_tab(self) -> QWidget:
        widget = QWidget()
        form = QFormLayout(widget)
        self.expense_data = QDateEdit()
        self.expense_data.setDate(QDate.currentDate())
        self.expense_data.setCalendarPopup(True)
        self.categoria = QComboBox()
        self.categoria.addItems(["material", "estampa", "embalagem", "transporte", "marketing", "equipamento", "outros"])
        self.expense_desc = QLineEdit()
        self.expense_valor = QLineEdit("0")

        form.addRow("Data", self.expense_data)
        form.addRow("Categoria", self.categoria)
        form.addRow("Descrição", self.expense_desc)
        form.addRow("Valor", self.expense_valor)

        actions = QHBoxLayout()
        self.save_expense_button = QPushButton("Salvar Gasto")
        actions.addWidget(self.save_expense_button)
        form.addRow(actions)
        return widget

    def _create_operational_tab(self) -> QWidget:
        widget = QWidget()
        form = QFormLayout(widget)
        self.op_data = QDateEdit()
        self.op_data.setDate(QDate.currentDate())
        self.op_data.setCalendarPopup(True)
        self.op_tipo = QComboBox()
        self.op_tipo.addItems(["aluguel", "internet", "energia", "ferramentas", "manutenção", "outros"])
        self.op_desc = QLineEdit()
        self.op_valor = QLineEdit("0")

        form.addRow("Data", self.op_data)
        form.addRow("Tipo", self.op_tipo)
        form.addRow("Descrição", self.op_desc)
        form.addRow("Valor", self.op_valor)

        actions = QHBoxLayout()
        self.save_op_button = QPushButton("Salvar Custo Operacional")
        actions.addWidget(self.save_op_button)
        form.addRow(actions)
        return widget

    def get_expense_payload(self) -> dict:
        return {
            "data": self.expense_data.date().toString("yyyy-MM-dd"),
            "categoria": self.categoria.currentText(),
            "descricao": self.expense_desc.text().strip(),
            "valor": float(self.expense_valor.text() or 0),
        }

    def get_operational_payload(self) -> dict:
        return {
            "data": self.op_data.date().toString("yyyy-MM-dd"),
            "tipo": self.op_tipo.currentText(),
            "descricao": self.op_desc.text().strip(),
            "valor": float(self.op_valor.text() or 0),
        }

    def clear_expense_form(self) -> None:
        self.expense_desc.clear()
        self.expense_valor.setText("0")

    def clear_op_form(self) -> None:
        self.op_desc.clear()
        self.op_valor.setText("0")
