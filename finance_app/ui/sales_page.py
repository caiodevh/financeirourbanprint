from __future__ import annotations

from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class SalesPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)

        group = QGroupBox("Registrar Venda")
        form = QFormLayout(group)

        self.data = QDateEdit()
        self.data.setCalendarPopup(True)
        self.data.setDate(QDate.currentDate())
        self.cliente = QLineEdit()
        self.produto = QLineEdit()
        self.quantidade = QLineEdit("1")
        self.preco_unitario = QLineEdit("0")
        self.forma_pagamento = QComboBox()
        self.forma_pagamento.addItems(["Pix", "Dinheiro", "Cartão", "Boleto"])
        self.observacoes = QTextEdit()
        self.observacoes.setMaximumHeight(70)

        self.valor_total = QLabel("R$ 0,00")
        self.lucro = QLabel("R$ 0,00")

        form.addRow("Data", self.data)
        form.addRow("Cliente", self.cliente)
        form.addRow("Produto", self.produto)
        form.addRow("Quantidade", self.quantidade)
        form.addRow("Preço unitário", self.preco_unitario)
        form.addRow("Forma de pagamento", self.forma_pagamento)
        form.addRow("Observações", self.observacoes)
        form.addRow("Valor total", self.valor_total)
        form.addRow("Lucro bruto da venda", self.lucro)

        buttons = QHBoxLayout()
        self.calc_button = QPushButton("Calcular")
        self.save_button = QPushButton("Salvar Venda")
        buttons.addWidget(self.calc_button)
        buttons.addWidget(self.save_button)
        form.addRow(buttons)

        layout.addWidget(group)
        layout.addStretch()

    def get_payload(self) -> dict:
        return {
            "data": self.data.date().toString("yyyy-MM-dd"),
            "cliente": self.cliente.text().strip(),
            "produto": self.produto.text().strip(),
            "quantidade": int(self.quantidade.text() or 0),
            "preco_unitario": float(self.preco_unitario.text() or 0),
            "forma_pagamento": self.forma_pagamento.currentText(),
            "observacoes": self.observacoes.toPlainText().strip(),
        }

    def set_calculated(self, valor_total: float, lucro: float) -> None:
        self.valor_total.setText(f"R$ {valor_total:.2f}")
        color = "#1f9d55" if lucro >= 0 else "#d64545"
        self.lucro.setStyleSheet(f"font-weight: bold; color: {color};")
        self.lucro.setText(f"R$ {lucro:.2f}")

    def clear_form(self) -> None:
        self.cliente.clear()
        self.produto.clear()
        self.quantidade.setText("1")
        self.preco_unitario.setText("0")
        self.observacoes.clear()
        self.set_calculated(0, 0)
