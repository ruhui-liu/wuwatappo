# -*- coding: utf-8 -*-
"""
Wuwa Tappo 自动点击 + 自动开宝箱工具 (仅 Windows)

原理:
  - 自动输入: 通过 Win32 SendInput 定时模拟按键/鼠标点击, Tappo 会把它计入敲击数, 从而给宝箱充能。
  - 自动开箱: 两种方式任选
      1) 坐标模式: 用热键记录宝箱按钮(以及之后需要点的"确定/领取"按钮)的位置, 定时依次点击。
      2) 图像模式: 提供宝箱按钮截图, 屏幕上找到它才点击 (需要 pip install pyautogui opencv-python pillow)。

热键 (全局):
  F6  开始/暂停 自动输入
  F7  开始/暂停 自动开箱
  F8  把当前鼠标位置追加为一个开箱点击点 (按顺序点击)
  F9  清空所有开箱点击点
  F10 退出
"""
import ctypes
import json
import os
import random
import sys
import time
from ctypes import wintypes

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

DEFAULT_CONFIG = {
    # 自动输入方式: "key" 模拟按键, "click" 在当前鼠标位置左键点击 (不推荐, 会点到别的窗口)
    "input_mode": "key",
    # 模拟的按键 (虚拟键码名), 默认 Shift: 在绝大多数程序里单按 Shift 不会产生任何效果
    "key": "shift",
    # 每秒模拟次数
    "inputs_per_second": 10,
    # 每次间隔的随机抖动比例 (0~1)
    "jitter": 0.2,
    # 每隔多少秒尝试开一次宝箱
    "chest_interval_seconds": 30,
    # 开箱点击点之间的等待秒数 (等动画/弹窗)
    "chest_click_delay_seconds": 1.5,
    # 开箱点击点, 用 F8 记录, 格式 [[x, y], ...]
    "chest_points": [],
    # 图像模式: 宝箱按钮截图路径, 留空则使用坐标模式
    "chest_image": "",
    "image_confidence": 0.85,
    # 开箱后是否把鼠标移回原来的位置
    "restore_cursor": True,
    # 启动时是否立即开启
    "auto_start_input": False,
    "auto_start_chest": False,
}

VK = {
    "shift": 0x10, "ctrl": 0x11, "alt": 0x12, "space": 0x20,
    "lshift": 0xA0, "rshift": 0xA1, "lctrl": 0xA2, "rctrl": 0xA3,
    "f13": 0x7C, "f14": 0x7D, "f15": 0x7E, "f16": 0x7F,
    "f17": 0x80, "f18": 0x81, "f19": 0x82, "f20": 0x83,
    "scrolllock": 0x91, "numlock": 0x90,
}
for _c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789":
    VK[_c.lower()] = ord(_c)

HOTKEY_INPUT, HOTKEY_CHEST, HOTKEY_ADD, HOTKEY_CLEAR, HOTKEY_EXIT = 0x75, 0x76, 0x77, 0x78, 0x79  # F6..F10

# ---------------------------------------------------------------- Win32 ----
if sys.platform != "win32":
    print("这个工具只能在 Windows 上运行 (Wuwa Tappo 是 Windows 程序)。")
    sys.exit(1)

user32 = ctypes.WinDLL("user32", use_last_error=True)

INPUT_MOUSE, INPUT_KEYBOARD = 0, 1
KEYEVENTF_KEYUP = 0x0002
MOUSEEVENTF_LEFTDOWN, MOUSEEVENTF_LEFTUP = 0x0002, 0x0004
ULONG_PTR = ctypes.c_size_t


class MOUSEINPUT(ctypes.Structure):
    _fields_ = [("dx", wintypes.LONG), ("dy", wintypes.LONG), ("mouseData", wintypes.DWORD),
                ("dwFlags", wintypes.DWORD), ("time", wintypes.DWORD), ("dwExtraInfo", ULONG_PTR)]


class KEYBDINPUT(ctypes.Structure):
    _fields_ = [("wVk", wintypes.WORD), ("wScan", wintypes.WORD), ("dwFlags", wintypes.DWORD),
                ("time", wintypes.DWORD), ("dwExtraInfo", ULONG_PTR)]


class HARDWAREINPUT(ctypes.Structure):
    _fields_ = [("uMsg", wintypes.DWORD), ("wParamL", wintypes.WORD), ("wParamH", wintypes.WORD)]


class _INPUTUNION(ctypes.Union):
    _fields_ = [("mi", MOUSEINPUT), ("ki", KEYBDINPUT), ("hi", HARDWAREINPUT)]


class INPUT(ctypes.Structure):
    _anonymous_ = ("u",)
    _fields_ = [("type", wintypes.DWORD), ("u", _INPUTUNION)]


user32.SendInput.argtypes = (wintypes.UINT, ctypes.POINTER(INPUT), ctypes.c_int)
user32.MapVirtualKeyW.argtypes = (wintypes.UINT, wintypes.UINT)
user32.GetAsyncKeyState.argtypes = (ctypes.c_int,)
user32.GetAsyncKeyState.restype = ctypes.c_short

try:  # 让坐标在高 DPI 缩放下也准确
    ctypes.WinDLL("shcore").SetProcessDpiAwareness(2)
except Exception:
    try:
        user32.SetProcessDPIAware()
    except Exception:
        pass


def _send(*inputs):
    arr = (INPUT * len(inputs))(*inputs)
    user32.SendInput(len(inputs), arr, ctypes.sizeof(INPUT))


def press_key(vk):
    scan = user32.MapVirtualKeyW(vk, 0)
    down = INPUT(type=INPUT_KEYBOARD, ki=KEYBDINPUT(wVk=vk, wScan=scan, dwFlags=0))
    up = INPUT(type=INPUT_KEYBOARD, ki=KEYBDINPUT(wVk=vk, wScan=scan, dwFlags=KEYEVENTF_KEYUP))
    _send(down)
    time.sleep(random.uniform(0.02, 0.05))
    _send(up)


def left_click():
    _send(INPUT(type=INPUT_MOUSE, mi=MOUSEINPUT(dwFlags=MOUSEEVENTF_LEFTDOWN)))
    time.sleep(random.uniform(0.03, 0.06))
    _send(INPUT(type=INPUT_MOUSE, mi=MOUSEINPUT(dwFlags=MOUSEEVENTF_LEFTUP)))


def get_cursor():
    pt = wintypes.POINT()
    user32.GetCursorPos(ctypes.byref(pt))
    return pt.x, pt.y


def click_at(x, y):
    user32.SetCursorPos(int(x), int(y))
    time.sleep(0.05)
    left_click()


def key_pressed_once(vk, _state={}):
    """边沿检测: 按下的那一刻返回 True 一次。"""
    down = bool(user32.GetAsyncKeyState(vk) & 0x8000)
    was = _state.get(vk, False)
    _state[vk] = down
    return down and not was


# --------------------------------------------------------------- config ----
def load_config():
    cfg = dict(DEFAULT_CONFIG)
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                cfg.update(json.load(f))
        except Exception as e:
            print(f"[警告] 读取 config.json 失败, 使用默认配置: {e}")
    else:
        save_config(cfg)
    return cfg


def save_config(cfg):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------- chest ----
def find_chest_by_image(cfg):
    try:
        import pyautogui
    except ImportError:
        print("[图像模式] 未安装 pyautogui, 请运行: pip install pyautogui opencv-python pillow")
        return None
    path = cfg["chest_image"]
    if not os.path.isabs(path):
        path = os.path.join(os.path.dirname(CONFIG_PATH), path)
    try:
        box = pyautogui.locateCenterOnScreen(path, confidence=cfg["image_confidence"], grayscale=True)
    except TypeError:  # 没装 opencv 时不支持 confidence
        box = pyautogui.locateCenterOnScreen(path, grayscale=True)
    except Exception:
        box = None
    return (box.x, box.y) if box else None


def open_chest(cfg):
    origin = get_cursor()
    try:
        if cfg.get("chest_image"):
            pos = find_chest_by_image(cfg)
            if not pos:
                print(time.strftime("[%H:%M:%S]"), "没找到可开的宝箱")
                return
            click_at(*pos)
            print(time.strftime("[%H:%M:%S]"), f"点击宝箱 {pos}")
            # 图像模式下, 额外记录的点作为"领取/确定"等后续按钮
            for x, y in cfg["chest_points"]:
                time.sleep(cfg["chest_click_delay_seconds"])
                click_at(x, y)
        else:
            if not cfg["chest_points"]:
                print("[开箱] 还没有记录点击点: 把鼠标放到宝箱按钮上按 F8")
                return
            for i, (x, y) in enumerate(cfg["chest_points"]):
                if i:
                    time.sleep(cfg["chest_click_delay_seconds"])
                click_at(x, y)
            print(time.strftime("[%H:%M:%S]"), f"已执行开箱点击 x{len(cfg['chest_points'])}")
    finally:
        if cfg.get("restore_cursor", True):
            user32.SetCursorPos(*origin)


# ----------------------------------------------------------------- main ----
def main():
    cfg = load_config()
    key_name = str(cfg["key"]).lower()
    if cfg["input_mode"] == "key" and key_name not in VK:
        print(f"[错误] 不支持的按键 '{cfg['key']}', 可选: {', '.join(sorted(VK))}")
        sys.exit(1)
    vk = VK.get(key_name)

    input_on = bool(cfg["auto_start_input"])
    chest_on = bool(cfg["auto_start_chest"])
    rate = max(0.1, float(cfg["inputs_per_second"]))
    next_input = time.monotonic()
    next_chest = time.monotonic() + 3
    count = 0

    def status():
        print(f"  自动输入: {'开' if input_on else '关'} | 自动开箱: {'开' if chest_on else '关'}"
              f" | 开箱点: {len(cfg['chest_points'])} | 已模拟: {count}")

    print(__doc__)
    print(f"配置文件: {CONFIG_PATH}")
    status()

    while True:
        now = time.monotonic()

        if key_pressed_once(HOTKEY_EXIT):
            print("退出。")
            break
        if key_pressed_once(HOTKEY_INPUT):
            input_on = not input_on
            next_input = now
            status()
        if key_pressed_once(HOTKEY_CHEST):
            chest_on = not chest_on
            next_chest = now
            status()
        if key_pressed_once(HOTKEY_ADD):
            p = list(get_cursor())
            cfg["chest_points"].append(p)
            save_config(cfg)
            print(f"  已添加开箱点 #{len(cfg['chest_points'])}: {p}")
        if key_pressed_once(HOTKEY_CLEAR):
            cfg["chest_points"] = []
            save_config(cfg)
            print("  已清空开箱点")

        if chest_on and now >= next_chest:
            open_chest(cfg)
            next_chest = time.monotonic() + max(1.0, float(cfg["chest_interval_seconds"]))
            next_input = time.monotonic()

        if input_on and now >= next_input:
            if cfg["input_mode"] == "click":
                left_click()
            else:
                press_key(vk)
            count += 1
            if count % 500 == 0:
                status()
            base = 1.0 / rate
            j = float(cfg["jitter"])
            next_input = now + base * random.uniform(1 - j, 1 + j)

        time.sleep(0.005)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
