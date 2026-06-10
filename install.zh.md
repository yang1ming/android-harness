# Agent Skill 安装指南

中文 | [English](install.md)

本文面向需要安装并使用 Android Harness skill 的 agent 和 agent runtime。

Android Harness 包含两个部分：

- `SKILL.md`：面向 agent 的 skill 入口。
- `android-harness`：host-side CLI，skill 通过它使用 ADB 控制已授权的 Android 设备。

只安装 skill 文件是不够的。agent 执行环境还必须能够运行 `android-harness` CLI。

## 需求

- Python 3.10+
- Android platform-tools，并确保 `adb` 在 `PATH` 中
- 已授权的 Android 设备或模拟器
- 已启用并授权 USB debugging，或已授权的 ADB over TCP/IP 目标

Android Harness 默认是 host-side / ADB-first 工具。不要把本仓库本身部署到
Android 设备上。

## 从 Git 仓库安装

把仓库克隆到稳定路径：

```bash
git clone <repo-url> /path/to/android-harness
cd /path/to/android-harness
python -m pip install -e .
android-harness doctor
```

如果连接了多台设备，可以设置：

```bash
export ANDROID_SERIAL=<device-id>
```

或者在运行命令时通过 `-s <device-id>` 指定：

```bash
android-harness -s emulator-5554 doctor
```

## 安装 Agent Skill

仓库根目录的 `SKILL.md` 是 skill 入口。

如果 agent 支持直接从 GitHub 仓库读取 skills，把 skill installer 指向本仓库 URL。
installer 应该使用仓库根目录的 `SKILL.md`。

如果 agent 从本地 skill 目录读取 skills，把 skill 文件安装到对应目录。以 Codex
风格的 skill discovery 为例：

```bash
mkdir -p ~/.codex/skills/android-harness
cp /path/to/android-harness/SKILL.md ~/.codex/skills/android-harness/SKILL.md
cp /path/to/android-harness/README.md ~/.codex/skills/android-harness/
cp /path/to/android-harness/README.zh.md ~/.codex/skills/android-harness/
cp /path/to/android-harness/install.md ~/.codex/skills/android-harness/
cp /path/to/android-harness/install.zh.md ~/.codex/skills/android-harness/
cp /path/to/android-harness/NOTICE.md ~/.codex/skills/android-harness/
cp /path/to/android-harness/LICENSE ~/.codex/skills/android-harness/
cp -R /path/to/android-harness/interaction-skills ~/.codex/skills/android-harness/
```

复制后的 skill 仍然应该调用从仓库路径安装的 CLI：

```bash
android-harness doctor
```

## 验证 Agent 就绪状态

运行：

```bash
android-harness doctor
```

然后验证 helper 环境：

```bash
android-harness <<'PY'
print(device_info())
print(current_app())
print(page_info())
PY
```

就绪的 agent 应该优先使用这个操作循环：

1. 截图。
2. 在有帮助时检查当前 app 和 UI tree。
3. 执行 tap、swipe、文本输入或 key event。
4. 等待 screen、app 或 text 改变。
5. 捕获结果。

## 可选设备端组件

核心 Android Harness 不需要 APK 或 AccessibilityService。

某些可选插件可能需要设备端组件。例如 `plugins/adbkeyboard_plugin.py` 会与外部
ADBKeyboard IME 配合，用于 Unicode 文本输入。该 IME 不由本仓库分发，用户需要
自行按照它的协议和政策安装、使用。

## 安全边界

只在授权设备、授权 app 和授权环境中使用这个 skill。

不要把 Android Harness 用于：

- 未授权设备、app 或账号。
- 账号接管、验证码处理、支付流程、批量注册或绕过风控。
- 隐藏 ADB、root、模拟器、自动化或调试信号。
- 把特定 app 业务流程加入 core。
- 把账号数据或私有运营数据加入 core。
