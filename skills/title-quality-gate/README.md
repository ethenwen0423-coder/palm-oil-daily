# Title Quality Gate

`title-quality-gate` 只负责检查标题，不负责生成标题。

它检查：

- `Headline` 是否表达市场主线
- `Headline` 是否像研究报告标题
- `Headline` 是否出现交易动作或具体价格
- `Subheadline` 是否解释核心逻辑
- `Report Title` 是否符合研究报告风格
- `One Sentence Summary` 是否清晰、一致、易懂

标准调用顺序：

1. 调用 `title-generation` 生成标题。
2. 调用 `title-quality-gate` 检查标题。
3. 如果检查失败，返回 `title-generation` 重新生成。

职责边界：

- `title-generation`：负责生成。
- `title-quality-gate`：负责检查。
