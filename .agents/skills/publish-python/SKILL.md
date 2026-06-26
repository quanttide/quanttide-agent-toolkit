---
name: publish-python
version: 1.0.0
description: "发布 Python 包到 PyPI：更新 CHANGELOG → 升级版本号 → 创建 tag + GitHub Release → CI 自动发布到 PyPI"
---

# Publish Python Package

## 前提条件

- 代码变更已提交到 `main` 分支并推送
- CI 已配置 `publish-python.yml`（监听 `release: [published]`，过滤 `refs/tags/python/`）

## 流程

### 第一步：更新 CHANGELOG

文件：`packages/python/CHANGELOG.md`

- 在顶部追加新版本条目，**不要覆盖原有历史**
- 版本格式：`## [0.4.0]` — 括号内不带 `v`
- 分类使用 `### Added` / `### Changed` / `### Fixed` 等

### 第二步：升级版本号

文件：`packages/python/pyproject.toml`

```toml
version = "0.4.0"
```

**CI 会校验 tag 版本与 pyproject.toml 版本是否一致**，不一致则发布失败。

### 第三步：创建根目录 CHANGELOG（如不存在）

文件：`CHANGELOG.md`（repo 根目录，非 `packages/python/`）

```
## [0.4.0] - 2026-06-23
```

- 只包含当前版本的信息即可
- 版本格式与 packages/python/ 一致：`[0.4.0]`（不带 scope，不带 `v`）

### 第四步：提交并推送

```bash
git add -A
git commit -m "chore: bump python v0.3.0 → v0.4.0"
git push origin main
```

### 第五步：运行发布命令

```bash
qtcloud-devops release publish --version python/v0.4.0 -y
```

参数格式说明：

| | 格式 | 示例 |
|---|---|---|
| `--version` | `scope/vX.Y.Z` | `python/v0.4.0` |
| CHANGELOG 条目 | `[X.Y.Z]` | `[0.4.0]` |

工具从参数中提取版本号时，同时去掉 scope 前缀和 `v`，只留 `X.Y.Z` 去 CHANGELOG 匹配。

### 第六步：验证

```bash
pip index versions quanttide-agent
```

确认 `LATEST` 显示新版本。CI 执行约需 30s，可在 GitHub Actions 查看进度。

## 常见错误

| 错误 | 原因 | 修复 |
|------|------|------|
| `CHANGELOG.md 不存在` | 根目录缺少 CHANGELOG.md | 在 repo 根目录创建 |
| `未找到 X.Y.Z 版本记录` | CHANGELOG 条目格式不匹配 | 检查版本号格式：`[X.Y.Z]`（不带 `v`） |
| tag/push 冲突 | 手动创建了 tag 或重复运行 | `git tag -d python/vX.Y.Z && git push origin --delete python/vX.Y.Z` 后重试 |
