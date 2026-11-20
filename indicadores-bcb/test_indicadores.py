import unittest

from analisar_indicadores import normalize, acumular, validar_calendario


class SeriesTest(unittest.TestCase):
    def test_normalizes_recent_month_and_negative_reading(self):
        rows = [{"data": "01/10/2025", "valor": "-0.15"}]
        self.assertEqual(normalize(rows), {"2025-10": -0.15})

    def test_duplicate_month_is_rejected(self):
        rows = [
            {"data": "01/01/2025", "valor": "0.33"},
            {"data": "31/01/2025", "valor": "0.35"},
        ]
        with self.assertRaisesRegex(ValueError, "duplicado"):
            normalize(rows)

    def test_accumulates_by_compounding_and_waits_for_full_window(self):
        months = {f"2025-{month:02}": 1.0 for month in range(1, 13)}
        output = acumular([{"mes": m, "ipca_mensal_pct": taxa, "selic_mensal_pct": taxa}
                           for m, taxa in months.items()])
        self.assertIsNone(output[10]["ipca_12m_pct"])
        self.assertAlmostEqual(output[11]["ipca_12m_pct"], (1.01**12 - 1) * 100)

    def test_rejects_a_calendar_gap_even_in_both_sources(self):
        months = {"2025-01": 0.2, "2025-03": 0.3}
        with self.assertRaisesRegex(ValueError, "lacuna"):
            validar_calendario(months, months)


if __name__ == "__main__":
    unittest.main()
