"""Normalize SGS data and calculate comparable monthly and rolling rates."""

import argparse
import csv
import json
import math
import sqlite3
from contextlib import closing
from datetime import datetime
from pathlib import Path
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parent
SERIES = {"ipca": 433, "selic": 4390}
START, END = "01/01/2020", "31/12/2025"
API = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.{code}/dados"


def fetch(code):
    query = f"?formato=json&dataInicial={START}&dataFinal={END}"
    with urlopen(API.format(code=code) + query, timeout=30) as response:
        return json.load(response)


def normalize(rows):
    months = {}
    for row in rows:
        month = datetime.strptime(row["data"], "%d/%m/%Y").strftime("%Y-%m")
        value = float(row["valor"])
        if month in months:
            raise ValueError(f"Mês duplicado: {month}")
        if not math.isfinite(value) or value <= -100:
            raise ValueError(f"Taxa percentual inválida em {month}: {value}")
        months[month] = value
    return months


def rolling_metrics(ipca, selic):
    months = sorted(ipca)
    if not months or ipca.keys() != selic.keys():
        raise ValueError("Séries vazias ou com cobertura mensal divergente")
    positions = [int(month[:4]) * 12 + int(month[5:]) for month in months]
    if positions != list(range(positions[0], positions[-1] + 1)):
        raise ValueError("Séries com lacuna no calendário")

    with closing(sqlite3.connect(":memory:")) as db:
        db.row_factory = sqlite3.Row
        db.create_function("log_factor", 1, lambda rate: math.log1p(rate / 100))
        db.create_function("to_percent", 1, lambda total: 100 * math.expm1(total))
        db.execute(
            "CREATE TABLE serie_mensal (mes TEXT PRIMARY KEY, ipca REAL, selic REAL)"
        )
        db.executemany(
            "INSERT INTO serie_mensal VALUES (?, ?, ?)",
            ((month, ipca[month], selic[month]) for month in months),
        )
        return [dict(row) for row in db.execute((ROOT / "metricas.sql").read_text("utf-8"))]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--atualizar", action="store_true", help="Baixar novamente o recorte SGS")
    args = parser.parse_args()
    original_data = ROOT / "dados"
    if args.atualizar:
        snapshots = {name: fetch(code) for name, code in SERIES.items()}
    else:
        snapshots = {
            name: json.loads((original_data / f"sgs-{code}.json").read_text("utf-8"))
            for name, code in SERIES.items()
        }
    rows = rolling_metrics(*(normalize(snapshots[name]) for name in SERIES))
    if len(rows) != 72 or rows[0]["mes"] != "2020-01" or rows[-1]["mes"] != "2025-12":
        raise ValueError("Recorte SGS incompleto: esperado janeiro de 2020 a dezembro de 2025")
    if args.atualizar:
        original_data.mkdir(exist_ok=True)
        for name, code in SERIES.items():
            (original_data / f"sgs-{code}.json").write_text(
                json.dumps(snapshots[name], ensure_ascii=False, indent=2) + "\n", "utf-8"
            )
    output = ROOT / "resultados"
    output.mkdir(exist_ok=True)
    with (output / "indicadores.csv").open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"{len(rows)} meses; último mês: {rows[-1]}")


if __name__ == "__main__":
    main()
