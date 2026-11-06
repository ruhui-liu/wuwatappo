# Wuwa Tappo 自动点击 / 自动开宝箱

给 Wuwa Tappo (Windows 桌面宠物, Wuthering Waves × Bongo Cat) 用的小工具:

- **自动输入**: 定时模拟按键 (默认 `Shift`), 让 Tappo 计数、给宝箱充能
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

> 如果 Tappo 以管理员权限运行, 本工具也需要以管理员身份运行, 否则模拟输入可能无效。

## 配置 (`config.json`)

| 字段 | 说明 | 默认 |
|---|---|---|
| `input_mode` | `key` 模拟按键; `click` 在当前鼠标处左键 (会点到其它窗口, 慎用) | `key` |
| `key` | 模拟的按键: `shift` `ctrl` `space` `f13`~`f20` `a`~`z` `0`~`9` 等 | `shift` |
| `inputs_per_second` | 每秒模拟次数 | `10` |
| `jitter` | 间隔随机抖动比例 | `0.2` |
| `chest_interval_seconds` | 每隔多少秒尝试开箱 | `30` |
| `chest_click_delay_seconds` | 多个开箱点之间的等待 | `1.5` |
| `chest_points` | 开箱点击点 (F8 记录) | `[]` |
| `chest_image` | 宝箱按钮截图, 设置后改用图像识别 (只有宝箱出现时才点) | `""` |
| `image_confidence` | 图像匹配阈值 | `0.85` |
| `restore_cursor` | 开箱后把鼠标移回原位 | `true` |
| `auto_start_input` / `auto_start_chest` | 启动后立即开启 | `false` |

### 图像模式 (可选)

坐标模式会盲点, 宝箱没满时点一下一般也没影响。想要"满了才点", 可以:

```
pip install pyautogui opencv-python pillow
```

把宝箱**可开启状态**的按钮截个小图存为 `chest.png`, 在 `config.json` 里设置 `"chest_image": "chest.png"`。
此时 `chest_points` 里记录的点会作为点开宝箱之后依次点击的"领取/确定"按钮。

## 提示

- 如果 `Shift` 不被 Tappo 计数, 换成 `space` 或字母键试试 (注意会输入到当前焦点窗口, 可以把焦点放在记事本或桌面上)。
- 自动开箱会短暂移动鼠标并点击, 挂机时使用效果最好。
- 本工具只模拟普通键鼠输入, 不修改游戏文件或内存; 是否符合官方规则请自行判断。
