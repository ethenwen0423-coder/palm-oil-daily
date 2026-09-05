---
name: report-writer-skill
description: Write or revise governed Chinese palm-oil and oil-fats daily or weekly reports through a structured outline, bounded draft, and deterministic editorial audit. Use after market data, data quality, forecast feedback, and freshness governance, and before headline generation and publication.
---

# report_writer_skill

## Scope

Write the report body. Do not fetch data, calculate strategy levels, change model or strategy parameters, invent a source, or generate `Headline` / `Subheadline`.

Inputs must already be governed by:

1. `market_data_skill` and its manifest/raw outputs;
2. `data_quality_gate_skill`;
3. `oil_report_freshness`;
4. for daily reports, `data/forecast/feedback/latest.json`;
5. the existing deterministic trading-strategy result.

Use `../vinson-research-writing/SKILL.md` for general style. This skill controls the oil-report research contract.

## Three-stage contract

### Stage 1: research outline

Before prose, create `source_runs/<date>-<kind>/report_outline.json`. It must validate against `references/report_outline.schema.json`.

The outline contains:

```text
top_call
market_stance
primary_driver
secondary_driver
transmission_chain
expectation_vs_reality
strongest_counter_case
invalidation_condition
trade_trigger
confirmation_condition
stop_loss
target_range
position_limit
signal_expiry
research_confidence
evidence_status
```

Rules:

- Choose exactly one baseline stance and at most two main drivers.
- Both main drivers must be fresh, governed `Level 1` evidence. Level 2/3 may appear only as background or risk.
- `strongest_counter_case` must be capable of explaining why the baseline view may be wrong.
- Direction, trigger, confirmation, stop, target, position, and expiry must come from existing strategy/data outputs. The writer must not create or recalculate them.
- Every driver records its source and `as_of` / snapshot time.
- Put unverifiable information only in `evidence_status.needs_verification`. Promote it to the body only if it can change the conclusion.
- The outline is an internal audit artifact, not a new visible report section.

For weekly reports, reason internally in the order `供给 → 需求 → 价格与资金 → 策略`, but expose only the conclusions with the greatest impact.

### Stage 2: bounded draft

Daily body budget: **2,400–3,200 Chinese characters**. Broad coverage establishes the research context; only the two governed Level 1 drivers may determine the core view.

Daily headings, in order:

1. `今日观点`
2. `今日交易信号`
3. `核心驱动与预期差`
4. `盘前市场全景`
5. `关键数据与价格`
6. `价格预测与验证`
7. `开盘推演`
8. `风险提示`
9. `信息来源与核验说明`
10. `消息来源链接`
11. `AI观点风险提示`

Weekly body budget: **1,600–2,000 Chinese characters**.

Weekly headings, in order:

1. `一句话核心观点`
2. `本周验证与预期差`
3. `核心数据变化`
4. `下周主线与事件`
5. `周一开盘推演`
6. `交易计划`
7. `风险提示`
8. `信息来源与核验说明`
9. `消息来源链接`
10. `AI观点风险提示`

The budget excludes the message-source link table and the fixed AI disclaimer.

Common rules:

- Lead with one `Top Call`: conclusion, action, and invalidation condition.
- Use only the two ranked drivers. Explain `why`, one transmission chain, and expectation versus reality.
- State the strongest counter-case without weakening it into a generic disclaimer.
- Each fact and each transmission chain appears in full only once. Later references add only new information.
- Do not mechanically append `【结论】`; use it at most twice in the whole report.
- Every numeric fact states its statistics date, snapshot time, or trading-session basis.
- Consolidate `需进一步核验` items in `信息来源与核验说明`; mention them in the core body only when they can change the view.
- Preserve the complete trade plan: direction, trigger, confirmation, stop, target, position limit, and signal expiry.
- P/Y/OI coverage is mandatory. Weekly reports also state relative strength and the role of Y/OI in the P thesis.
- Daily and weekly P/Y/OI execution plans use one Markdown table with the exact contract columns `品种 | 方向 | 触发 | 确认 | 止损 | 目标 | 仓位上限 | 信号有效期`; every product row must be complete. When a deterministic input omits a value, write the governed no-trade fallback instead of leaving a cell blank or inventing a number.
- Daily key data use a Markdown table with `指标 | 数值 | 时点 | 含义`; include 10–14 rows covering P/Y/OI, available rank-2 contracts, an external or crude-oil value, both soybean-palm and rapeseed-soybean-oil spreads, at least two origin/official supply-demand metrics, at least one domestic warehouse-receipt/inventory/basis/margin observation, and a P stop or target level from the outline.
- Daily pre-market panorama uses `维度 | 已验证事实 | 对P/Y/OI影响 | 盘中验证信号`; include exactly one row for each of 海外盘面、美豆与豆油、棕榈油产地、菜籽链、能源与生柴、国内现货与库存、合约结构与资金、天气物流与政策. At least five rows must contain both an exact number and a date/snapshot time. When evidence is unavailable, say `证据缺口`, write `不计入方向` in the impact cell, and state the evidence needed; never fill the gap with generic prose. Use real rank-1/rank-2 delivery contracts when present; never substitute a continuous contract. Follow the table with one 120–180-character synthesis naming `当前定价主线`, `最大预期差`, and `盘中验证优先级` without repeating the rows.
- Daily price forecast uses `品种 | 参考价 | 基准判断 | 下沿观察 | 上沿观察 | 上修触发 | 下修/失效 | 置信度` with complete P/Y/OI rows. Every numeric boundary and direction must come from the structured market record or existing `strategy_recommendation`; confidence cannot exceed generation feedback. Treat the table as a conditional pre-market forecast, not a promised intraday range.
- Immediately below the daily price forecast, state that the AI-generated forecast is based on the listed sources and fixed model, does not represent any source's official position, is not investment advice, and must be independently verified.
- Daily opening scenarios use a Markdown table with `情景 | 触发 | 确认 | 动作 | 放弃条件` and complete high/flat/low rows. Weekly scenarios add `概率` and complete high-open-rise/high-open-range/high-open-fall/low-open rows. Each scenario states how Y/OI confirmation or divergence changes the P action.
- Weekly core data use `指标 | 数值 | 统计时间 | 变化 | 含义` and include P/Y/OI plus both soybean-palm and rapeseed-soybean-oil spreads. The event table uses `日期 | 事件 | 重要性 | 触发条件` and covers Monday through Friday without blank placeholders.
- `信息来源与核验说明` explicitly labels actual skills, data sources, cutoff time, failed items, and replacement sources. Write `无` when a field is empty; do not omit the field.
- Copy every daily forecast feedback `required_report_disclosures` sentence exactly into `信息来源与核验说明`.
- Forecast feedback may only reduce confidence, downgrade a product, or add a counter-scenario. It cannot boost confidence or replace current evidence.

### Stage 3: senior editor audit

The audit is read-only with respect to the report:

```bash
python3 skills/report_writer_skill/scripts/audit_report.py \
  --report "reports/<date>.md" \
  --outline "source_runs/<date>-daily/report_outline.json" \
  --kind daily \
  --source-json "source_runs/<date>-daily/raw/futures_market_data.json" \
  --feedback data/forecast/feedback/latest.json \
  --output "source_runs/<date>-daily/report_quality.json" \
  --min-score 92
```

Use `--kind weekend` and the weekend source-run paths for a weekly report.

The editor checks:

- governed evidence supports the view;
- top call, stance, score, trade plan, opening scenarios, and risks agree;
- Level 2/3 evidence was not promoted into the mainline;
- news, causal chains, and conclusions are not repeated;
- critical prices, changes, spreads, and outline trade levels are fully checked;
- at least three other numeric facts are sampled with a fixed seed;
- daily forecast disclosures are present exactly;
- source/snapshot times and evidence gaps are disclosed;
- the quality score is at least 92/100. A score cannot compensate for a missing actionable Top Call, ranked two-driver analysis, or complete opening scenarios.

Scoring:

| Dimension | Points |
|---|---:|
| Data accuracy | 20 |
| View/trade-plan consistency | 20 |
| Freshness and source state | 15 |
| Causal chain and expectation gap | 15 |
| Risk and invalidation | 10 |
| Structural completeness | 10 |
| Concision and repetition control | 10 |

Regardless of total score, publication is blocked by:

- a critical market or trade-level mismatch;
- stale Level 2/3 evidence used as a main driver;
- a missing required forecast disclosure;
- contradictory baseline/trading directions;
- a missing required report section or invalid outline;
- a first-screen Top Call that omits the baseline stance, action, invalidation condition, or research confidence;
- an unranked driver section, incomplete opening scenarios, or (for weekly reports) an event calendar that does not cover Monday through Friday.
- an incomplete P/Y/OI execution table, unstructured key-data/scenario table, fewer than seven auditable auxiliary numeric facts, or a missing source-audit field.
- a missing eight-dimension pre-market panorama, fewer than five quantitative/time-bounded panorama rows, an evidence gap used directionally, a key-data table with fewer than ten rows or without origin-supply/domestic-physical evidence, or a price-forecast row whose reference price/watch boundaries do not match the governed source data.

`WARN` is appropriate for an explainable source-method difference. Do not turn a critical numeric error into a tolerance warning.

## Writing patterns

Compact causal pattern:

```text
事实（含时间） → 机制 → P/Y/OI影响 → 已定价/未定价 → 结论
```

Counter-case pattern:

```text
基准判断：...
最强反证：...
确认条件：...
失效条件：...
```

Trade pattern:

```text
方向 | 触发 | 确认 | 止损 | 目标 | 仓位上限 | 有效期
```

## Prohibitions

- No paragraph that only lists news.
- No view without a mechanism.
- No claim such as `原油跌，所以P跌` without the intermediate transmission.
- No stale policy, old inventory, research note, or rumor as today's mainline.
- No invented number, price level, probability, position, or source.
- No statement that feedback has improved accuracy without sufficient reproducible directional accuracy, Brier score, and interval evidence.
- No silent change to data source, forecast model, strategy, schedule, template, or publication frequency.

## Completion check

Return the draft only after:

- outline schema validation succeeds;
- only one stance and two drivers remain;
- the strongest counter-case and invalidation are explicit;
- every body number has an as-of basis;
- all trade-plan fields come from deterministic inputs;
- repeated facts/chains have been compressed;
- the deterministic audit returns `can_publish=true`.
