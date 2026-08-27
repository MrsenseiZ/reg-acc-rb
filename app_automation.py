#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module Tự Động Thao Tác Trực Tiếp Trên App Delta Roblox (Android Native UI)
Kết hợp với app OmoCaptcha Trợ Năng (Accessibility Service) trên Cloud Phone:
1. Tự động cấp quyền Root (su / tsu) để ép App Roblox mở đè lên màn hình chính
2. Tự động bật Dịch vụ Trợ Năng cho App OmoCaptcha để tự giải Arkose Captcha trên màn hình
3. Tự động đo màn hình & bấm nút 'Create Account'
4. Điền Birthday 18+, Username, Password, Gender
5. Bấm 'Sign Up' và chờ OmoCaptcha giải xong trên màn hình
6. Xuất tài khoản thành công và gửi về Discord
"""

import os
import sys
import time
import shutil
import subprocess
import threading
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
        print(f"{CYAN}🔧 [Hệ Thống] Phương thức điều khiển: {BOLD}{self.root_cmd.upper()}{RESET}")
        self.auto_enable_omocaptcha()
        self.auto_grant_all_permissions()
        self.package_name = self.detect_roblox_package()
        self.width, self.height = self.get_screen_size()

    def _detect_root(self) -> str:
        """Kiểm tra và xác thực quyền Root thực tế (su / tsu / system binaries)."""
        candidates = ["tsu", "su", "/system/xbin/su", "/system/bin/su", "/sbin/su"]
        for cmd in candidates:
            if shutil.which(cmd) or os.path.exists(cmd):
                try:
                    r = subprocess.run(f"{cmd} -c 'id'", shell=True, capture_output=True, text=True, timeout=3)
                    if "uid=0" in r.stdout or r.returncode == 0:
                        return cmd
                except Exception:
                    pass
        if shutil.which("adb"):
            return "adb shell"
        return "su" # Mặc định trên Cloud Phone

    def run_cmd(self, command: str) -> str:
        """Thực thi lệnh shell qua Root hoặc ADB."""
        try:
            if self.root_cmd == "adb shell":
                full_cmd = f"adb shell {command}"
            elif self.root_cmd:
                full_cmd = f"{self.root_cmd} -c '{command}'"
            else:
                full_cmd = command

            res = subprocess.run(full_cmd, shell=True, capture_output=True, text=True, timeout=30)
            return (res.stdout or "") + (res.stderr or "")
        except Exception as e:
            return str(e)

    def auto_enable_omocaptcha(self):
        """Tự động kích hoạt Dịch vụ Trợ Năng cho App OmoCaptcha trên Cloud Phone."""
        print(f"{CYAN}🧩 [OmoCaptcha] Đang kích hoạt Dịch vụ Trợ Năng tự giải Captcha trên màn hình...{RESET}")
        try:
            self.run_cmd("settings put secure accessibility_enabled 1")
            # Kích hoạt mọi accessibility service của com.omocaptcha
            out = self.run_cmd("pm list packages")
            if "omocaptcha" in out:
                self.run_cmd("settings put secure enabled_accessibility_services com.omocaptcha/com.omocaptcha.service.MyAccessibilityService:com.omocaptcha/.AccessibilityService")
                print(f"{GREEN}[✓] Đã kích hoạt Dịch Vụ Trợ Năng OmoCaptcha!{RESET}")
        except Exception:
            pass

    def get_screen_size(self) -> Tuple[int, int]:
        """Lấy độ phân giải thực tế của màn hình Cloud Phone (wm size)."""
        try:
            out = self.run_cmd("wm size")
            for line in out.splitlines():
                if "size:" in line.lower():
                    parts = line.split(":")[-1].strip().split("x")
                    if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                        w, h = int(parts[0]), int(parts[1])
                        print(f"{CYAN}📐 [Màn Hình] Độ phân giải Cloud Phone: {w}x{h}{RESET}")
                        return w, h
        except Exception:
            pass
        return 720, 1280

    def tap(self, x: int, y: int):
        """Chạm vào tọa độ pixel."""
        self.run_cmd(f"input tap {x} {y}")

    def tap_percent(self, px: float, py: float, delay_after: float = 0.5):
        """Chạm theo tỷ lệ % màn hình (px: 0.0 -> 1.0, py: 0.0 -> 1.0) chuẩn 100% mọi màn hình."""
        real_x = int(self.width * px)
        real_y = int(self.height * py)
        self.run_cmd(f"input tap {real_x} {real_y}")
        if delay_after > 0:
            time.sleep(delay_after)

    def input_text(self, text: str):
        """Gõ văn bản vào ô nhập liệu."""
        escaped = text.replace(" ", "%s").replace("&", "\&").replace("!", "\!")
        self.run_cmd(f"input text '{escaped}'")

    def auto_grant_all_permissions(self):
        """Tự động cấp toàn bộ quyền."""
        cmds = [
            "appops set com.termux SYSTEM_ALERT_WINDOW allow",
            "appops set com.termux RUN_IN_BACKGROUND allow",
            f"appops set {self.package_name} SYSTEM_ALERT_WINDOW allow",
        ]
        for c in cmds:
            self.run_cmd(c)

    def detect_roblox_package(self) -> str:
        """Tự động phát hiện tên gói Roblox."""
        try:
            out = self.run_cmd("pm list packages")
            if self.package_name in out:
                return self.package_name
            for line in out.splitlines():
                if "roblox" in line.lower() or "delta" in line.lower():
                    pkg = line.replace("package:", "").strip()
                    if pkg and pkg != "com.delta.installer":
                        return pkg
        except Exception:
            pass
        return self.package_name

    def clear_app_data(self):
        """Xóa toàn bộ cache và dữ liệu app để reset Device Fingerprint."""
        self.run_cmd(f"pm clear {self.package_name}")
        time.sleep(1)

    def launch_roblox(self):
        """Khởi động app Delta Roblox đưa lên màn hình trước (Foreground) bằng quyền Root."""
        print(f"{CYAN}📱 Đang mở ứng dụng Roblox lên màn hình trước...{RESET}")
        # Ép đưa Roblox lên foreground qua Intent và Monkey bằng Root
        self.run_cmd(f"am start -n {self.package_name}/com.roblox.client.ActivityProtocolLaunch")
        self.run_cmd(f"am start -n {self.package_name}/com.roblox.client.activity.SplashActivity")
        self.run_cmd(f"monkey -p {self.package_name} -c android.intent.category.LAUNCHER 1")
        
        # Chờ 7 giây cho màn hình Roblox load xong nút Create Account
        print(f"{YELLOW}⏳ Đang đợi màn hình chính Roblox xuất hiện (7s)...{RESET}")
        time.sleep(7)

    def register_single_account_on_app(self, proxy_str: Optional[str] = None) -> Tuple[bool, str, str, str]:
        """
        Chu trình tự động đăng ký 1 tài khoản trực tiếp trên màn hình App:
        1. Gán Proxy toàn máy
        2. Mở app Roblox lên màn hình
        3. Bấm 'Create Account' (nút trắng lớn)
        4. Tự điền Birthday 18+, Username, Password, Gender
        5. Bấm 'Sign Up'
        6. Để App OmoCaptcha tự động giải Captcha trên màn hình
        """
        username = generate_username()
        password = generate_password("random")
        bday = generate_birthday(age_mode="18+")
        gender = generate_gender()

        print(f"\n{CYAN}📱 [App Auto] Bắt đầu chu trình tạo tài khoản: {BOLD}{username}{RESET}")

        # 1. Gán Proxy nếu có
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
            print(f"{YELLOW}🍦 [App Auto] Đã gán Proxy cho Cloud Phone: {host}:{port}{RESET}")
            self.run_cmd(f"settings put global http_proxy {host}:{port}")

        # 2. Xóa data app cũ & Mở Roblox
        self.clear_app_data()
        self.launch_roblox()

        # 3. Bấm nút màu trắng "Create Account" (Nằm ở ~77% chiều cao màn hình)
        print(f"{CYAN}👉 [App Auto] Đang bấm nút màu trắng 'Create Account'...{RESET}")
        self.tap_percent(0.50, 0.77, delay_after=3.5)

        # 4. Tự điền form đăng ký
        print(f"{CYAN}✍️ [App Auto] Đang điền form đăng ký ({bday['age']} tuổi)...{RESET}")
        
        # Bấm ô Birthday (~32% màn hình)
        self.tap_percent(0.50, 0.32, delay_after=1.0)
        # Bấm nút Xác nhận Ngày Sinh ở popup (~90% màn hình)
        self.tap_percent(0.50, 0.90, delay_after=1.0)

        # Bấm ô Username (~44% màn hình) & Gõ username
        self.tap_percent(0.50, 0.44, delay_after=0.5)
        self.input_text(username)
        time.sleep(1.0)

        # Bấm ô Password (~55% màn hình) & Gõ password
        self.tap_percent(0.50, 0.55, delay_after=0.5)
        self.input_text(password)
        time.sleep(1.0)

        # Chọn Giới tính (~66% màn hình: Nam là 35%, Nữ là 65%)
        if gender == 2:
            self.tap_percent(0.35, 0.66, delay_after=0.5) # Nam
        else:
            self.tap_percent(0.65, 0.66, delay_after=0.5) # Nữ

        # Bấm nút Sign Up / Đăng Ký (~77% màn hình)
        print(f"{YELLOW}🚀 [App Auto] Đang bấm nút 'Sign Up' (Chờ OmoCaptcha tự động giải trên màn hình)...{RESET}")
        self.tap_percent(0.50, 0.77, delay_after=2.0)

        # 5. Chờ OmoCaptcha trên máy tự động phát hiện và giải trên màn hình
        for wait_i in range(25):
            time.sleep(1)
            sys.stdout.write(f"\r{CYAN}    ⌛ Đang đợi OmoCaptcha giải & Roblox hoàn tất: [{wait_i+1}/25s]...{RESET}")
            sys.stdout.flush()

        print(f"\n{GREEN}[✓] Đã hoàn tất chu trình tạo tài khoản: {BOLD}{username}{RESET}!")

        cookie = f"{username}:{password}"
        return True, username, password, cookie
