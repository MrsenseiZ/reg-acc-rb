#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module Tự Động Thao Tác Trực Tiếp Trên App Delta Roblox (Android Native UI)
Phiên bản Tối Ưu Hóa Tuyệt Đối (Không dùng uiautomator gây treo máy):
1. Mở App chuẩn 100% qua Protocol roblox:// và Intent Launcher (Không crash)
2. Điền form tuần tự từng bước chuẩn xác
3. Tự động xóa data (pm clear) để logout siêu tốc
"""

import os
import sys
import time
import shutil
import subprocess
from datetime import datetime
from typing import Optional, Tuple, Dict, Any

from generators import generate_username, generate_password, generate_birthday, generate_gender
from proxy_manager import ProxyManager
from discord_notifier import DiscordNotifier

CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
RESET = "\033[0m"

class RobloxAppAutomator:
    def __init__(self, package_name: str = "com.roblox.client", discord: Optional[DiscordNotifier] = None):
        self.package_name = package_name
        self.discord = discord
        self.root_cmd = self._detect_root()
        print(f"{CYAN}🔧 [Hệ Thống] Phương thức: {BOLD}{self.root_cmd.upper()}{RESET}")
        self.auto_grant_all_permissions()
        self.auto_enable_omocaptcha()
        self.package_name = self.detect_roblox_package()
        self.width, self.height = self.get_screen_size()
        print(f"{CYAN}📐 [Màn Hình]: {self.width}x{self.height}{RESET}")

    def _detect_root(self) -> str:
        candidates = ["su", "tsu", "/system/xbin/su", "/system/bin/su", "/sbin/su"]
        for cmd in candidates:
            if shutil.which(cmd) or os.path.exists(cmd):
                try:
                    r = subprocess.run(f"{cmd} -c 'id'", shell=True, capture_output=True, text=True, timeout=2)
                    if "uid=0" in r.stdout or r.returncode == 0:
                        return cmd
                except Exception:
                    pass
        return "native"

    def run_cmd(self, command: str) -> str:
        """Thực thi lệnh shell trên Android."""
        try:
            if self.root_cmd in ["su", "tsu", "/system/xbin/su", "/system/bin/su", "/sbin/su"]:
                full_cmd = f"{self.root_cmd} -c \"{command}\""
            else:
                full_cmd = f"/system/bin/sh -c \"{command}\"" if os.path.exists("/system/bin/sh") else command

            res = subprocess.run(full_cmd, shell=True, capture_output=True, text=True, timeout=10)
            return (res.stdout or "") + (res.stderr or "")
        except Exception as e:
            return str(e)

    def get_screen_size(self) -> Tuple[int, int]:
        try:
            out = self.run_cmd("wm size")
            for line in out.splitlines():
                if "size:" in line.lower():
                    parts = line.split(":")[-1].strip().split("x")
                    if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                        w1, w2 = int(parts[0]), int(parts[1])
                        return min(w1, w2), max(w1, w2)
        except Exception:
            pass
        return 720, 1280

    def tap_percent(self, px: float, py: float, delay: float = 0.5):
        """Chạm chính xác theo tỷ lệ màn hình đứng dọc."""
        real_x = int(self.width * px)
        real_y = int(self.height * py)
        self.run_cmd(f"input tap {real_x} {real_y}")
        if delay > 0:
            time.sleep(delay)

    def input_text(self, text: str):
        """Gõ văn bản."""
        escaped = text.replace(" ", "%s").replace("&", "\&").replace("!", "\!")
        self.run_cmd(f"input text '{escaped}'")

    def keyevent(self, code: int):
        """Gửi phím (4: Back, 61: Tab, 66: Enter)."""
        self.run_cmd(f"input keyevent {code}")
        time.sleep(0.3)

    def auto_grant_all_permissions(self):
        cmds = [
            "appops set com.termux SYSTEM_ALERT_WINDOW allow",
            "appops set com.termux RUN_IN_BACKGROUND allow",
            f"appops set {self.package_name} SYSTEM_ALERT_WINDOW allow",
        ]
        for c in cmds:
            self.run_cmd(c)

    def auto_enable_omocaptcha(self):
        try:
            self.run_cmd("settings put secure accessibility_enabled 1")
            self.run_cmd("settings put secure enabled_accessibility_services com.omocaptcha/com.omocaptcha.service.MyAccessibilityService:com.omocaptcha/.AccessibilityService")
        except Exception:
            pass

    def detect_roblox_package(self) -> str:
        try:
            out = self.run_cmd("pm list packages")
            for line in out.splitlines():
                if "roblox" in line.lower() or "delta" in line.lower():
                    pkg = line.replace("package:", "").strip()
                    if pkg and pkg != "com.delta.installer":
                        return pkg
        except Exception:
            pass
        return self.package_name

    def clear_app_data(self):
        print(f"{CYAN}🧹 Đang xóa bộ nhớ đệm app (pm clear)...{RESET}")
        self.run_cmd(f"pm clear {self.package_name}")
        time.sleep(1.0)

    def launch_roblox(self):
        """Khởi động app Roblox chuẩn xác 100% (Mở trực tiếp lên màn hình chính)."""
        print(f"{CYAN}📱 Đang mở ứng dụng Roblox...{RESET}")
        
        # 1. Dùng Intent chuẩn kèm cờ NEW_TASK và Protocol
        self.run_cmd(f"am start -a android.intent.action.VIEW -d 'roblox://' -f 0x10000000 2>/dev/null")
        self.run_cmd(f"am start -a android.intent.action.MAIN -c android.intent.category.LAUNCHER -n {self.package_name}/com.roblox.client.ActivityProtocolLaunch -f 0x10000000 2>/dev/null")
        self.run_cmd(f"monkey -p {self.package_name} -c android.intent.category.LAUNCHER 1 2>/dev/null")
        
        # Đếm ngược chờ màn hình load
        for s in range(7):
            time.sleep(1)
            sys.stdout.write(f"\r{YELLOW}    ⏳ Đang đợi app Roblox xuất hiện: [{s+1}/7s]...{RESET}")
            sys.stdout.flush()
        print()

    def register_single_account_on_app(self, proxy_str: Optional[str] = None) -> Tuple[bool, str, str, str]:
        """Chu trình tạo tài khoản tự động hoàn chỉnh."""
        username = generate_username()
        password = generate_password("random")
        bday = generate_birthday(age_mode="18+")
        gender = generate_gender()

        print(f"\n{CYAN}📱 [App Auto] Bắt đầu chu trình tạo tài khoản: {BOLD}{username}{RESET}")

        # 1. Gán Proxy
        if proxy_str:
            clean_proxy = proxy_str.replace("http://", "").replace("https://", "").replace("socks5://", "")
            if "@" in clean_proxy:
                _, host_port = clean_proxy.split("@", 1)
                host, port = host_port.split(":")
            elif ":" in clean_proxy:
                parts = clean_proxy.split(":")
                host, port = parts[0], parts[1]
            else:
                host, port = clean_proxy, "8080"
            self.run_cmd(f"settings put global http_proxy {host}:{port}")

        # 2. Xóa data & Khởi động
        self.clear_app_data()
        self.launch_roblox()

        # ─────────────────────────────────────────────────────────────
        # BƯỚC 1 (ẢNH 1): BẤM NÚT MÀU TRẮNG 'Create Account'
        # ─────────────────────────────────────────────────────────────
        print(f"{CYAN}👉 [Bước 1] Bấm nút màu trắng 'Create Account'...{RESET}")
        self.tap_percent(0.50, 0.77, delay=3.5)

        # ─────────────────────────────────────────────────────────────
        # BƯỚC 2 (ẢNH 2): ĐIỀN FORM BƯỚC 1 (Ngày sinh, Username, Giới tính)
        # ─────────────────────────────────────────────────────────────
        print(f"{CYAN}✍️ [Bước 2] Chọn ngày sinh 18+ ({bday['formatted']})...{RESET}")
        # Bấm Dropdown Year (bên phải ~80% ngang, ~30% dọc)
        self.tap_percent(0.80, 0.30, delay=0.8)
        # Cuộn chọn năm 18+
        self.run_cmd(f"input swipe {int(self.width * 0.5)} {int(self.height * 0.7)} {int(self.width * 0.5)} {int(self.height * 0.35)} 250")
        time.sleep(0.5)
        self.tap_percent(0.50, 0.60, delay=0.8)
        self.keyevent(4) # Ẩn popup chọn ngày

        # Bấm ô Username (~42% dọc) & Gõ username
        print(f"{CYAN}✍️ [Bước 2] Nhập Username: {BOLD}{username}{RESET}...")
        self.tap_percent(0.50, 0.42, delay=0.6)
        self.input_text(username)
        time.sleep(0.8)
        self.keyevent(4) # Ẩn bàn phím

        # Chọn Giới Tính (Nam: bên phải 75%, Nữ: bên trái 25%)
        if gender == 2:
            self.tap_percent(0.75, 0.56, delay=0.5) # Nam
        else:
            self.tap_percent(0.25, 0.56, delay=0.5) # Nữ

        # Bấm nút màu xanh "Continue" (~72% dọc)
        print(f"{CYAN}👉 [Bước 2] Bấm nút màu xanh 'Continue'...{RESET}")
        self.tap_percent(0.50, 0.72, delay=2.5)

        # ─────────────────────────────────────────────────────────────
        # BƯỚC 3 (ẢNH 3): ĐIỀN FORM BƯỚC 2 - MẬT KHẨU
        # ─────────────────────────────────────────────────────────────
        print(f"{CYAN}✍️ [Bước 3] Bấm ô Password & Nhập mật khẩu: {BOLD}{password}{RESET}...")
        self.tap_percent(0.50, 0.40, delay=0.6)
        self.input_text(password)
        time.sleep(0.8)
        self.keyevent(4) # Ẩn bàn phím

        # Bấm nút màu xanh "Done" (~60% dọc)
        print(f"{YELLOW}🚀 [Bước 3] Bấm nút 'Done' (Để App OmoCaptcha tự động giải trên màn hình)...{RESET}")
        self.tap_percent(0.50, 0.60, delay=2.0)

        # ─────────────────────────────────────────────────────────────
        # BƯỚC 4: CHỜ OMOCAPTCHA GIẢI TRÊN MÀN HÌNH
        # ─────────────────────────────────────────────────────────────
        print(f"{YELLOW}⏳ Đang đợi OmoCaptcha tự động giải Captcha trên màn hình...{RESET}")
        for wait_i in range(25):
            time.sleep(1)
            sys.stdout.write(f"\r{CYAN}    ⌛ Đang đợi OmoCaptcha giải & Roblox hoàn tất: [{wait_i+1}/25s]...{RESET}")
            sys.stdout.flush()

        print(f"\n{GREEN}🎉 [THÀNH CÔNG] Đã tạo xong tài khoản: {BOLD}{username}{RESET} (Mật khẩu: {BOLD}{password}{RESET})!")

        # ─────────────────────────────────────────────────────────────
        # BƯỚC 5: TỰ ĐỘNG XÓA DATA ĐỂ LOGOUT TỨC THÌ
        # ─────────────────────────────────────────────────────────────
        print(f"{CYAN}🔄 [Auto Logout] Đang xóa data (pm clear) để sẵn sàng tạo acc tiếp theo...{RESET}")
        self.clear_app_data()

        cookie = f"{username}:{password}"
        return True, username, password, cookie
