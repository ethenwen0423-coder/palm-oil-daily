import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "verify_public_report_contract.py"
SPEC = importlib.util.spec_from_file_location("verify_public_report_contract", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def valid_daily() -> str:
    sections = {
        "今日观点": "油脂震荡，今日不新开仓；突破区间后判断失效。置信度：★★☆☆☆。",
        "今日交易信号": """今日策略：震荡。

|品种|方向|触发|确认|止损|目标|仓位上限|信号有效期|
|---|---|---|---|---|---|---|---|
|P|震荡|9500|资金确认|9400|9600|不新开仓|日内|
|Y|震荡|8500|资金确认|8400|8600|不新开仓|日内|
|OI|震荡|10000|资金确认|9900|10100|不新开仓|日内|""",
        "核心驱动与预期差": "主驱动一与主驱动二均有来源，供需→价格；预期与现实存在差异，最强反证会推翻判断。",
        "关键数据与价格": """|指标|数值|时点|含义|
|---|---|---|---|
|P2701|9500|07:00|P主线|
|Y2701|8500|07:00|Y联动|
|OI2701|10000|07:00|OI联动|""",
        "开盘推演": """|情景|触发|确认|动作|放弃条件|
|---|---|---|---|---|
|高开|P高开|Y/OI同步|观察|Y/OI背离|
|平开|P平开|Y/OI同步|观察|Y/OI背离|
|低开|P低开|Y/OI同步|不新开仓|Y/OI背离|""",
        "风险提示": "若驱动逆转则判断失效。",
        "信息来源与核验说明": (
            "实际 skill（执行链）：行情采集→数据门禁→预测反馈→新鲜度治理→正文写作→标题门→报告审计→预测冻结。"
            "数据源：官方与结构化行情。截止时间：07:00。失败项：无。替代来源：无。"
        ),
        "消息来源链接": "|来源|用途|链接|\n|---|---|---|\n|官方|核验|https://example.com/|",
        "AI观点风险提示": "本报告由AI生成，不构成投资建议。",
    }
    return "# 09月03日晨报\n\n" + "\n\n".join(
        f"## 【{name}】\n\n{sections[name]}" for name in MODULE.DAILY_SECTIONS
    ) + "\n"


def record(markdown: str) -> dict:
    return {
        "date": "2026-09-03",
        "kind": "daily",
        "content": markdown,
        "download": "downloads/2026-09-03.md",
        "quality": {"status": "ok", "can_publish": True, "score": 100, "minimum_score": 92},
    }


class PublicReportContractTests(unittest.TestCase):
    def test_valid_daily_publication_passes(self) -> None:
        markdown = valid_daily()
        result = MODULE.validate_report_record(record(markdown), markdown)
        self.assertTrue(result["can_publish"], result)

    def test_download_must_match_api_content(self) -> None:
        markdown = valid_daily()
        result = MODULE.validate_report_record(record(markdown), markdown + "changed")
        self.assertFalse(result["can_publish"])
        self.assertIn("API 正文与下载 Markdown 不一致", result["errors"])

    def test_legacy_compaction_is_blocked(self) -> None:
        markdown = (
            valid_daily()
            .replace("仓位上限|信号有效期", "仓位|有效期")
            .replace("动作|放弃条件", "动作|放弃")
            .replace("|P主线|", "|P|")
            .replace(
                "行情采集→数据门禁→预测反馈→新鲜度治理→正文写作→标题门→报告审计→预测冻结",
                "mkt/fresh/writer",
            )
            .replace("今日不新开仓", "行动：交易表")
        )
        result = MODULE.validate_report_record(record(markdown), markdown)
        self.assertFalse(result["can_publish"])
        joined = "\n".join(result["errors"])
        self.assertIn("仓位上限", joined)
        self.assertIn("放弃条件", joined)
        self.assertIn("含义过度压缩", joined)
        self.assertIn("公开执行链缺少阶段", joined)
        self.assertIn("缺少明确行动", joined)


if __name__ == "__main__":
    unittest.main()
