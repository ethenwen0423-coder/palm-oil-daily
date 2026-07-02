# Changelog

## v1.0.0 - 2026-07-02

### Added

- 从 `title-quality-gate` 拆分出独立 `title-generation` Skill。
- 明确本 Skill 只负责生成 `Headline`、`Subheadline`、`Report Title`、`One Sentence Summary`。
- 建立市场主线识别流程：今天市场交易什么、相比昨天变化是什么、昨天主线是否仍然成立。
- 保留“标题忠于市场主线，不忠于新鲜感”的生成原则。
- 明确生成完成后必须交由 `title-quality-gate` 检查。
