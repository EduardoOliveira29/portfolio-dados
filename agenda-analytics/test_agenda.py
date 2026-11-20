import csv
import json
import unittest

from analisar_agenda import ROOT, generate, registros


class TesteAgenda(unittest.TestCase):
    def test_base_publicada(self):
        with (ROOT / "resultados/agendamentos.csv").open(encoding="utf-8", newline="") as arq:
            publicado = list(csv.DictReader(arq))
        esperado = [{k: str(v) for k, v in linha.items()} for linha in registros(generate(2400))]
        self.assertEqual(esperado, publicado)

    def test_indicadores_publicados(self):
        linhas = list(registros(generate(2400)))
        elegiveis = sum(linha["desfecho"] != "cancelado" for linha in linhas)
        faltas = sum(linha["desfecho"] == "falta" for linha in linhas)
        esperado = dict(marcados=len(linhas), elegiveis=elegiveis, faltas=faltas,
                        cancelados=len(linhas) - elegiveis, taxa_falta_pct=round(100 * faltas / elegiveis, 2))
        self.assertEqual(esperado, json.loads((ROOT / "resultados/resumo.json").read_text("utf-8")))

    def test_desfecho_invalido(self):
        with self.assertRaises(ValueError):
            list(registros([(1, "2025-01-01", "N", "Manha", 1, "desconhecido")]))

    def test_identificador_duplicado(self):
        linha = (1, "2025-01-01", "N", "Manha", 1, "cancelado")
        with self.assertRaises(ValueError):
            list(registros([linha, linha]))


if __name__ == "__main__":
    unittest.main()
