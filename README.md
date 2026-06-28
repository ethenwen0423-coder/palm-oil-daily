# 棕榈油行情日报网站

这个目录是 `vinsontesla.com` 的静态网站源文件。

## 日常更新

1. 在 `reports/` 下新增当天 Markdown 日报，例如 `reports/2026-06-29.md`。
2. 运行 `bash scripts/deploy_report.sh`。
3. GitHub Pages 会自动更新公网网站。

## 域名发布

你已经购买了 `vinsontesla.com`，本站按 GitHub Pages 发布。

域名 DNS 需要在购买域名的平台添加：

- `A` 记录，主机名 `@`，指向 `185.199.108.153`
- `A` 记录，主机名 `@`，指向 `185.199.109.153`
- `A` 记录，主机名 `@`，指向 `185.199.110.153`
- `A` 记录，主机名 `@`，指向 `185.199.111.153`
- `CNAME` 记录，主机名 `www`，指向 `ethenwen0423-coder.github.io`

自动任务会每天生成并整理日报，然后推送到 GitHub。真正通过 `vinsontesla.com` 访问，还取决于 DNS 是否配置完成并生效。
