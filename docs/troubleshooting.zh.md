# 故障排查指南

本文覆盖 Android Harness 在 Linux、ADB、模拟器、ADB-over-TCP 和 daemon
transport 中常见的故障。

Android Harness 是 host-side / ADB-first 工具。它不会绕过 Android 授权弹窗、
账号检查、App 保护、模拟器检测、root 检测，也不会隐藏自动化或调试信号。

## 快速定位

先在运行 agent 或 CLI 的同一台 host 上执行：

```bash
which adb
adb version
adb devices -l
android-harness doctor
```

如果启用了 daemon transport：

```bash
android-harness daemon status
android-harness --transport daemon doctor
```

反馈问题时，建议附上这些命令的脱敏输出，以及 host OS、Python 版本、Android
版本、连接方式、设备或模拟器型号。

## 找不到 ADB 或 ADB 版本不对

常见现象：

- `adb not found on PATH`
- `android-harness doctor` 在选择设备前失败
- `adb version` 不是预期版本

检查：

```bash
which adb
adb version
python -m pip show android-harness
```

处理：

- 安装 Android SDK Platform Tools，或发行版提供的包，例如 `android-tools-adb`。
- 确保预期的 `adb` 目录排在旧版本 `adb` 前面。
- 修改 `PATH` 后重启 shell、terminal、service 或 agent runtime。
- 替换 `adb` 后执行：

```bash
adb kill-server
adb start-server
```

## 看不到设备

常见现象：

- `adb devices -l` 只有表头
- `android-harness doctor` 找不到 ready device

检查：

```bash
adb kill-server
adb start-server
adb devices -l
```

处理：

- 真实设备需要启用 Developer options 和 USB debugging。
- 重新插拔 USB，并在设备提示时选择可传输数据的 USB 模式。
- 排查连接问题时，优先使用主机直连 USB 口，减少 hub 干扰。
- 模拟器需要等待完整启动后再运行 doctor。
- 如果有多个 agent runtime，确认这些命令运行在同一个 runtime 中。

## 设备显示 unauthorized

常见现象：

- `adb devices -l` 显示 `unauthorized`
- `android-harness doctor` 无法读取设备信息

处理：

- 解锁 Android 设备。
- 在设备上接受 USB debugging RSA 授权弹窗。
- 如果弹窗不出现，在 Android Developer options 中 revoke USB debugging
  authorizations，然后重新连接并再次运行 `adb devices -l`。
- 重启 ADB server：

```bash
adb kill-server
adb start-server
adb devices -l
```

Android Harness 不能跳过这个授权步骤。

## 设备 offline 或连接不稳定

常见现象：

- `adb devices -l` 显示 `offline`
- 命令偶发 timeout
- 截图或 UI dump 偶发失败

处理：

- 重新插拔 USB，并等待几秒。
- 重启 ADB server。
- 如果长期 offline，重启模拟器或真实设备。
- 运行过程中不要切换 USB 模式。
- 如果使用 ADB-over-TCP，从 host 重新连接：

```bash
adb disconnect
adb connect <device-ip>:5555
```

## Linux USB 权限问题

常见现象：

- `adb devices -l` 显示 `no permissions`
- root 用户能连接设备，但 agent 用户不行

检查：

```bash
id
lsusb
adb devices -l
```

处理：

- 安装发行版或厂商提供的 Android 设备 udev rules。
- 将 agent 用户加入发行版使用的设备访问组，常见名称包括 `plugdev` 或
  `adbusers`。
- 修改用户组后退出并重新登录。
- 重新连接设备并重启 ADB server。

不要为了绕过 USB 权限问题而长期用 root 运行 agent。修正 udev 和用户组权限更容易
审计。

## 同时连接了多台设备

常见现象：

- `adb` 报 `more than one device/emulator`
- `android-harness doctor` 选中了非预期设备

处理：

使用其中一种方式固定目标设备：

```bash
export ANDROID_SERIAL=<device-id>
android-harness doctor
```

```bash
android-harness -s <device-id> doctor
```

脚本、示例、smoke test 和 agent 运行应使用同一个 serial。

## 模拟器不出现

常见现象：

- Android Emulator 已打开，但 `adb devices -l` 中没有
- `emulator-5554` 显示 offline
- Linux 上模拟器启动慢或启动失败

检查：

```bash
adb devices -l
adb shell getprop sys.boot_completed
ls -l /dev/kvm
```

处理：

- 等待模拟器完整启动，直到 `sys.boot_completed` 返回 `1`。
- 通过 Android Studio 或 SDK tools 安装 Android Emulator、Android SDK
  Platform Tools 和至少一个 system image。
- Linux 上确认当前用户可以访问 `/dev/kvm`，以使用硬件加速。
- 在嵌套虚拟化、VM、container 或 WSL 环境中，先确认 KVM 或等价加速路径可用。
- 如果模拟器一直 offline，重启 ADB 和模拟器。

## ADB-over-TCP 无法连接

常见现象：

- `adb connect <ip>:5555` 失败
- `android-harness -s <ip>:5555 doctor` 无法访问设备

检查：

```bash
adb devices -l
adb tcpip 5555
adb connect <device-ip>:5555
adb devices -l
```

处理：

- 先通过 USB 授权设备，再切换到 TCP/IP。
- 确保 host 和设备在可互通网络中。
- serial 需要包含端口，例如 `<device-ip>:5555`。
- 测试结束后，如果环境不需要 TCP/IP，可以断开：

```bash
adb disconnect <device-ip>:5555
```

不要把 ADB-over-TCP 暴露在不可信网络中。

## Daemon transport 失败

常见现象：

- `android-harness --transport daemon doctor` 提示 daemon unavailable
- `android-harness daemon status` 显示 `stale socket`
- daemon 启动失败并输出 log 路径

检查：

```bash
android-harness daemon status
android-harness daemon stop
android-harness daemon start
android-harness --transport daemon doctor
```

说明：

- daemon 是可选能力。默认 subprocess transport 不依赖 daemon：

```bash
android-harness --transport subprocess doctor
```

- 默认 socket 路径是 `${XDG_RUNTIME_DIR}/android-harness/daemon.sock`。如果
  `XDG_RUNTIME_DIR` 不存在或不可用，会 fallback 到
  `/tmp/android-harness-${uid}/daemon.sock`。
- 启动诊断 log 会写在 socket 旁边，例如 `daemon.sock.log`。
- stale socket 表示 socket 路径存在，但没有健康 daemon 响应。`daemon stop` 会
  删除 stale socket，`daemon start` 会先删除 stale socket 再启动新 daemon。

## 截图或 UI dump 失败

常见现象：

- 截图文件为空或不存在
- `uiautomator` 输出为空或 XML 异常
- `page_info()` 无法解析当前页面

处理：

- 确认设备已解锁并亮屏。
- 先运行 `android-harness doctor`。
- 单独测试截图：

```bash
adb exec-out screencap -p > /tmp/android-screen.png
```

- 某些安全页面会主动阻止截图或 UI inspection。Android Harness 不绕过这些平台或
  App 限制。

## Unicode 文本输入失败

常见现象：

- 中文、emoji 或符号输入乱码
- `adb shell input text` 无法输入预期文本

处理：

- 使用输入法插件，例如 `plugins/adbkeyboard_plugin.py`。
- core `type_text()` 只适合简单 ASCII 文本。

## 提交 Issue 前

建议包含：

- `android-harness doctor` 输出
- `adb devices -l`
- `adb version`
- Host OS 和 Python 版本
- Android 版本、设备型号、模拟器名称和连接方式
- 是否启用了 daemon transport
- 已脱敏日志，不要包含真实账号、token、支付数据、短信、验证码或个人数据
