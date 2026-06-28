# 发布指南

这个文档用于让 Android Harness 的发布流程保持小、可复现、可审计。

## 发布检查清单

1. 确认工作区干净：

   ```bash
   git status --short
   ```

2. 运行本地检查：

   ```bash
   make check PYTHON=.venv/bin/python
   ```

3. 本地构建包：

   ```bash
   .venv/bin/python -m build --outdir /tmp/android-harness-dist
   ```

4. 确认 `CHANGELOG.md` 已记录本次 release 面向用户的变化。

5. 确认 `ROADMAP.md` 已同步完成项和剩余公开方向。

6. 创建并推送版本 tag：

   ```bash
   git tag v0.1.0
   git push github v0.1.0
   ```

7. 等待 GitHub Actions 中的 `CI` 和 `Release Build` workflow 全部通过。

8. 基于 tag 创建 GitHub Release，并附加 `Release Build` workflow 产出的
   `android-harness-dist` artifact。

9. 在已授权设备或模拟器上运行手动 smoke check：

   ```bash
   android-harness smoke
   android-harness exec examples/basic_observe.py
   ```

## 发布边界

- Release artifact 只应包含 host-side Python package 和文档。
- 不要打包 Android APK、keystore、账号数据、截图或设备日志。
- ADBKeyboard 这类可选设备端依赖必须保持外部依赖，并由用户自行管理。
- Release notes 不应宣称支持 stealth、evasion、账号自动化、支付自动化、
  CAPTCHA 处理或风控绕过。
