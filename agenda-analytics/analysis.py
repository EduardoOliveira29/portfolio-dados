"""Generate a fictional appointment ledger and export operational KPIs."""

import argparse
import csv
import json
import random
import sqlite3
from contextlib import closing
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent
UNITS = ("N", "S", "C")
SHIFTS = ("Manha", "Tarde", "Noite")


def generate(count, seed=42):
    rng = random.Random(seed)
    for appointment_id in range(1, count + 1):
        day = date(2025, 1, 1) + timedelta(days=rng.randrange(181))
        unit = rng.choice(UNITS)
        shift = rng.choice(SHIFTS)
        reminder = int(rng.random() < 0.75)
        risk = 0.10 + 0.07 * (shift == "Noite") + 0.04 * (unit == "N")
        draw = rng.random()
        outcome = "cancelado" if draw < 0.10 else "falta" if draw < 0.10 + risk else "realizado"
        yield appointment_id, day.isoformat(), unit, shift, reminder, outcome


def build(db, rows):
    db.row_factory = sqlite3.Row
    db.executescript((ROOT / "modelo.sql").read_text("utf-8"))
    with db:
        db.executemany("INSERT INTO agendamento VALUES (?, ?, ?, ?, ?, ?)", rows)
    summary = dict(db.execute("SELECT * FROM resumo").fetchone())
    segments = [dict(row) for row in db.execute(
        "SELECT * FROM por_segmento ORDER BY faltas DESC, unidade, turno"
    )]
    trend = [dict(row) for row in db.execute("SELECT * FROM por_mes ORDER BY mes")]
    return summary, segments, trend


def write_csv(path, rows):
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registros", type=int, default=2400)
    args = parser.parse_args()
    if args.registros < 1:
        parser.error("--registros deve ser positivo")

    output = ROOT / "resultados"
    output.mkdir(exist_ok=True)
    with closing(sqlite3.connect(":memory:")) as db:
        report, segments, trend = build(db, generate(args.registros))
        raw_rows = [dict(row) for row in db.execute("SELECT * FROM agendamento ORDER BY id")]
        write_csv(output / "agendamentos.csv", raw_rows)
        write_csv(output / "segmentos.csv", segments)
        write_csv(output / "mensal.csv", trend)
    (output / "resumo.json").write_text(json.dumps(report, indent=2) + "\n", "utf-8")
    print(json.dumps(report))


if __name__ == "__main__":
    main()
