# Title Quality Gate Checklist

Use this checklist only to inspect a title set. Do not generate replacement titles here.

## Headline

- [ ] 是否表达今天市场交易的主线？
- [ ] 是否概括市场核心观点，而不是交易动作？
- [ ] 是否能够独立作为研究报告标题？
- [ ] 是否更像 Bloomberg、Reuters 或国内头部期货研究所标题？
- [ ] 是否不像微信群盘前提示？
- [ ] 是否能够脱离正文，让读者理解当天市场核心变化？
- [ ] 是否没有为了和昨天不同而创造不存在的新观点？

## Forbidden Content

- [ ] 是否不包含具体价格？
- [ ] 是否不包含追高？
- [ ] 是否不包含止损？
- [ ] 是否不包含承接？
- [ ] 是否不包含加仓？
- [ ] 是否不包含减仓？
- [ ] 是否不包含交易计划？

## Subheadline

- [ ] 是否解释观点背后的核心逻辑？
- [ ] 是否没有告诉用户如何交易？
- [ ] 是否与 Headline 表达的市场主线一致？

## Report Title

- [ ] 是否具备研究报告标题风格？
- [ ] 是否正式、克制、结论明确？
- [ ] 是否不像聊天消息或公众号标题？

## One Sentence Summary

- [ ] 是否一句话表达结论和原因？
- [ ] 是否清晰易懂？
- [ ] 是否没有新增标题之外的 unsupported claim？

## Gate Result

If any item fails, return `需重写` and send the failed checks back to `title-generation`.
