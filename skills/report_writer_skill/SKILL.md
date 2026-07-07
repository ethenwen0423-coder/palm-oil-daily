---
name: report-writer-skill
description: Dedicated report writer skill implementing the report_writer_skill interface for oil and fats morning reports. Use after market_data_skill and oil_report_freshness, and before headline_skill, when Codex needs to write or rewrite the body of palm-oil/oil-fats daily or weekly reports with higher research quality without increasing length. It upgrades report body writing from information summary to institutional research analysis using driver ranking, why-based reasoning, transmission chains, expectation-vs-reality checks, invalidation conditions, and confidence ratings.
---

# Skill: report_writer_skill

## Positioning

Use this skill to write the report body only.

Do not generate `Headline` or `Subheadline`. Do not fetch market data. Do not override `oil_report_freshness`. Do not add new report sections unless the existing structure already requires them.

Base writing style still follows `../vinson-research-writing/SKILL.md`, but this skill is stricter for oil/fats reports.

## Core Objective

Upgrade the body from `资讯汇总` to `研究分析` while keeping the report length stable.

Write closer to domestic top-tier futures research morning notes:

- 中信期货
- 永安期货
- 国投安信期货
- 浙商期货
- 南华期货

Principle:

```text
研究 > 新闻
分析 > 罗列
逻辑 > 数据
结论 > 信息
```

## Required Inputs

Before writing, use only:

1. `market_data_skill` output or equivalent called data source results.
2. `oil_report_freshness` governed output.
3. Existing report structure requirements.

Do not re-upgrade old news, weekly inventory, old policy, old research reports, or unverifiable rumors into today's driver.

## Writing Algorithm

For each body module, run this sequence:

1. Select the core view.
2. Rank drivers by impact.
3. Explain why the view holds.
4. Build the transmission chain.
5. Separate expectation from reality.
6. State invalidation conditions.
7. Assign confidence.
8. Compress repeated statements instead of adding length.

## Driver Ranking

Before writing body paragraphs, rank drivers by impact:

```text
★★★★★  Main driver
★★★★☆  Secondary driver
★★★☆☆  Supporting variable
★★☆☆☆  Background
★☆☆☆☆  Stale or low-impact background
```

Body logic must focus on the top two drivers.

Lower-ranked items may appear only as background or risk context. Do not let them become the mainline.

## Why Requirement

Every view must answer `为什么`.

Use this compact pattern:

```markdown
观点：...
原因：1）...；2）...；3）...
总结：...
```

Do not write only a result, such as `P 强于 Y/OI`. Explain the cause:

- relative driver strength
- cross-market linkage
- inventory or basis pressure
- flow/position behavior
- expectation-vs-reality mismatch

## Transmission Chain

Important views must include a mechanism, not a one-step claim.

Example:

```text
原油下跌
↓
生柴利润压缩
↓
POGO估值支撑减弱
↓
棕榈油需求预期降温
↓
P承压
```

Use short inline chains when space is limited:

`原油 → 生柴利润 → POGO估值 → 需求预期 → P承压`

## Expectation Vs Reality

Every core section must identify whether the market is trading expectation or reality.

Use:

```text
预期：...
现实：...
差异：...
结论：...
```

Explain why price has or has not fully priced the expectation.

Example:

`市场仍交易印尼政策预期，但国内库存高、基差弱，说明现实需求尚未验证预期，价格更容易走震荡而非单边。`

## Invalidation Thinking

Each core view must include what would change the research conclusion.

Do not turn invalidation into trading advice. Only state research conditions.

Examples:

- `若 FCPO 重新放量大涨，当前震荡判断需要上修。`
- `若原油重新突破关键位置，生柴估值修复逻辑需要重新评估。`
- `若库存连续去化，现实压力对 P 的压制将减弱。`

## Confidence Rating

Each core view must include confidence:

```text
置信度：★★★★★ / ★★★★☆ / ★★★☆☆ / ★★☆☆☆ / ★☆☆☆☆
```

Calculate confidence from:

- data quality
- information freshness
- source reliability
- logic consistency

Guide:

- `★★★★★`: fresh data, reliable source, clear driver, consistent chain
- `★★★★☆`: mostly fresh and reliable, minor uncertainty
- `★★★☆☆`: mixed data or partial confirmation
- `★★☆☆☆`: old data, weak source, or conflicting signals
- `★☆☆☆☆`: unverifiable or only background

## No Length Increase

Do not add large new sections.

Integrate the upgraded analysis into existing modules:

- `今日观点`
- `今日交易重点`
- `开盘推演`
- `风险提示`
- weekly equivalents

Use replacement, not expansion:

- replace news lists with driver ranking
- replace repeated claims with one logic chain
- replace generic risk with invalidation conditions
- replace vague confidence with explicit stars

## Repetition Control

Do not repeat the same view across sections.

Use one concise structure:

```text
观点
↓
三个原因
↓
一句总结
```

If the same logic appears again, refer to it briefly and add only new information.

## Required Module Behavior

### 今日观点

Must contain:

- one core view
- top two drivers
- expectation-vs-reality statement
- confidence rating

No more than the existing length target.

### 今日交易重点

Must contain:

- driver ranking by impact
- why the top two drivers matter
- one transmission chain
- one invalidation condition

### 开盘推演

Must explain why each scenario would occur.

Do not only list high/open/low scenarios. Each scenario must link trigger → mechanism → research conclusion.

### 风险提示

Use risks as invalidation conditions, not generic warnings.

Each risk must answer:

- what changes
- why it changes the conclusion
- which current view it challenges

## Hard Prohibitions

- Do not write a paragraph that only lists news.
- Do not write a view without reasons.
- Do not write `原油跌，所以P跌` without the transmission chain.
- Do not let background items become main drivers.
- Do not add new first-level sections to satisfy this skill.
- Do not increase report length by adding repeated explanation.
- Do not write unverifiable information as confirmed fact.
- Do not let `headline_skill` responsibilities enter the body writer.

## Output Check

Before returning body text, verify:

- Each core view answers why.
- Driver ranking exists and the body focuses on the top two drivers.
- Important views contain a transmission chain.
- Expectation and reality are separated where the market is trading a theme.
- Invalidation conditions are stated without becoming trading advice.
- Confidence ratings are included for core views.
- Level 2 and non-upgraded Level 3 information remains background.
- Unverifiable information is marked as unconfirmed.
- No new first-level sections were added only to satisfy this skill.
- Repeated news or repeated logic was compressed.
