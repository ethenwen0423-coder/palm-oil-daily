import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
SCRIPT = SCRIPTS / "record_forecast.py"
SPEC = importlib.util.spec_from_file_location("record_forecast", SCRIPT)
record_forecast = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(record_forecast)


def contract(product: str, contract_code: str, stance: str, confidence: str = "中", total: float = 60.0, warning: str = "暂无明显冲突信号") -> dict:
    return {
        "product": product,
        "contract": contract_code,
        "contract_rank": 1,
        "score": {
            "total": total,
            "technical": 51.0,
            "fundamental": 50.0,
            "driver": 67.4,
            "money_flow": 56.6,
            "stance": stance,
            "view_confidence": confidence,
            "contradiction_warning": warning,
        },
        "strategy_recommendation": {
            "upper_watch": "9420",
            "lower_watch": "9250",
            "invalidation": "跌破 9200 后当前判断失效",
        },
    }


def payload() -> dict:
    return {
        "contracts": [
            contract("P", "P2609", "震荡偏强"),
            contract("Y", "Y2609", "震荡偏弱"),
            contract("OI", "OI2609", "震荡"),
        ]
    }


def write_oil_futures(path: Path, value: dict) -> None:
    path.write_text("window.OIL_FUTURES_CONTRACTS = " + json.dumps(value, ensure_ascii=False) + ";\n", encoding="utf-8")


class RecordForecastTest(unittest.TestCase):
    generated_at = "2026-07-13T08:20:00+08:00"
    cutoff_at = "2026-07-13T08:15:00+08:00"
    report_date = "2026-07-13"

    def freeze(self, root: Path, source: dict | None = None, quality_gate_status: str = "ok") -> tuple[dict, Path]:
        oil_futures = root / "oil_futures.js"
        target = root / "forecast" / "2026-07-13.json"
        write_oil_futures(oil_futures, source or payload())
        result = record_forecast.freeze_forecast(
            oil_futures, target, self.report_date, self.generated_at, self.cutoff_at, quality_gate_status
        )
        return result, target

    def test_rank_one_p_y_oi_generate_and_rank_two_is_ignored(self) -> None:
        source = payload()
        rank_two = copy.deepcopy(source["contracts"][0])
        rank_two["contract"] = "P2701"
        rank_two["contract_rank"] = 2
        source["contracts"].append(rank_two)
        with tempfile.TemporaryDirectory() as temporary:
            result, target = self.freeze(Path(temporary), source)
            saved = json.loads(target.read_text(encoding="utf-8"))
        self.assertFalse(result["already_exists"])
        self.assertEqual([record["contract"] for record in saved["records"]], ["P2609", "Y2609", "OI2609"])

    def test_missing_main_contract_fails(self) -> None:
        source = payload()
        source["contracts"].pop()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            with self.assertRaisesRegex(ValueError, "缺少 rank=1 主力合约"):
                self.freeze(root, source)
            self.assertFalse((root / "forecast" / "2026-07-13.json").exists())

    def test_quality_gate_failure_does_not_write(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            with self.assertRaisesRegex(ValueError, "quality-gate-status"):
                self.freeze(root, quality_gate_status="blocked")
            self.assertFalse((root / "forecast" / "2026-07-13.json").exists())

    def test_bullish_bearish_and_range_probability_formulas(self) -> None:
        self.assertEqual(record_forecast.score_map_v1(75, "偏多", "高", "暂无明显冲突信号"), {"up": 0.695, "range": 0.305, "down": 0.0})
        self.assertEqual(record_forecast.score_map_v1(75, "偏空", "高", "暂无明显冲突信号"), {"up": 0.0, "range": 0.305, "down": 0.695})
        self.assertEqual(record_forecast.score_map_v1(75, "震荡", "高", "暂无明显冲突信号"), {"up": 0.225, "range": 0.55, "down": 0.225})

    def test_confidence_mapping_and_conflict_penalty(self) -> None:
        directional_mass = lambda confidence, warning="暂无明显冲突信号": 1 - record_forecast.score_map_v1(75, "偏多", confidence, warning)["range"]
        self.assertAlmostEqual(directional_mass("高"), 0.695, places=6)
        self.assertAlmostEqual(directional_mass("中"), 0.585, places=6)
        self.assertAlmostEqual(directional_mass("低"), 0.4475, places=6)
        self.assertAlmostEqual(directional_mass("缺失"), 0.42, places=6)
        self.assertAlmostEqual(directional_mass("高", "存在冲突"), 0.545, places=6)

    def test_freeze_persists_standardized_and_source_confidence(self) -> None:
        mappings = [("高", "high"), ("medium", "medium"), ("低", "low"), (None, "unknown")]
        for source_confidence, expected_confidence in mappings:
            source = contract("P", "P2609", "震荡偏强", source_confidence)
            frozen = record_forecast.build_record(source, self.report_date, self.generated_at, self.cutoff_at)
            self.assertEqual(frozen["source_confidence"], source_confidence)
            self.assertEqual(frozen["confidence"], expected_confidence)
            self.assertEqual(frozen["outcome_rule_version"], "outcome-v1-fixed-0.30pct")

    def test_probabilities_strictly_sum_to_one(self) -> None:
        probabilities = record_forecast.score_map_v1(63.7, "震荡偏弱", "低", "暂无明显冲突信号")
        self.assertEqual(sum(probabilities.values()), 1.0)

    def test_invalid_watch_range_fails(self) -> None:
        source = payload()
        source["contracts"][0]["strategy_recommendation"]["lower_watch"] = "9420"
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaisesRegex(ValueError, "观察区间无效"):
                self.freeze(Path(temporary), source)

    def test_first_write_is_idempotent_and_validates_against_schema(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            first, target = self.freeze(root)
            saved = json.loads(target.read_text(encoding="utf-8"))
            validated = record_forecast.subprocess.run(
                [sys.executable, str(SCRIPTS / "validate_forecast.py"), "--forecast", str(target)],
                check=False,
                capture_output=True,
                text=True,
            )
            second, _ = self.freeze(root)
        self.assertEqual(first["status"], "ok")
        self.assertFalse(first["already_exists"])
        self.assertEqual(saved["records"][0]["invalidation"]["price"], 9200.0)
        self.assertEqual(validated.returncode, 0, validated.stdout)
        self.assertTrue(second["already_exists"])

    def test_different_content_or_evaluated_record_cannot_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            _, target = self.freeze(root)
            original = target.read_text(encoding="utf-8")
            changed = payload()
            changed["contracts"][0]["score"]["total"] = 70
            with self.assertRaisesRegex(ValueError, "内容不同"):
                self.freeze(root, changed)
            self.assertEqual(target.read_text(encoding="utf-8"), original)

            existing = json.loads(original)
            existing["records"][0]["evaluation_status"] = "evaluated"
            target.write_text(json.dumps(existing), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "不是 pending"):
                self.freeze(root)

    def test_cli_freezes_temp_fixture(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "oil_futures.js"
            target = root / "forecast" / "2026-07-13.json"
            write_oil_futures(source, payload())
            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--oil-futures",
                    str(source),
                    "--forecast",
                    str(target),
                    "--report-date",
                    self.report_date,
                    "--generated-at",
                    self.generated_at,
                    "--cutoff-at",
                    self.cutoff_at,
                    "--quality-gate-status",
                    "ok",
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            result = json.loads(completed.stdout)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(result["status"], "ok")
        self.assertFalse(result["already_exists"])


if __name__ == "__main__":
    unittest.main()
