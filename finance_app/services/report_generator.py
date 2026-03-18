from __future__ import annotations

from datetime import date, datetime, timedelta
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


class ReportGenerator:
    def __init__(self, output_dir: str | Path = "reports") -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def period_range(self, period: str) -> tuple[str | None, str | None]:
        today = date.today()
        if period == "7 dias":
            return (today - timedelta(days=7)).isoformat(), today.isoformat()
        if period == "30 dias":
            return (today - timedelta(days=30)).isoformat(), today.isoformat()
        return None, None

    def _generate_chart(self, sales_df: pd.DataFrame, expenses_df: pd.DataFrame, output: Path) -> Path | None:
        if sales_df.empty and expenses_df.empty:
            return None
        sales_total = float(sales_df["valor_total"].sum()) if not sales_df.empty else 0
        expenses_total = float(expenses_df["valor"].sum()) if not expenses_df.empty else 0
        fig, ax = plt.subplots(figsize=(4.5, 3))
        ax.bar(["Receita", "Gastos"], [sales_total, expenses_total], color=["#1f9d55", "#d64545"])
        ax.set_title("Receita vs Gastos")
        ax.set_ylabel("R$")
        fig.tight_layout()
        fig.savefig(output)
        plt.close(fig)
        return output

    def generate_pdf(self, period: str, sales: list[dict], expenses: list[dict], op_costs: list[dict]) -> Path:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        pdf_path = self.output_dir / f"relatorio_financeiro_{period.replace(' ', '_')}_{timestamp}.pdf"
        chart_path = self.output_dir / f"chart_{timestamp}.png"

        sales_df = pd.DataFrame(sales)
        exp_df = pd.DataFrame(expenses)
        op_df = pd.DataFrame(op_costs)

        receita = float(sales_df["valor_total"].sum()) if not sales_df.empty else 0.0
        gastos = float(exp_df["valor"].sum()) if not exp_df.empty else 0.0
        custos_op = float(op_df["valor"].sum()) if not op_df.empty else 0.0
        lucro_bruto = receita
        lucro_liquido = lucro_bruto - gastos - custos_op

        chart = self._generate_chart(sales_df, exp_df, chart_path)

        doc = SimpleDocTemplate(str(pdf_path), pagesize=A4)
        styles = getSampleStyleSheet()
        story = []

        story.append(Paragraph("Relatório Financeiro - Loja de Camisetas", styles["Title"]))
        story.append(Paragraph(f"Período: {period}", styles["Heading2"]))
        story.append(Paragraph(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles["Normal"]))
        story.append(Spacer(1, 12))

        summary_data = [
            ["Receita total", f"R$ {receita:,.2f}"],
            ["Gastos totais", f"R$ {gastos + custos_op:,.2f}"],
            ["Lucro bruto", f"R$ {lucro_bruto:,.2f}"],
            ["Lucro líquido", f"R$ {lucro_liquido:,.2f}"],
        ]
        summary_table = Table(summary_data, colWidths=[230, 180])
        summary_table.setStyle(
            TableStyle(
                [
                    ("GRID", (0, 0), (-1, -1), 1, colors.grey),
                    ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke),
                    ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ]
            )
        )
        story.append(Paragraph("Resumo financeiro", styles["Heading3"]))
        story.append(summary_table)
        story.append(Spacer(1, 10))

        story.append(Paragraph("Vendas", styles["Heading3"]))
        sales_rows = [["Data", "Cliente", "Produto", "Valor", "Lucro"]]
        if not sales_df.empty:
            for _, row in sales_df.iterrows():
                sales_rows.append([
                    row.get("data", ""),
                    row.get("cliente", ""),
                    row.get("produto", ""),
                    f"R$ {float(row.get('valor_total', 0)):.2f}",
                    f"R$ {float(row.get('lucro', 0)):.2f}",
                ])
        else:
            sales_rows.append(["-", "-", "-", "R$ 0,00", "R$ 0,00"])

        sales_table = Table(sales_rows, repeatRows=1)
        sales_table.setStyle(
            TableStyle(
                [
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("BACKGROUND", (0, 0), (-1, 0), colors.lightblue),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                ]
            )
        )
        story.append(sales_table)
        story.append(Spacer(1, 10))

        story.append(Paragraph("Gastos", styles["Heading3"]))
        exp_rows = [["Data", "Categoria", "Descrição", "Valor"]]
        if not exp_df.empty:
            for _, row in exp_df.iterrows():
                exp_rows.append([
                    row.get("data", ""),
                    row.get("categoria", ""),
                    row.get("descricao", ""),
                    f"R$ {float(row.get('valor', 0)):.2f}",
                ])
        else:
            exp_rows.append(["-", "-", "-", "R$ 0,00"])

        exp_table = Table(exp_rows, repeatRows=1)
        exp_table.setStyle(
            TableStyle(
                [
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                ]
            )
        )
        story.append(exp_table)
        story.append(Spacer(1, 10))

        if chart and chart.exists():
            story.append(Paragraph("Gráfico de Receita vs Gastos", styles["Heading3"]))
            story.append(Image(str(chart), width=320, height=220))

        story.append(Spacer(1, 16))
        story.append(Paragraph(f"Rodapé: relatório gerado em {datetime.now().strftime('%d/%m/%Y')}", styles["Italic"]))

        doc.build(story)
        return pdf_path
