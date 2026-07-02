# Title Generation

`title-generation` 只负责生成研究标题，不负责检查。

它生成四类内容：

- `Headline`
- `Subheadline`
- `Report Title`
- `One Sentence Summary`

核心原则：标题忠于市场主线，不为了避免重复而制造新观点。

标准调用顺序：

1. 调用 `title-generation` 生成标题。
2. 调用 `title-quality-gate` 检查标题。
3. 如果检查失败，返回 `title-generation` 重新生成。

职责边界：

- `title-generation`：总结市场、提炼主线、生成标题。
- `title-quality-gate`：检查标题是否合格，不生成标题。
