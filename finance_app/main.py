from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QMainWindow,
    QMessageBox,
    QTabWidget,
    QWidget,
)

from finance_app.database.database_manager import DatabaseManager
from finance_app.services.finance_calculator import FinanceCalculator
from finance_app.services.report_generator import ReportGenerator
from finance_app.ui.dashboard import DashboardPage
from finance_app.ui.expenses_page import ExpensesPage
from finance_app.ui.reports_page import ReportsPage
from finance_app.ui.sales_page import SalesPage


class FinanceApp(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Financeiro Urbano Print")
        self.resize(1400, 850)

        self.db = DatabaseManager("finance_store.db")
        self.calculator = FinanceCalculator()
        self.report_generator = ReportGenerator()

        tabs = QTabWidget()
        self.dashboard = DashboardPage()
        self.sales_page = SalesPage()
        self.expenses_page = ExpensesPage()
        self.reports_page = ReportsPage()

        tabs.addTab(self.dashboard, "Dashboard")
        tabs.addTab(self.sales_page, "Registrar Venda")
        tabs.addTab(self.expenses_page, "Registrar Gastos")
        tabs.addTab(self.reports_page, "Histórico e Relatórios")

        self.setCentralWidget(tabs)
        self._connect_signals()
        self.refresh_all()

    def _connect_signals(self) -> None:
        self.sales_page.calc_button.clicked.connect(self.calculate_sale)
        self.sales_page.save_button.clicked.connect(self.save_sale)
        self.expenses_page.save_expense_button.clicked.connect(self.save_expense)
        self.expenses_page.save_op_button.clicked.connect(self.save_operational)

        self.reports_page.apply_filter_btn.clicked.connect(self.refresh_history)
        self.reports_page.export_csv_btn.clicked.connect(self.export_csv)
        self.reports_page.export_pdf_period_btn.clicked.connect(lambda: self.export_pdf("7 dias"))
        self.reports_page.export_pdf_30_btn.clicked.connect(lambda: self.export_pdf("30 dias"))
        self.reports_page.export_pdf_geral_btn.clicked.connect(lambda: self.export_pdf("geral"))
        self.reports_page.backup_btn.clicked.connect(self.backup_db)
        self.reports_page.delete_btn.clicked.connect(self.delete_selected)

    def _show_info(self, title: str, text: str) -> None:
        QMessageBox.information(self, title, text)

    def _show_error(self, title: str, text: str) -> None:
        QMessageBox.critical(self, title, text)

    def calculate_sale(self) -> None:
        try:
            payload = self.sales_page.get_payload()
            value, profit = self.calculator.calculate_sale_values(
                payload["quantidade"], payload["preco_unitario"], payload["custo_producao"]
            )
            self.sales_page.set_calculated(value, profit)
        except ValueError:
            self._show_error("Erro", "Preencha quantidade, preço e custo com valores numéricos.")

    def save_sale(self) -> None:
        try:
            payload = self.sales_page.get_payload()
            if not payload["cliente"] or not payload["produto"]:
                self._show_error("Validação", "Cliente e produto são obrigatórios.")
                return
            payload["valor_total"], payload["lucro"] = self.calculator.calculate_sale_values(
                payload["quantidade"], payload["preco_unitario"], payload["custo_producao"]
            )
            self.db.add_sale(payload)
            self.sales_page.clear_form()
            self.refresh_all()
            self._show_info("Sucesso", "Venda registrada com sucesso.")
        except ValueError:
            self._show_error("Erro", "Verifique os números informados.")

    def save_expense(self) -> None:
        try:
            payload = self.expenses_page.get_expense_payload()
            if not payload["descricao"]:
                self._show_error("Validação", "Descrição obrigatória.")
                return
            self.db.add_expense(payload)
            self.expenses_page.clear_expense_form()
            self.refresh_all()
            self._show_info("Sucesso", "Gasto registrado com sucesso.")
        except ValueError:
            self._show_error("Erro", "Valor inválido para gasto.")

    def save_operational(self) -> None:
        try:
            payload = self.expenses_page.get_operational_payload()
            if not payload["descricao"]:
                self._show_error("Validação", "Descrição obrigatória.")
                return
            self.db.add_operational_cost(payload)
            self.expenses_page.clear_op_form()
            self.refresh_all()
            self._show_info("Sucesso", "Custo operacional registrado com sucesso.")
        except ValueError:
            self._show_error("Erro", "Valor inválido para custo operacional.")

    def refresh_all(self) -> None:
        sales = [dict(r) for r in self.db.fetch_sales()]
        expenses = [dict(r) for r in self.db.fetch_expenses()]
        op_costs = [dict(r) for r in self.db.fetch_operational_costs()]

        indicators = self.calculator.indicators_from_data(sales, expenses, op_costs)
        self.dashboard.refresh(
            indicators.__dict__,
            [dict(r) for r in self.db.fetch_monthly_sales()],
            [dict(r) for r in self.db.fetch_expenses_by_category()],
        )
        self.refresh_history()

    def refresh_history(self) -> None:
        start = self.reports_page.start_date.date().toString("yyyy-MM-dd")
        end = self.reports_page.end_date.date().toString("yyyy-MM-dd")
        cliente = self.reports_page.search_cliente.text().strip()

        history = self.db.fetch_financial_history(start, end)
        if cliente:
            history = [row for row in history if cliente.lower() in row["descricao"].lower()]
        self.reports_page.update_table(history)

    def export_csv(self) -> None:
        history = self.db.fetch_financial_history(
            self.reports_page.start_date.date().toString("yyyy-MM-dd"),
            self.reports_page.end_date.date().toString("yyyy-MM-dd"),
        )
        if not history:
            self._show_info("Exportação", "Sem dados para exportar.")
            return
        target, _ = QFileDialog.getSaveFileName(self, "Salvar CSV", "historico_financeiro.csv", "CSV (*.csv)")
        if not target:
            return
        pd.DataFrame(history).to_csv(target, index=False, encoding="utf-8-sig")
        self._show_info("Exportação", f"CSV exportado em:\n{target}")

    def export_pdf(self, period: str) -> None:
        start, end = self.report_generator.period_range(period)
        sales = [dict(r) for r in self.db.fetch_sales(start, end)]
        expenses = [dict(r) for r in self.db.fetch_expenses(start, end)]
        op_costs = [dict(r) for r in self.db.fetch_operational_costs(start, end)]
        pdf_path = self.report_generator.generate_pdf(period, sales, expenses, op_costs)
        self._show_info("Relatório", f"PDF gerado em:\n{pdf_path}")

    def backup_db(self) -> None:
        backup = self.db.backup_database("backups")
        self._show_info("Backup", f"Backup concluído:\n{backup}")

    def delete_selected(self) -> None:
        selected = self.reports_page.selected_record()
        if not selected:
            self._show_error("Excluir", "Selecione um registro na tabela.")
            return
        if not self.reports_page.confirm_delete():
            return
        table, record_id = selected
        self.db.delete_record(table, record_id)
        self.refresh_all()


def main() -> None:
    app = QApplication(sys.argv)
    window = FinanceApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
