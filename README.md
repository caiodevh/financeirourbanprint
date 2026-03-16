# Financeiro Urbano Print

Aplicativo desktop em Python para gestão financeira de uma pequena loja de camisetas personalizadas.

## Funcionalidades
- Dashboard com receita, gastos, lucro, lucro líquido e margem.
- Registro de vendas com cálculo automático de valor total e lucro.
- Registro de gastos e custos operacionais.
- Histórico financeiro com filtros por período, tipo e busca por cliente.
- Exportação para CSV.
- Relatórios em PDF (7 dias, 30 dias e geral) com gráfico e tabelas.
- Backup automático do banco SQLite.
- Confirmação antes de apagar registros.

## Estrutura
```
finance_app/
  main.py
  database/database_manager.py
  ui/dashboard.py
  ui/sales_page.py
  ui/expenses_page.py
  ui/reports_page.py
  services/finance_calculator.py
  services/report_generator.py
```

## Como executar
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
pip install -r requirements.txt
python finance_app/main.py
```

Banco SQLite padrão: `finance_store.db`.
