from __future__ import annotations

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QGridLayout, QHBoxLayout, QLabel, QVBoxLayout, QWidget


class StatCard(QFrame):
    def __init__(self, title: str, value: str, color: str) -> None:
        super().__init__()
        self.setObjectName("statCard")
        self.setStyleSheet(f"QFrame#statCard {{ background-color: #f5f7fa; border: 1px solid #dfe4ea; border-radius: 8px;}}")
        layout = QVBoxLayout(self)
        self.title = QLabel(title)
        self.title.setStyleSheet("font-size: 12px; color: #4a5568;")
        self.value = QLabel(value)
        self.value.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {color};")
        layout.addWidget(self.title)
        layout.addWidget(self.value)

    def update_value(self, value: str, color: str) -> None:
        self.value.setText(value)
        self.value.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {color};")


class DashboardPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.layout = QVBoxLayout(self)

        cards_layout = QGridLayout()
        self.card_receita = StatCard("Receita total", "R$ 0,00", "#1f9d55")
        self.card_gastos = StatCard("Gastos totais", "R$ 0,00", "#d64545")
        self.card_lucro = StatCard("Lucro total", "R$ 0,00", "#1f9d55")
        self.card_lucro_liquido = StatCard("Lucro líquido", "R$ 0,00", "#f1c40f")
        self.card_margem = StatCard("Margem média", "0.00%", "#2b6cb0")

        cards = [
            self.card_receita,
            self.card_gastos,
            self.card_lucro,
            self.card_lucro_liquido,
            self.card_margem,
        ]
        for i, card in enumerate(cards):
            cards_layout.addWidget(card, i // 3, i % 3)

        self.layout.addLayout(cards_layout)

        charts_layout = QHBoxLayout()
        self.sales_chart = self._build_chart("Vendas por período")
        self.expenses_chart = self._build_chart("Gastos por categoria")
        self.profit_chart = self._build_chart("Lucro mensal")
        charts_layout.addWidget(self.sales_chart["canvas"])
        charts_layout.addWidget(self.expenses_chart["canvas"])
        charts_layout.addWidget(self.profit_chart["canvas"])
        self.layout.addLayout(charts_layout)
        self.layout.addStretch()

    def _build_chart(self, title: str):
        figure = Figure(figsize=(3.5, 2.5))
        canvas = FigureCanvas(figure)
        axis = figure.add_subplot(111)
        axis.set_title(title)
        axis.grid(True, alpha=0.3)
        figure.tight_layout()
        return {"figure": figure, "canvas": canvas, "axis": axis}

    def refresh(self, indicators: dict, monthly_sales: list[dict], expenses_by_category: list[dict]) -> None:
        lucro_color = "#1f9d55" if indicators["lucro_total"] >= 0 else "#d64545"
        liquido = indicators["lucro_liquido"]
        if liquido > 0:
            liquido_color = "#1f9d55"
        elif liquido < 0:
            liquido_color = "#d64545"
        else:
            liquido_color = "#f1c40f"

        self.card_receita.update_value(f"R$ {indicators['receita_total']:.2f}", "#1f9d55")
        self.card_gastos.update_value(f"R$ {indicators['gastos_totais'] + indicators['custos_operacionais']:.2f}", "#d64545")
        self.card_lucro.update_value(f"R$ {indicators['lucro_total']:.2f}", lucro_color)
        self.card_lucro_liquido.update_value(f"R$ {indicators['lucro_liquido']:.2f}", liquido_color)
        self.card_margem.update_value(f"{indicators['margem_media']:.2f}%", "#2b6cb0")

        self._draw_sales_chart(monthly_sales)
        self._draw_expense_chart(expenses_by_category)
        self._draw_profit_chart(monthly_sales)

    def _draw_sales_chart(self, monthly_sales: list[dict]) -> None:
        ax = self.sales_chart["axis"]
        ax.clear()
        ax.set_title("Vendas por período")
        labels = [row["mes"] for row in monthly_sales]
        values = [row["receita"] for row in monthly_sales]
        if values:
            ax.plot(labels, values, marker="o", color="#2b6cb0")
        ax.tick_params(axis="x", rotation=25)
        ax.grid(True, alpha=0.3)
        self.sales_chart["canvas"].draw()

    def _draw_expense_chart(self, expenses_by_category: list[dict]) -> None:
        ax = self.expenses_chart["axis"]
        ax.clear()
        ax.set_title("Gastos por categoria")
        labels = [row["categoria"] for row in expenses_by_category]
        values = [row["total"] for row in expenses_by_category]
        if values:
            ax.pie(values, labels=labels, autopct="%1.0f%%")
        self.expenses_chart["canvas"].draw()

    def _draw_profit_chart(self, monthly_sales: list[dict]) -> None:
        ax = self.profit_chart["axis"]
        ax.clear()
        ax.set_title("Lucro mensal")
        labels = [row["mes"] for row in monthly_sales]
        values = [row["lucro"] for row in monthly_sales]
        if values:
            colors = ["#1f9d55" if v >= 0 else "#d64545" for v in values]
            ax.bar(labels, values, color=colors)
        ax.tick_params(axis="x", rotation=25)
        ax.axhline(0, color="black", linewidth=0.8)
        self.profit_chart["canvas"].draw()
