# 棕榈油周报与周一推演自动任务

每周日 21:15 生成并发布周报。生产目录为 `/Users/ethen/Sites/palm-oil-daily`，文件为 `reports/YYYY-MM-DD-weekend.md`。一级标题使用“MM月DD日周报”，不超过 15 个字。不得改变数据源、预测模型、交易策略参数、调度或发布频率。

生产服务器由 `server/run_research_agent.py` 复用与静态站一致的受管控链路，
并在 `source_runs/$REPORT_DATE-weekend/skill_chain.json` 留下 market data、
data quality、freshness、writer、headline 和 report quality 各阶段证据。
周报不得只消费压缩行情快照：必须读取跨站新闻/研报事件、华泰天玑增量、
上一期报告与上一期 source snapshot，完成逐条验证后再生成静态 Markdown、
`data/reports.json`、`data/reports.js`、下载文件与报告索引。

下一交易日若因中国期货市场节假日不是周一，明确写“下一交易日待交易所日历确认/顺延”。

## 固定调度顺序

正式生成前读取 `skills/master_report_skill/SKILL.md`，按以下顺序执行：

```text
market_data_skill
→ data_quality_gate_skill
→ oil_report_freshness
→ report_writer_skill（提纲→正文）
→ headline_skill
→ report_quality_gate（高级编辑审计）
```

执行：

```bash
cd /Users/ethen/Sites/palm-oil-daily
git pull --ff-only
python3 scripts/run_financial_skills.py --date "$REPORT_DATE" --kind weekend --timeout 90
python3 skills/data_quality_gate_skill/scripts/validate_data.py \
  --manifest "source_runs/$REPORT_DATE-weekend/manifest.json" --strict
```

读取 manifest 和 `raw/` 全部实际结果。manifest 缺失、全部金融源失败或关键数据门禁失败时停止发布。

实际成功、失败、替代来源和截止时间必须记录。核心数据使用 DCE、MPOB/MPOA/ITS、USDA、CME/ICE、东方财富、问财、期货公司研报等可复核来源；微信/产业文章只补充叙事，不把其中数字直接包装为已核实事实。Reuters/Wind 不可访问时只说明，不伪造链接。

天玑增量由服务端只读采集器在报告生成前写入 `raw/futures_market_data.weekly_compatible.json` 的 `institutional_evidence`，manifest 必须列出 `htfc_tianji_read_only`。周报使用其中的 7×24 快讯、智能 K 线、研报和风向罗盘返回；仅使用接口明确返回、可匹配油脂品种且有有效时间戳的字段。指标和快讯只用于验证周内驱动、资金/趋势背景或风险反证，不能替代交易所结算、官方供需或既有策略，也不得由 Writer 推导新的交易指令。接口失败、权限不足或无匹配品种时必须披露，但不阻断其他通过门禁的数据源。

## Writing Skill：三阶段

写作前完整读取：

- `skills/report_writer_skill/SKILL.md`
- `skills/vinson-research-writing/SKILL.md`
- 需要时读取其术语、示例和反例

### 1. 结构化提纲

先保存 `source_runs/$REPORT_DATE-weekend/report_outline.json`，必须符合：

`skills/report_writer_skill/references/report_outline.schema.json`

提纲仅保留一个基准方向和两个 Level 1 主驱动，完整包含 Top Call、预期差、最强反证、失效条件和既有策略提供的触发/确认/止损/目标/仓位/有效期。禁止由 Writer 创造交易数字。

内部研究按 `供给 → 需求 → 价格与资金 → 策略` 整理，可在 `supply_demand_framework` 留审计记录；最终正文只展示影响最大的结论，不新增客户可见栏目。

### 2. 正文

正文（不含消息来源链接表和固定 AI 声明）控制在 **1,600–2,000 字**，固定栏目顺序：

1. `【一句话核心观点】`
   - 首屏给出唯一 Top Call、下周行动、失效条件和置信度。
   - 包含 P 主线与 Y/OI 的共振或分化，不写泛化标题。
2. `【本周验证与预期差】`
   - 先复核上周判断：哪些兑现、哪些落空、错在何处。
   - 只写两个主驱动，每个包含时间、机制、盘面定价程度。
   - 写最强反证；新闻只在这里完整出现一次。
3. `【核心数据变化】`
   - 不超过 10 项；必须含 P/Y/OI、至少两个可核验的价差或相对价值指标。
   - 使用“指标、数值、统计时间、变化、含义”五列表格；每项写统计时间、变化、含义，不只罗列数字。
4. `【下周主线与事件】`
   - 将供给、需求、价格资金的结论压缩为下周唯一主线。
   - 说明 P/Y/OI 强弱排序和排序条件。
   - 使用“日期、事件、重要性、触发条件”四列表格，逐行覆盖周一至周五；没有确定事件不得编造。
5. `【周一开盘推演】`
   - 使用“情景、概率、触发、确认、动作、放弃条件”六列表格，完整列出高开高走、高开震荡、高开回落、低开四种情景。
   - 概率来自既有模型/规则，不得由 Writer任意生成；写触发、确认、应对、放弃条件。
   - 写清 Y/OI 同步或背离时对 P 的调整。
6. `【交易计划】`
   - 使用一张表格对 P/Y/OI 分别写品种、方向、触发、确认、止损、目标、仓位上限和信号有效期；三行均不得空缺。
   - 方案必须覆盖可执行、不可追、观望三种状态。
7. `【风险提示】`
   - 不超过 3 条，用失效条件表达；至少包含最强反证及 Y/OI 对 P 结论的扰动。
8. `【信息来源与核验说明】`
   - 明确标注实际 skill、数据源、截止时间、失败项和替代来源五个字段；没有失败或替代时写“无”，不得省略字段。
   - “需进一步核验”集中在此；只在会改变结论时进入核心正文。
9. `【消息来源链接】`
   - 只列实际使用、核验或尝试访问的公开链接。
10. `【AI观点风险提示】`
   - 固定说明 AI 研究判断不构成投资建议或交易指令，期货波动较大，客户应独立决策。

共同规则：

- 每个事实和传导链只完整出现一次。
- 不机械添加 `【结论】`，全文最多两处。
- 主驱动只能来自 freshness 治理后的 Level 1 信息；Level 2/3、旧政策、旧库存、传言只能作背景/风险。
- P 为主线，但必须系统覆盖 Y/OI；豆油包含外盘豆油和压榨/到港/库存或生柴，菜油包含菜籽/进口成本与到港/库存/基差。
- 每个正文数字均附统计日期、交易时段或快照时间。
- 无法核验的事实写“需进一步核验”，禁止伪装成结论。
- 新闻约 30%，分析约 70%；重点解释为什么、定价程度、预期差和如何交易。

### 3. 高级编辑审计

标题先通过 `title-generation`，再通过 `title-quality-gate`。标题仅来自最近 24 小时或周末新增的可核验主驱动，不放价格和交易动作。

如存在 `futures_market_data.weekly_compatible.json`，审计优先使用该文件；否则使用 `futures_market_data.json`：

```bash
python3 skills/report_writer_skill/scripts/audit_report.py \
  --report "reports/$REPORT_DATE-weekend.md" \
  --outline "source_runs/$REPORT_DATE-weekend/report_outline.json" \
  --kind weekend \
  --source-json "source_runs/$REPORT_DATE-weekend/raw/futures_market_data.weekly_compatible.json" \
  --output "source_runs/$REPORT_DATE-weekend/report_quality.json" \
  --min-score 92
```

低于 92 分或出现任一一票否决项均不得发布：关键行情/价位错误、Level 2/3 成为主线、方向冲突、必需栏目/提纲缺失、首屏 Top Call 未同时写明基准方向/行动/失效条件/置信度、主驱动未明确排序为“主驱动一/主驱动二”、四种周一情景或 Y/OI 对 P 的同步/背离处理缺失、下周事件未覆盖周一至周五。不得以“栏目齐全、数字正确”代替研究判断。关键数字全量复核，其他数字按固定种子至少抽取 3 项。来源口径差异可解释时记 `WARN`。

最后按 `skills/vinson-research-writing/checklist.md` 自检。

## 发布与验证

门禁全部通过后执行：

```bash
bash scripts/deploy_report.sh
```

检查 `git status`、推送结果、GitHub Pages、`index.html`、`data/reports.js`、`data/version.js`、周报 Markdown 和下载文件。不得夹带工作树其他修改。
