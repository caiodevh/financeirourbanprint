from __future__ import annotations

import shutil
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Iterable, Optional


class DatabaseManager:
    def __init__(self, db_path: str | Path = "finance_app.db") -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    @contextmanager
    def connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def _init_db(self) -> None:
        with self.connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS produtos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL UNIQUE,
                    tipo TEXT,
                    custo_base REAL NOT NULL DEFAULT 0,
                    preco_sugerido REAL NOT NULL DEFAULT 0
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS vendas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    data TEXT NOT NULL,
                    cliente TEXT NOT NULL,
                    produto TEXT NOT NULL,
                    quantidade INTEGER NOT NULL,
                    preco_unitario REAL NOT NULL,
                    valor_total REAL NOT NULL,
                    custo_producao REAL NOT NULL,
                    lucro REAL NOT NULL,
                    forma_pagamento TEXT NOT NULL,
                    observacoes TEXT
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS gastos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    data TEXT NOT NULL,
                    categoria TEXT NOT NULL,
                    descricao TEXT NOT NULL,
                    valor REAL NOT NULL
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS custos_operacionais (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    data TEXT NOT NULL,
                    tipo TEXT NOT NULL,
                    descricao TEXT NOT NULL,
                    valor REAL NOT NULL
                )
                """
            )

    def backup_database(self, backup_dir: str | Path = "backups") -> Path:
        backup_path = Path(backup_dir)
        backup_path.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        target = backup_path / f"finance_backup_{timestamp}.db"
        shutil.copy2(self.db_path, target)
        return target

    def add_sale(self, payload: dict) -> int:
        with self.connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO vendas (
                    data, cliente, produto, quantidade, preco_unitario,
                    valor_total, custo_producao, lucro, forma_pagamento, observacoes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    payload["data"],
                    payload["cliente"],
                    payload["produto"],
                    payload["quantidade"],
                    payload["preco_unitario"],
                    payload["valor_total"],
                    payload["custo_producao"],
                    payload["lucro"],
                    payload["forma_pagamento"],
                    payload.get("observacoes", ""),
                ),
            )
            return cursor.lastrowid

    def add_expense(self, payload: dict) -> int:
        with self.connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO gastos (data, categoria, descricao, valor) VALUES (?, ?, ?, ?)",
                (payload["data"], payload["categoria"], payload["descricao"], payload["valor"]),
            )
            return cursor.lastrowid

    def add_operational_cost(self, payload: dict) -> int:
        with self.connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO custos_operacionais (data, tipo, descricao, valor) VALUES (?, ?, ?, ?)",
                (payload["data"], payload["tipo"], payload["descricao"], payload["valor"]),
            )
            return cursor.lastrowid

    def add_product(self, payload: dict) -> int:
        with self.connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO produtos (nome, tipo, custo_base, preco_sugerido)
                VALUES (?, ?, ?, ?)
                """,
                (payload["nome"], payload.get("tipo", ""), payload["custo_base"], payload["preco_sugerido"]),
            )
            return cursor.lastrowid

    def delete_record(self, table: str, record_id: int) -> None:
        if table not in {"vendas", "gastos", "custos_operacionais", "produtos"}:
            raise ValueError("Tabela inválida")
        with self.connection() as conn:
            conn.execute(f"DELETE FROM {table} WHERE id = ?", (record_id,))

    def fetch_sales(self, start_date: Optional[str] = None, end_date: Optional[str] = None, cliente: str = "") -> list[sqlite3.Row]:
        query = "SELECT * FROM vendas WHERE 1=1"
        params: list = []
        if start_date:
            query += " AND data >= ?"
            params.append(start_date)
        if end_date:
            query += " AND data <= ?"
            params.append(end_date)
        if cliente:
            query += " AND cliente LIKE ?"
            params.append(f"%{cliente}%")
        query += " ORDER BY data DESC, id DESC"
        with self.connection() as conn:
            return conn.execute(query, params).fetchall()

    def fetch_expenses(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> list[sqlite3.Row]:
        query = "SELECT * FROM gastos WHERE 1=1"
        params: list = []
        if start_date:
            query += " AND data >= ?"
            params.append(start_date)
        if end_date:
            query += " AND data <= ?"
            params.append(end_date)
        query += " ORDER BY data DESC, id DESC"
        with self.connection() as conn:
            return conn.execute(query, params).fetchall()

    def fetch_operational_costs(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> list[sqlite3.Row]:
        query = "SELECT * FROM custos_operacionais WHERE 1=1"
        params: list = []
        if start_date:
            query += " AND data >= ?"
            params.append(start_date)
        if end_date:
            query += " AND data <= ?"
            params.append(end_date)
        query += " ORDER BY data DESC, id DESC"
        with self.connection() as conn:
            return conn.execute(query, params).fetchall()

    def fetch_products(self) -> list[sqlite3.Row]:
        with self.connection() as conn:
            return conn.execute("SELECT * FROM produtos ORDER BY nome ASC").fetchall()

    def fetch_monthly_sales(self) -> Iterable[sqlite3.Row]:
        with self.connection() as conn:
            return conn.execute(
                """
                SELECT substr(data, 1, 7) AS mes,
                       SUM(valor_total) AS receita,
                       SUM(custo_producao) AS custo,
                       SUM(lucro) AS lucro
                FROM vendas
                GROUP BY substr(data, 1, 7)
                ORDER BY mes
                """
            ).fetchall()

    def fetch_expenses_by_category(self) -> Iterable[sqlite3.Row]:
        with self.connection() as conn:
            return conn.execute(
                """
                SELECT categoria, SUM(valor) as total
                FROM gastos
                GROUP BY categoria
                ORDER BY total DESC
                """
            ).fetchall()

    def fetch_financial_history(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> list[dict]:
        sales = [dict(row) | {"tipo": "Venda"} for row in self.fetch_sales(start_date, end_date)]
        expenses = [dict(row) | {"tipo": "Gasto"} for row in self.fetch_expenses(start_date, end_date)]
        costs = [dict(row) | {"tipo": "Custo Operacional"} for row in self.fetch_operational_costs(start_date, end_date)]

        normalized: list[dict] = []
        for row in sales:
            normalized.append(
                {
                    "id": row["id"],
                    "data": row["data"],
                    "tipo": "Venda",
                    "categoria": row["forma_pagamento"],
                    "descricao": f"{row['cliente']} - {row['produto']}",
                    "valor": row["valor_total"],
                }
            )
        for row in expenses:
            normalized.append(
                {
                    "id": row["id"],
                    "data": row["data"],
                    "tipo": "Gasto",
                    "categoria": row["categoria"],
                    "descricao": row["descricao"],
                    "valor": -row["valor"],
                }
            )
        for row in costs:
            normalized.append(
                {
                    "id": row["id"],
                    "data": row["data"],
                    "tipo": "Custo Operacional",
                    "categoria": row["tipo"],
                    "descricao": row["descricao"],
                    "valor": -row["valor"],
                }
            )

        return sorted(normalized, key=lambda x: (x["data"], x["id"]), reverse=True)
