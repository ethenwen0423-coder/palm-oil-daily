---
name: vinson-research-writing
description: Use for Chinese financial research writing and editing, including palm-oil daily or weekly reports, A-share morning notes, market commentary, industry reports, website articles, GitHub Pages content, customer pushes, PPT copy, and Markdown research reports. Apply by default when improving readability, structure, tone, terminology, or institutional research style.
---

# Vinson Research Writing Standard

## When To Use

Use this Skill for all research-facing writing in this project:

- 棕榈油日报、周报
- A股晨报、市场点评、行业专题
- 网站文章、GitHub Pages 内容
- 客户推送、PPT 文案
- Markdown 研究报告

This Skill controls writing quality only. Do not change data sources, business logic, trading strategy, scheduling, or publishing logic because of this Skill.

## Required Reading

For any report generation or rewrite:

1. Read this `SKILL.md`.
2. Read `checklist.md` before final output.
3. Read `terminology.md` when financial terms, oilseed terms, or web copy terms appear.
4. Read `examples.md` when rewriting weak prose or improving readability.
5. Read `anti_patterns.md` when text feels like AI output, news recap, or loose analysis.

## Writing Objective

Write like a domestic top-tier sell-side or futures research team:

- 中信期货
- 永安期货
- 银河期货
- 国泰君安期货
- 华泰期货
- 中粮期货
- Bloomberg Intelligence
- Reuters Research

Do not imitate WeChat self-media, marketing accounts, Zhihu, Xiaohongshu, or generic AI articles.

The final text must be professional, restrained, logically rigorous, opinionated, dense, readable, and useful for institutional clients.

## Default Language

Use simplified Chinese unless the user explicitly requests English.

Keep English only for established names or technical terms such as Bloomberg, Reuters, TradingView, API, Markdown, HTML, CSS, React, Next.js, and TypeScript.

Financial analysis should use professional Chinese.

## Core Principles

1. Help clients make decisions. Do not merely help them read news.
2. Put opinion before news.
3. Use the structure: 观点 -> 数据 -> 逻辑 -> 交易建议.
4. Every analysis must answer: 为什么、意味着什么、怎么交易.
5. News should be about 30%; analysis should be about 70%.

## Required Structure

For research reports, the first paragraph must give the view directly. No warm-up, no broad background, no delayed conclusion.

For each important point, follow:

1. 事实
2. 解释
3. 市场如何交易
4. 交易建议
5. 失效条件

Explain whether the market is trading expectation or reality.

## Sentence And Paragraph Rules

- One paragraph, one point.
- Each paragraph should usually be no more than 3 sentences.
- Prefer 20-30 Chinese characters per sentence when possible.
- Use short, active sentences.
- Delete sentences that do not change the reader's decision.

Avoid repeated or vague connectors:

- 总体来看
- 综合来看
- 可以看到
- 值得注意的是
- 建议关注
- 后续仍需关注
- 市场认为
- 从目前来看
- 在此背景下
- 预计
- 可能
- 或将

If these terms are necessary, use them sparingly.

## Data Explanation Rule

Never list data without interpretation.

For every important data point, explain:

- 为什么重要
- 为什么变化
- 市场怎么看
- 如何影响行情
- 如何影响交易

If a data point cannot support a trading decision, remove it or move it to a compact table.

## Markdown Rules

- Use exactly one H1.
- Use H2 for main sections.
- Use H3 only when needed.
- Do not exceed H3.
- Use Markdown tables when comparing three or more numbers, views, risks, or trading plans.
- Avoid continuous long paragraphs.
- Keep enough whitespace for scanning.

## Source Links And AI Risk Note

Research reports must end with source transparency:

1. Add a final or near-final H2 section named `【消息来源链接】`.
2. Use a concise Markdown table with source name, purpose, and link.
3. Include only sources actually used, checked, or attempted in that report.
4. If a terminal source such as Reuters or Wind is unavailable, state that clearly and do not add a fake link.
5. After source links, add `【AI观点风险提示】`.
6. State that the report is AI-generated from public information, configured skills, and available data at generation time.
7. State that it represents only AI model output and research judgment, not investment advice or trading instruction.
8. Keep the note concise and restrained.

Preferred wording:

> 本报告由 AI 基于公开信息、已调用数据源和既定研究框架生成，仅代表模型在生成时点的研究判断，不构成投资建议或交易指令。期货价格波动较大，请结合自身风险承受能力独立决策。

## Web Copy Rules

When writing HTML, CSS, React, or Next.js copy and layout text:

- Chinese font preference: HarmonyOS Sans, PingFang SC, 思源黑体.
- English font preference: Inter.
- Numeric font preference: DIN.
- H1: 32px.
- H2: 24px.
- H3: 18px.
- Body: 16px.
- Line height: 1.7.
- Card radius: 16px.
- Style reference: Bloomberg, TradingView, Apple official site.
- Avoid blog style, default GitHub Pages style, and WeChat article style.

For Markdown outputs, do not output font CSS. Maintain hierarchy, tables, whitespace, and reading flow.

## Final Pass

Before finalizing, run the checklist in `checklist.md`. If any item fails, rewrite the failing section before publishing.
