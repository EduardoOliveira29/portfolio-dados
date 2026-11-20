"""Consulta IPCA e Selic por mês no Oracle e calcula as taxas acumuladas."""

import argparse
import csv
import json
import math
import os
from getpass import getpass
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


def validar_calendario(ipca, selic):
    months = sorted(ipca)
    if not months or ipca.keys() != selic.keys():
        raise ValueError("Séries vazias ou com cobertura mensal divergente")
    positions = [int(month[:4]) * 12 + int(month[5:]) for month in months]
    if positions != list(range(positions[0], positions[-1] + 1)):
        raise ValueError("Séries com lacuna no calendário")

def juntar_series(db, ipca, selic):
    import oracledb

    def parametro(serie):
        return json.dumps([{"mes": mes, "taxa": taxa} for mes, taxa in serie.items()])

    with db.cursor() as cursor:
        cursor.setinputsizes(ipca=oracledb.DB_TYPE_CLOB, selic=oracledb.DB_TYPE_CLOB)
        cursor.execute((ROOT / "metricas.sql").read_text("utf-8"),
                       ipca=parametro(ipca), selic=parametro(selic))
        return [{"mes": mes, "ipca_mensal_pct": ipca_mes, "selic_mensal_pct": selic_mes}
                for mes, ipca_mes, selic_mes in cursor]


def acumular(rows):
    for index, row in enumerate(rows):
        row["ipca_12m_pct"] = None
        row["selic_12m_pct"] = None
        if index >= 11:
            window = rows[index - 11:index + 1]
            row["ipca_12m_pct"] = compound(window, "ipca_mensal_pct")
            row["selic_12m_pct"] = compound(window, "selic_mensal_pct")
    return rows


def compound(window, field):
    factor = 1.0
    for row in window:
        factor *= 1 + row[field] / 100
    return round((factor - 1) * 100, 8)


def main():
    parser = argparse.ArgumentParser(description=__doc__, add_help=False, usage="%(prog)s [opções]")
    opcoes = parser.add_argument_group("Opções")
    opcoes.add_argument("-h", "--ajuda", "--help", action="help", help="Mostrar esta ajuda e sair")
    opcoes.add_argument("--atualizar", action="store_true", help="Baixar novamente o recorte SGS")
    args = parser.parse_args()
    original_data = ROOT / "dados"
    if args.atualizar:
        snapshots = {name: fetch(code) for name, code in SERIES.items()}
    else:
        snapshots = {
            name: json.loads((original_data / f"sgs-{code}.json").read_text("utf-8"))
            for name, code in SERIES.items()
        }
    import oracledb

    ipca, selic = (normalize(snapshots[name]) for name in SERIES)
    validar_calendario(ipca, selic)
    with oracledb.connect(user=os.environ["ORACLE_USER"], dsn=os.environ["ORACLE_DSN"],
                          password=getpass("Senha do Oracle: ")) as db:
        rows = acumular(juntar_series(db, ipca, selic))
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
