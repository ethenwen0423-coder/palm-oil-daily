# 日报保存规则

每天生成一份 Markdown 文件，文件名使用 `YYYY-MM-DD.md`。

建议结构：

```markdown
# 2026-06-29 棕榈油行情日报

## 核心结论
- ...

## 盘面与价格
- ...

## 基本面
- ...

## 外盘与宏观
- ...

## 今日关注
- ...
```

写好日报后运行：

```bash
python3 scripts/publish_report.py
```
