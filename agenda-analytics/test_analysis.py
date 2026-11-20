import sqlite3
import unittest

from analysis import build, generate


class AgendaTest(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(":memory:")
        self.addCleanup(self.db.close)

    def test_cancelled_outside_the_no_show_denominator(self):
        rows = [
            (1, "2025-01-08", "N", "Manha", 1, "falta"),
            (2, "2025-01-08", "N", "Manha", 1, "realizado"),
            (3, "2025-01-08", "N", "Manha", 0, "cancelado"),
        ]
        report, segments, trend = build(self.db, rows)
        self.assertEqual((report["marcados"], report["elegiveis"]), (3, 2))
        self.assertEqual(report["taxa_falta_pct"], 50.0)
        self.assertEqual(segments[0]["faltas"], 1)
        self.assertEqual(trend[0]["mes"], "2025-01")

    def test_cancelled_only_segment_has_no_defined_rate(self):
        report, segments, _ = build(
            self.db, [(1, "2025-01-01", "N", "Manha", 1, "cancelado")]
        )
        self.assertIsNone(report["taxa_falta_pct"])
        self.assertIsNone(segments[0]["taxa_falta_pct"])

    def test_generation_is_reproducible(self):
        self.assertEqual(list(generate(20)), list(generate(20)))

    def test_rejects_unknown_outcome(self):
        with self.assertRaises(sqlite3.IntegrityError):
            build(self.db, [(1, "2025-01-01", "N", "Manha", 1, "desconhecido")])


if __name__ == "__main__":
    unittest.main()
