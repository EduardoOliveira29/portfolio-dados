"""Regenerate the portfolio figures from the exported CSV files."""

import csv
from datetime import date
from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter

ROOT = Path(__file__).resolve().parent
INK = "#17334a"
TEAL = "#137c76"
GOLD = "#9b5305"
PAPER = "#faf8f2"
MUTED = "#506473"


def create_chart(title, subtitle, source):
    figure, axis = plt.subplots(figsize=(10, 5.1), facecolor=PAPER)
    axis.set_facecolor(PAPER)
    figure.subplots_adjust(left=0.17, right=0.92, bottom=0.17, top=0.77)
    figure.text(0.08, 0.91, title, fontsize=23, weight="bold", color=INK)
    figure.text(0.08, 0.84, subtitle, fontsize=11, color=MUTED)
    figure.text(0.08, 0.055, source, fontsize=9, color=MUTED)
    axis.spines[:].set_visible(False)
    axis.tick_params(length=0, pad=8, colors=MUTED)
    axis.set_axisbelow(True)
    return figure, axis


def chart_bcb():
    folder = ROOT / "indicadores-bcb" / "resultados"
    with (folder / "indicadores.csv").open(encoding="utf-8", newline="") as file:
        rows = [row for row in csv.DictReader(file) if row["ipca_12m_pct"]]
    months = [date.fromisoformat(row["mes"] + "-01") for row in rows]
    figure, axis = create_chart(
        "Inflação e juros no Brasil",
        "Variação acumulada em 12 meses (%)",
        "Fonte: Banco Central do Brasil, SGS 433 e 4390. Recorte de jan/2020 a dez/2025.",
    )
    for key, label, color in (
        ("ipca_12m_pct", "IPCA", TEAL),
        ("selic_12m_pct", "Selic efetiva", GOLD),
    ):
        values = [float(row[key]) for row in rows]
        axis.plot(months, values, label=label, color=color, linewidth=2.5)
    axis.xaxis.set_major_locator(mdates.YearLocator())
    axis.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    axis.set_xlim(months[0], months[-1])
    axis.yaxis.set_major_formatter(PercentFormatter(100, decimals=0))
    axis.set_ylim(bottom=0)
    axis.grid(axis="y", color="#deded5", linewidth=0.7)
    axis.legend(loc="upper left", frameon=False, labelcolor=INK)
    figure.savefig(folder / "evolucao.png", dpi=145)
    plt.close(figure)


def chart_agenda():
    folder = ROOT / "agenda-analytics" / "resultados"
    with (folder / "segmentos.csv").open(encoding="utf-8", newline="") as file:
        rows = list(reversed(list(csv.DictReader(file))))
    figure, axis = create_chart(
        "Onde se concentram as faltas?",
        "Volume de faltas por unidade e turno",
        "Dados sintéticos. Percentuais calculados sobre realizados e faltas.",
    )
    labels = [f"{row['unidade']} · {row['turno'].replace('Manha', 'Manhã')}" for row in rows]
    bars = axis.barh(labels, [int(row["faltas"]) for row in rows],
                     color=[TEAL if row["turno"] == "Noite" else "#a6b4bc" for row in rows])
    for bar, row in zip(bars, rows, strict=True):
        label = f"{row['faltas']} ({float(row['taxa_falta_pct']):.2f}%)".replace(".", ",")
        axis.annotate(label, (bar.get_width(), bar.get_y() + bar.get_height() / 2),
                      xytext=(5, 0), textcoords="offset points", va="center", color=INK)
    axis.set_xlim(0, max(int(row["faltas"]) for row in rows) * 1.24)
    axis.grid(axis="x", color="#deded5", linewidth=0.7)
    figure.savefig(folder / "faltas.png", dpi=145)
    plt.close(figure)


if __name__ == "__main__":
    chart_bcb()
    chart_agenda()
