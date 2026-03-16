from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Indicators:
    receita_total: float
    gastos_totais: float
    custos_operacionais: float
    lucro_total: float
    lucro_liquido: float
    margem_media: float


class FinanceCalculator:
    @staticmethod
    def calculate_sale_values(quantidade: int, preco_unitario: float, custo_producao: float) -> tuple[float, float]:
        valor_total = quantidade * preco_unitario
        lucro = valor_total - custo_producao
        return valor_total, lucro

    @staticmethod
    def indicators_from_data(sales: list[dict], expenses: list[dict], operational_costs: list[dict]) -> Indicators:
        receita_total = sum(float(row["valor_total"]) for row in sales)
        lucro_total = sum(float(row["lucro"]) for row in sales)
        gastos_totais = sum(float(row["valor"]) for row in expenses)
        custos_totais = sum(float(row["valor"]) for row in operational_costs)
        lucro_liquido = receita_total - gastos_totais - custos_totais - sum(float(row["custo_producao"]) for row in sales)
        margem_media = (lucro_total / receita_total * 100) if receita_total > 0 else 0.0
        return Indicators(
            receita_total=receita_total,
            gastos_totais=gastos_totais,
            custos_operacionais=custos_totais,
            lucro_total=lucro_total,
            lucro_liquido=lucro_liquido,
            margem_media=margem_media,
        )
