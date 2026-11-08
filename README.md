# Wuwa Tappo 自动点击 / 自动开宝箱

给 Wuwa Tappo (Windows 桌面宠物, Wuthering Waves × Bongo Cat) 用的小工具:

- **自动输入**: 每轮同时按下 12 个键 (F13~F24), 让 Tappo 计数、给宝箱充能。
  F13~F24 是普通键盘上没有的键, 系统和常用软件都不响应, **挂着它也能正常打字、玩游戏**
- **不抢鼠标**: 自动开箱会等你停止操作几秒后才执行, 点完把鼠标和窗口焦点还给你
- **自动开箱**: 定时点击你记录好的宝箱按钮位置 (可附带后续的"领取/确定"按钮), 或者用截图识别宝箱

## 使用

1. 安装 [Python 3](https://www.python.org/downloads/) (安装时勾选 *Add Python to PATH*)
2. 双击 `start.bat` (或 `python tappo_auto.py`)。第一次运行会生成 `config.json`
3. 打开 Tappo, 把鼠标移到 **宝箱按钮** 上按 `F8` 记录位置;
   如果开箱后还要点"领取/确定", 把鼠标移过去再按一次 `F8` (按顺序点击)
4. `F6` 开始自动输入, `F7` 开始自动开箱

| 热键 | 功能 |
|---|---|
| F6 | 开始/暂停 自动输入 |
| F7 | 开始/暂停 自动开箱 |
| F8 | 记录当前鼠标位置为开箱点击点 |
| F9 | 清空开箱点击点 |
| F10 | 退出 |
| F11 | 立即执行一次开箱点击 (测试用, 会打印点到了哪个窗口) |

> 如果 Tappo 以管理员权限运行, 本工具也需要以管理员身份运行 (双击 `start_admin.bat`), 否则 Windows 会拦截模拟点击。

## 配置 (`config.json`)

| 字段 | 说明 | 默认 |
|---|---|---|
| `input_mode` | `key` 模拟按键; `click` 在当前鼠标处左键 (会点到其它窗口, 慎用) | `key` |
| `keys` | 每轮同时按下的键列表, 可选 `f13`~`f24` `shift` `ctrl` `space` `a`~`z` `0`~`9` 等 | `f13`~`f24` 共 12 个 |
| `inputs_per_second` | 每秒按几轮 (每秒敲击数 = 轮数 × 键数) | `10` |
| `key_hold_seconds` | 每轮按下保持多久 | `0.01` |
| `pause_input_when_active` | 检测到你在操作键鼠时暂停自动输入 | `false` |
| `chest_wait_idle_seconds` | 你停止操作多少秒后才自动开箱 (`0` = 不等) | `3` |
| `jitter` | 间隔随机抖动比例 | `0.2` |
| `chest_interval_seconds` | 每隔多少秒尝试开箱 | `30` |
| `chest_click_delay_seconds` | 多个开箱点之间的等待 | `1.5` |
| `chest_points` | 开箱点击点 (F8 记录) | `[]` |
| `chest_image` | 宝箱按钮截图, 设置后改用图像识别 (只有宝箱出现时才点) | `""` |
| `image_confidence` | 图像匹配阈值 | `0.85` |
| `restore_cursor` | 开箱后把鼠标移回原位 | `true` |
| `click_method` | `sendinput` 模拟真实鼠标 / `message` 直接给窗口发鼠标消息 / `both` 两种都用 | `both` |
| `click_hover_seconds` | 鼠标移到按钮后停留多久再按下 | `0.2` |
| `click_hold_seconds` | 鼠标按下保持多久 | `0.12` |
| `focus_window` | 点击前先把目标窗口切到前台 | `true` |
| `auto_start_input` / `auto_start_chest` | 启动后立即开启 | `false` |

### 图像模式 (可选)

坐标模式会盲点, 宝箱没满时点一下一般也没影响。想要"满了才点", 可以:

```
pip install pyautogui opencv-python pillow
```

把宝箱**可开启状态**的按钮截个小图存为 `chest.png`, 在 `config.json` 里设置 `"chest_image": "chest.png"`。
此时 `chest_points` 里记录的点会作为点开宝箱之后依次点击的"领取/确定"按钮。

## 鼠标移过去了但没点开宝箱?

1. 用 **`start_admin.bat`** 以管理员身份运行 (最常见原因: Tappo 权限更高, 点击被系统拦截, 但移动鼠标不受影响)
2. 按 `F11` 测试一次, 看控制台打印的窗口标题是不是 Tappo; 出现"模拟输入被系统拦截"的警告也说明是权限问题
3. 把 `click_hover_seconds` 调到 `0.5`, `click_hold_seconds` 调到 `0.2` 试试
4. 分别把 `click_method` 改成 `sendinput` 或 `message` 试试哪种有效 (`both` 可能会在同一位置点两次)

## 提示

- 开启自动输入后看 Tappo 的计数涨得快不快, 确认 F13~F24 有被计入。如果没被计入, 把 `keys` 换成 `["shift", "ctrl"]` 之类
  (注意: Shift/Ctrl 会和你正在按的键组合, 这时建议把 `pause_input_when_active` 设成 `true`)。
- 如果 Tappo 对计数有速度上限, 调高轮数或键数也不会更快, 可以适当降低以免浪费。
- 旧版 `config.json` 里的 `"key": "shift"` 会自动升级成新的 `keys`。
- 自动开箱会短暂移动鼠标并点击, 挂机时使用效果最好。
- 本工具只模拟普通键鼠输入, 不修改游戏文件或内存; 是否符合官方规则请自行判断。
