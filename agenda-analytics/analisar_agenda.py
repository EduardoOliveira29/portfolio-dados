"""Gera uma agenda fictícia e consulta os indicadores no Oracle."""

import argparse
import csv
import json
import random
import os
from getpass import getpass
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


COLUNAS = ("id", "data_prevista", "unidade_id", "turno", "lembrete_enviado", "desfecho")


def registros(rows):
    vistos = set()
    for linha in rows:
        codigo, dia, unidade, turno, lembrete, desfecho = linha
        date.fromisoformat(dia)
        if codigo in vistos or unidade not in UNITS or turno not in SHIFTS:
            raise ValueError("Identificador repetido ou unidade/turno inválido")
        if lembrete not in (0, 1) or desfecho not in ("realizado", "cancelado", "falta"):
            raise ValueError("Lembrete ou desfecho inválido")
        vistos.add(codigo)
        yield dict(zip(COLUNAS, linha, strict=True))


def build(db, rows):
    import oracledb

    base = (ROOT / "modelo.sql").read_text("utf-8")
    dados = json.dumps(list(registros(rows)))
    segmentos, mensal = [], []
    with db.cursor() as cursor:
        cursor.setinputsizes(dados=oracledb.DB_TYPE_CLOB)
        cursor.execute(base, dados=dados)
        nomes = [coluna[0].lower() for coluna in cursor.description]
        for linha in cursor:
            registro = dict(zip(nomes, linha))
            recorte = registro.pop("recorte")
            for chave in ("mes", "unidade", "turno"):
                if registro[chave] is None:
                    del registro[chave]
            if recorte == "resumo":
                resumo = registro
            elif recorte == "mensal":
                mensal.append(registro)
            else:
                segmentos.append(registro)
    return resumo, segmentos, mensal


def write_csv(path, rows):
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__, add_help=False, usage="%(prog)s [opções]")
    opcoes = parser.add_argument_group("Opções")
    opcoes.add_argument("-h", "--ajuda", "--help", action="help", help="Mostrar esta ajuda e sair")
    opcoes.add_argument("--registros", type=int, default=2400, metavar="N", help="Quantidade de agendamentos fictícios")
    args = parser.parse_args()
    if args.registros < 1:
        parser.error("--registros deve ser positivo")

    output = ROOT / "resultados"
    output.mkdir(exist_ok=True)
    import oracledb

    linhas = list(generate(args.registros))
    with oracledb.connect(user=os.environ["ORACLE_USER"], dsn=os.environ["ORACLE_DSN"],
                          password=getpass("Senha do Oracle: ")) as db:
        report, segments, trend = build(db, linhas)
    write_csv(output / "agendamentos.csv", [dict(zip(COLUNAS, row)) for row in linhas])
    write_csv(output / "segmentos.csv", segments)
    write_csv(output / "mensal.csv", trend)
    (output / "resumo.json").write_text(json.dumps(report, indent=2) + "\n", "utf-8")
    print(json.dumps(report))


if __name__ == "__main__":
    main()
