# 棕榈油每日晨报自动任务

仅在中国期货市场交易日生成并发布当天晨报。生产目录为 `/Users/ethen/Sites/palm-oil-daily`，公网仓库为 `ethenwen0423-coder/palm-oil-daily`。不得修改数据源、预测模型、交易策略参数、调度或发布频率。

## 交易日与停止条件

1. 使用 Asia/Shanghai 当日作为 `REPORT_DATE`。
2. 先核验中国期货市场交易日；非交易日立即停止，不生成、不提交、不推送，并记录“今日非交易日，未发布”。
3. manifest 缺失、金融数据源全部失败、关键数据门禁失败、报告质量门禁失败时停止正式发布并记录原因。

## 固定调度顺序

正式生成前读取 `skills/master_report_skill/SKILL.md`，严格按以下顺序执行：

```text
market_data_skill
→ data_quality_gate_skill
→ forecast_generation_feedback
→ oil_report_freshness
→ report_writer_skill（提纲→正文）
→ headline_skill
→ report_quality_gate（高级编辑审计）
→ forecast_tracking_skill（发布前冻结）
```

当前实现映射：

```bash
cd /Users/ethen/Sites/palm-oil-daily
git pull --ff-only
python3 scripts/run_financial_skills.py --date "$REPORT_DATE" --kind daily --timeout 180
python3 skills/data_quality_gate_skill/scripts/validate_data.py \
  --manifest "source_runs/$REPORT_DATE-daily/manifest.json" --strict
python3 skills/forecast_tracking_skill/scripts/build_generation_feedback.py \
  --metrics data/forecast/metrics/latest.json \
  --review-dir data/review/daily \
  --output data/forecast/feedback/latest.json \
  --as-of "$REPORT_DATE"
```

随后完整读取：

- `source_runs/$REPORT_DATE-daily/manifest.json`
- `source_runs/$REPORT_DATE-daily/raw/` 的原始结果
- `data/forecast/feedback/latest.json`
- 最近 30 天每日复盘（通过 `review_memory.py` 的 `load_recent_reviews(days=30)`）
- `references/wechat_oil_sources.md`，仅作为动态来源线索，不把历史链接当固定引用

调用 `contract_selector_skill` 并刷新 `data/contracts/current_contracts.json`。P/Y/OI/M/RM 的 rank=1、rank=2 合约均进入分析；rank=1 为主叙事，rank=2 用于换月、资金迁移、跨期和流动性。

金融 skill 的实际成功、失败、替代来源必须写入来源说明。核心数据以交易所、官方机构、结构化行情和可复核研报交叉验证；微信/产业文章只补充叙事，不作为未经复核的行情或库存事实。

天玑增量由服务端只读采集器在报告生成前写入 `raw/futures_market_data.json` 的 `institutional_evidence`，manifest 必须列出 `htfc_tianji_read_only`。日报使用其中的 7×24 快讯、智能 K 线、研报和风向罗盘返回；仅在接口明确对应油脂品种、时间戳可用且与其他行情不冲突时，作为补充证据。不得把天玑指标或观点自行扩展成交易建议；接口不可用或无匹配品种时，在来源说明披露，不阻断其他已通过门禁的数据源。

## Writing Skill：三阶段

写作前完整读取：

- `skills/report_writer_skill/SKILL.md`
- `skills/vinson-research-writing/SKILL.md`
- 需要时读取其 `terminology.md`、`examples.md`、`anti_patterns.md`

### 1. 结构化提纲

先保存 `source_runs/$REPORT_DATE-daily/report_outline.json`，必须符合：

`skills/report_writer_skill/references/report_outline.schema.json`

提纲只保留一个基准方向、两个 Level 1 主驱动，并包含：

```text
top_call, market_stance, primary_driver, secondary_driver,
transmission_chain, expectation_vs_reality, strongest_counter_case,
invalidation_condition, trade_trigger, confirmation_condition,
stop_loss, target_range, position_limit, signal_expiry,
research_confidence, evidence_status
```

方向、触发、确认、止损、目标、仓位和有效期只允许复制既有策略结果，不得由 Writer 自行计算。Level 2/3、陈旧政策、旧库存和未核验消息不得成为今日主线。

### 2. 正文

保存为 `reports/$REPORT_DATE.md`，一级标题控制在 15 个字以内。正文（不含消息来源链接表和固定 AI 声明）控制在 **1,000–1,400 字**。

固定栏目顺序：

1. `【今日观点】`
   - 首屏 50 字左右给出 Top Call：最重要的一件事、基准方向、行动、失效条件和置信度。
   - 不堆价格，不重复交易表。
2. `【今日交易信号】`
   - 写综合评分、唯一策略方向和 P/Y/OI 强弱。
   - 用紧凑表格完整保留：方向、触发、确认、止损、目标、仓位上限、信号有效期。
3. `【核心驱动与预期差】`
   - 只写两个主驱动；每个包含快照时间、为什么重要、传导链、已定价/未定价。
   - 写出最强反证及它如何推翻基准判断。
   - 新闻仅在这里完整出现一次，不再设置新闻摘要。
4. `【关键数据与价格】`
   - 不超过 8 项，必须含 P/Y/OI、关键外盘/原油、至少一个价差和 P 关键位。
   - 每个数字带交易时段、统计日期或快照时间，并说明含义。
5. `【开盘推演】`
   - 高开、平开、低开三种情景；每种写触发 → 确认 → 动作 → 放弃条件。
   - 说明 Y/OI 同步或背离时对 P 处理的影响。
6. `【风险提示】`
   - 不超过 3 条，以失效条件表达；至少一条是最强反证。
7. `【信息来源与核验说明】`
   - 列出实际 skill、数据源、截止时间、失败项和替代来源。
   - 集中列出“需进一步核验”；只有会改变结论的缺口才能在核心正文出现。
   - 逐字写入 generation feedback 的全部 `required_report_disclosures`。
8. `【消息来源链接】`
   - 只列实际使用、核验或尝试访问的公开链接；禁止伪造 Reuters/Wind 链接。
9. `【AI观点风险提示】`
   - 固定说明 AI 研究判断不构成投资建议或交易指令，期货波动较大，客户应按自身承受能力独立决策。

共同写作规则：

- 每个事实和完整传导链只出现一次。
- 不机械添加 `【结论】`，全文最多两处。
- 新闻约 30%，分析约 70%；回答最大驱动、预期差、资金交易内容、最大风险。
- 不用模糊词替代判断；不把无法核验的信息包装为事实。
- feedback 只能降置信度、降主线等级或增加反向情景，不能上调置信度或改策略。
- 不得声称预测“准确率已改善”，除非有充足且可复现的方向命中率、Brier 和区间质量证据。

### 3. 高级编辑审计

标题必须先通过 `title-generation`，再通过 `title-quality-gate`。标题仅基于 freshness 的今日新增驱动和主线，不放交易动作或价格。

写完后运行：

```bash
python3 skills/forecast_tracking_skill/scripts/validate_report_feedback.py \
  --report "reports/$REPORT_DATE.md" \
  --feedback data/forecast/feedback/latest.json \
  --report-date "$REPORT_DATE"

python3 skills/report_writer_skill/scripts/audit_report.py \
  --report "reports/$REPORT_DATE.md" \
  --outline "source_runs/$REPORT_DATE-daily/report_outline.json" \
  --kind daily \
  --source-json "source_runs/$REPORT_DATE-daily/raw/futures_market_data.json" \
  --feedback data/forecast/feedback/latest.json \
  --output "source_runs/$REPORT_DATE-daily/report_quality.json" \
  --min-score 92
```

低于 92 分或出现以下任一情况均不得发布：关键行情/价位错误、主线使用陈旧 Level 2/3 信息、预测披露缺失、交易方向冲突、必需栏目或提纲缺失、首屏 Top Call 未同时写明基准方向/行动/失效条件/置信度、主驱动未明确排序为“主驱动一/主驱动二”、开盘三情景或 Y/OI 对 P 的同步/背离处理缺失。不得以“栏目齐全、数字正确”代替研究判断。来源口径不同但可解释时可记 `WARN`，不得放过关键数字错误。

发布前再按 `skills/vinson-research-writing/checklist.md` 自检，并完成 forecast tracking 的发布前冻结审计，禁止使用当日未来或收盘后数据。

## 发布与验证

门禁全部通过后执行：

```bash
bash scripts/deploy_report.sh
```

最后检查 `git status`、推送结果、GitHub Pages、`index.html`、`data/reports.js`、`data/version.js`、当天 Markdown 和下载文件。脚本提交范围仅限既定报告发布文件，不得夹带其他工作树修改。
