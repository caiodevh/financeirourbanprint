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
run.py
build_executable.py
Abrir_Financeiro.bat
abrir_financeiro.sh
```

## Como executar em modo desenvolvimento
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
pip install -r requirements.txt
python run.py
```

Banco SQLite padrão: `finance_store.db`.

---

## Gerar executável (1 clique)

### Windows
1. Instale dependências:
   ```bat
   pip install -r requirements.txt
   ```
2. Gere o executável:
   ```bat
   python build_executable.py
   ```
3. Abra com 1 clique no arquivo:
   - `Abrir_Financeiro.bat`

O executável será criado em: `dist/FinanceiroUrbanoPrint.exe`.

### Linux/macOS
1. Instale dependências:
   ```bash
   pip install -r requirements.txt
   ```
2. Gere o executável:
   ```bash
   python build_executable.py
   ```
3. Abra com 1 clique (duplo clique/terminal):
   - `./abrir_financeiro.sh`

O executável será criado em: `dist/FinanceiroUrbanoPrint`.
