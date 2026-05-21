# Android Harness

Android Harness 是一个轻量、可扩展、可由 agent 边用边增强的 Android
设备控制层。它通过稳定原语操作真实设备或模拟器：ADB、截图、输入事件、
uiautomator XML、日志和文件。

它是一个独立的 Android-focused 项目，参考了 Browser Harness 的架构思想；
本项目不隶属于 Browser Use，也不代表 Browser Harness 官方 Android 版本。

- 核心保持小而稳定。
- 任务级 helper 放在 `agent-workspace/agent_helpers.py`。
- 可复用 App 经验放在 `agent-workspace/app-skills/`。
- OCR、人类化操作、环境画像等能力放进插件层。

## Quick Start

连接已经授权 USB debugging 的 Android 设备或模拟器，然后运行：

```bash
android-harness doctor
```

通过 heredoc 执行 helper 代码：

```bash
android-harness <<'PY'
print(device_info())
print(current_app())
path = screenshot()
print(path)
PY
```

## Architecture

```text
src/android_harness/
  run.py       # CLI and Python execution environment
  helpers.py   # public agent-facing primitives
  adb.py       # ADB backend
  ui.py        # uiautomator XML parsing
  plugins.py   # plugin registry and boundaries
  admin.py     # diagnostics

agent-workspace/
  agent_helpers.py
  app-skills/

interaction-skills/
  permissions.md
  scrolling.md
  text-input.md
```

## Design Boundaries

核心包含设备事实、屏幕事实、App 状态、输入、文件、日志、等待和诊断。

核心不包含 OCR 引擎、特定 App 业务流程、隐藏/规避检测、账号处理、验证码处理、
支付流程或业务逻辑。这些能力只能在明确授权的前提下放入插件或 skills，并在
需要时通过 policy 插件做确认和约束。

## License

MIT License. See `LICENSE`.
