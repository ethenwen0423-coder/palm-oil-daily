---
name: oil-report-freshness
description: Information-governance skill for oil and fats morning reports. Use when Codex needs to run oil_report_freshness before report writing: classify market inputs by freshness, source reliability, verification status, and eligibility to become today's market mainline; produce governed inputs for report_writer. This skill is not for Headline, Subheadline, body writing, trading advice, technical analysis, or final title/style quality checks.
---

# Oil Report Freshness

## Purpose

Use this skill before `report_writer` writes an oil/fats morning report.

The job is information governance only:

- judge freshness
- classify information layers
- check source reliability
- flag unverifiable claims
- decide whether a claim may become today's mainline
- output structured inputs for `report_writer`

Do not write the report body. Do not generate `Headline` or `Subheadline`. Do not give trading advice or technical analysis. Headline generation belongs to `headline_skill`.

Core principle:

> Today's information decides today's view. Yesterday's information explains today's background. Historical information must not pretend to be today's driver.

## Information Levels

Classify every input before using it.

| Level | Name | Examples | Allowed use |
| --- | --- | --- | --- |
| Level 1 | High Freshness / 今日新增信息 | P/Y/OI night session, FCPO, CBOT, WTI/Brent, dollar index, Treasury yields, latest news, latest futures-company daily report, latest shipment data, latest weather, latest macro event | May support today's view, Headline basis, and the first logic of the body |
| Level 2 | Medium Freshness / 背景信息 | Weekly stocks, basis, port stocks, import margin, crush margin, weekly supply-demand | Background only; must include statistical date and update time; must not become today's mainline |
| Level 3 | Low Freshness / 事件信息 | B50, MPOB, USDA, Canada acreage, policy, export tax | Background by default; upgrade to Level 1 only if there is a confirmed new update within the latest 24 hours |

## Governance Chain

Run this chain for every item:

1. Was it newly updated in the latest 24 hours?
2. Does it have a reliable source?
3. Does it affect today's trading or pricing?
4. Is it allowed to become today's mainline?

If any answer is no or cannot be verified, forbid the item from becoming today's mainline.

Use `需进一步核验` when the source, timestamp, or fact cannot be confirmed. Do not guess.

## Automatic Corrections

Apply these corrections before output:

- If old information is written as today's mainline, downgrade it to background.
- If weekly inventory, basis, port stocks, import margin, crush margin, or weekly supply-demand is written as today's driver, move it to background and require date/update-time labels.
- If policy or event information has no new 24-hour update, rewrite it as: `市场仍关注……今日暂无新增进展。`
- If a claim is unverifiable, move it to `待核验信息` and state that it must not be written as confirmed fact.
- If a low-freshness item cannot be safely corrected, output `需要report_writer重新生成对应段落`.

## Mainline Eligibility

Only Level 1 items may form `今日主线建议`.

Level 2 items may explain the background behind Level 1 moves, but they cannot be the mainline.

Level 3 items may become the mainline only when both conditions hold:

- there is a confirmed new update in the latest 24 hours
- the update directly affects today's trading or pricing

If today's Level 1 evidence is mixed or weak, say `主线不清，偏轮动` rather than forcing a mainline.

## Required Output

Return exactly these sections in this order:

```markdown
① 今日新增驱动
- ...

② 今日主线建议
...

③ 延续性背景
- ...（统计日期：...；更新时间：...）

④ 风险因素
- ...

⑤ 不允许作为主线的信息
- ...

⑥ 待核验信息
- ...（不得写成确定事实；需进一步核验）

⑦ 信息新鲜度表
| 信息 | Level | 是否24小时新增 | 来源/可核验性 | 是否影响今日交易 | 是否允许成为主线 | 处理意见 |
| --- | --- | --- | --- | --- | --- | --- |
| ... | ... | ... | ... | ... | ... | ... |
```

Rules for this output:

- `今日新增驱动` contains only truly new Level 1 information.
- `今日主线建议` is a mainline suggestion only, not a Headline and not body copy.
- `延续性背景` contains Level 2 and non-upgraded Level 3 information.
- `不允许作为主线的信息` explicitly lists weekly data, old news, old policy, unverified claims, and stale event narratives that must not be framed as today's driver.
- `待核验信息` must not be phrased as confirmed fact.
- `信息新鲜度表` must make the decision path auditable.

## Pre-Output Checklist

Before returning, check:

- Is the suggested mainline based on Level 1 information?
- Did any Level 2 item get incorrectly used as today's mainline?
- Did any Level 3 item get upgraded without a confirmed 24-hour update?
- Are unverifiable items clearly marked?
- Are old news and stale policy items downgraded?
- Is there repeated narrative that should be merged?
- Are there source conflicts?

If a problem can be corrected, correct it before output. If it cannot be corrected, state `需要report_writer重新生成对应段落` and identify the affected section.

## Downstream Contract

`report_writer` may use only the governed content returned by this skill.

`report_writer` must not re-upgrade Level 2 or non-upgraded Level 3 information into today's mainline, today's driver, or today's largest impact.
