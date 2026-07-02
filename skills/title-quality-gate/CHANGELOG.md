# Changelog

## v2.0.0 - 2026-07-02

### Changed

- 按单一职责原则重构标题系统。
- 将标题生成职责迁移到独立 `title-generation` Skill。
- `title-quality-gate` 只保留标题检查职责，不再生成或改写标题。
- 检查失败时，返回失败项并要求回到 `title-generation` 重新生成。
- 新增 `README.md`，明确与 `title-generation` 的职责边界和调用顺序。

## v1.1.0 - 2026-07-02

### Changed

- 优化 Headline 生成逻辑：由“避免重复”改为“表达市场主线”。
- 明确 Headline 的目标不是每天都不同，而是准确表达当天市场最重要的主线。
- 新增生成流程：先识别今天市场交易什么、相比昨天最大变化是什么、昨天主线是否仍然成立。
- 允许市场主线不变时，Headline 与昨天保持相似。
- 明确只有政策变化、库存变化、资金风格变化、外盘主线变化、市场情绪明显变化等新驱动出现时，才更新 Headline。
- 新增质量检查：识别是否为了和昨天不同而强行修改标题。
- 新增 `examples.md` 和 `checklist.md`，用于长期维护标题质量门。

## v1.0.0 - 2026-06-30

### Added

- 创建 `title-quality-gate` Skill。
- 建立 Headline、Subheadline、Trading Plan 的职责边界。
- 禁止 Headline 和 Subheadline 承载具体交易动作。
- 建立通过/需重写的输出规则。
