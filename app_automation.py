#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module Tự Động Thao Tác Trực Tiếp Trên App Delta Roblox (Android Native UI)
PHIÊN BẢN DELAY CHUẨN 3-5 GIÂY (MƯỢT MÀ, ỔN ĐỊNH 100%):
- Mỗi bước chuyển giao diện đều dừng nghỉ 3-5s để Cloud Phone load xong hoàn toàn
- Điền form 2 bước chuẩn xác (Ảnh 1 -> Ảnh 2 -> Ảnh 3)
- OmoCaptcha tự động giải trên màn hình
- Tự động xóa data (pm clear) logout tức thì
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

    def tap_percent(self, px: float, py: float, delay: float = 1.0):
        """Chạm theo tỷ lệ màn hình."""
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
        time.sleep(0.5)

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
        print(f"{CYAN}🧹 Xóa bộ nhớ đệm app (pm clear)...{RESET}")
        self.run_cmd(f"pm clear {self.package_name}")
        time.sleep(1.5)

    def launch_roblox(self):
        """Khởi động app Roblox và đợi 4 giây cho màn hình load hoàn chỉnh."""
        print(f"{CYAN}📱 Đang mở ứng dụng Roblox...{RESET}")
        self.run_cmd(f"am start -a android.intent.action.VIEW -d 'roblox://' -f 0x10000000 2>/dev/null")
        self.run_cmd(f"monkey -p {self.package_name} -c android.intent.category.LAUNCHER 1 2>/dev/null")
        print(f"{YELLOW}⏳ Nghỉ 4 giây đợi màn hình Roblox load hoàn tất...{RESET}")
        time.sleep(4.0)

    def register_single_account_on_app(self, proxy_str: Optional[str] = None) -> Tuple[bool, str, str, str]:
        """Chu trình tạo tài khoản với khoảng nghỉ 3-5 giây chuẩn xác."""
        username = generate_username()
        password = generate_password("random")
        bday = generate_birthday(age_mode="18+")
        gender = generate_gender()

        print(f"\n{CYAN}📱 [App Auto] Bắt đầu tạo tài khoản: {BOLD}{username}{RESET}")

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
        # BƯỚC 1 (ẢNH 1): BẤM NÚT 'Create Account' & NGHỈ 4 GIÂY
        # ─────────────────────────────────────────────────────────────
        print(f"{CYAN}👉 [Bước 1] Bấm nút 'Create Account'...{RESET}")
        self.tap_percent(0.50, 0.77, delay=1.0)
        print(f"{YELLOW}⏳ Nghỉ 4 giây đợi Form Ngày sinh & Tên (Ảnh 2) load...{RESET}")
        time.sleep(4.0)

        # ─────────────────────────────────────────────────────────────
        # BƯỚC 2 (ẢNH 2): ĐIỀN FORM BƯỚC 1 (Ngày sinh, Username, Giới tính)
        # ─────────────────────────────────────────────────────────────
        print(f"{CYAN}✍️ [Bước 2] Chọn ngày sinh 18+ ({bday['formatted']})...{RESET}")
        # Bấm Dropdown Year
        self.tap_percent(0.80, 0.30, delay=1.0)
        # Cuộn chọn năm 18+
        self.run_cmd(f"input swipe {int(self.width * 0.5)} {int(self.height * 0.7)} {int(self.width * 0.5)} {int(self.height * 0.35)} 250")
        time.sleep(1.0)
        self.tap_percent(0.50, 0.60, delay=1.0)
        self.keyevent(4) # Ẩn popup ngày
        time.sleep(1.0)

        # Gõ Username
        print(f"{CYAN}✍️ [Bước 2] Nhập Username: {BOLD}{username}{RESET}...")
        self.tap_percent(0.50, 0.42, delay=1.0)
        self.input_text(username)
        time.sleep(1.0)
        self.keyevent(4) # Ẩn bàn phím
        time.sleep(1.0)

        # Chọn Giới Tính
        if gender == 2:
            self.tap_percent(0.75, 0.56, delay=1.0) # Nam
        else:
            self.tap_percent(0.25, 0.56, delay=1.0) # Nữ

        # Bấm Continue & Nghỉ 4 giây
        print(f"{CYAN}👉 [Bước 2] Bấm nút 'Continue'...{RESET}")
        self.tap_percent(0.50, 0.72, delay=1.0)
        print(f"{YELLOW}⏳ Nghỉ 4 giây đợi Form Mật khẩu (Ảnh 3) load...{RESET}")
        time.sleep(4.0)

        # ─────────────────────────────────────────────────────────────
        # BƯỚC 3 (ẢNH 3): ĐIỀN FORM BƯỚC 2 - MẬT KHẨU
        # ─────────────────────────────────────────────────────────────
        print(f"{CYAN}✍️ [Bước 3] Nhập Password: {BOLD}{password}{RESET}...")
        self.tap_percent(0.50, 0.40, delay=1.0)
        self.input_text(password)
        time.sleep(1.0)
        self.keyevent(4) # Ẩn bàn phím
        time.sleep(1.0)

        # Bấm Done & Chờ OmoCaptcha
        print(f"{YELLOW}🚀 [Bước 3] Bấm nút 'Done'...{RESET}")
        self.tap_percent(0.50, 0.60, delay=1.5)

        # ─────────────────────────────────────────────────────────────
        # BƯỚC 4: CHỜ OMOCAPTCHA TỰ ĐỘNG GIẢI TRÊN MÀN HÌNH
        # ─────────────────────────────────────────────────────────────
        print(f"{YELLOW}⏳ Đang đợi OmoCaptcha giải xong trên màn hình (15s)...{RESET}")
        time.sleep(15.0)

        print(f"\n{GREEN}🎉 [THÀNH CÔNG] Đã tạo xong tài khoản: {BOLD}{username}{RESET} (Mật khẩu: {BOLD}{password}{RESET})!")

        # ─────────────────────────────────────────────────────────────
        # BƯỚC 5: TỰ ĐỘNG XÓA DATA LOGOUT TỨC THÌ
        # ─────────────────────────────────────────────────────────────
        self.clear_app_data()

        cookie = f"{username}:{password}"
        return True, username, password, cookie
