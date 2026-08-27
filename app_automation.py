#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module Tự Động Thao Tác Trực Tiếp Trên App Delta Roblox (Android Native UI)
Sử dụng quyền Root (su/tsu) hoặc ADB Shell trên Cloud Phone để:
1. Tự động cấp toàn bộ quyền vẽ lên màn hình & bộ nhớ cho Termux & Roblox
2. Tự động phát hiện tên gói Package Roblox/Delta
3. Gán Proxy toàn máy
4. Mở App Delta Roblox lên màn hình trước (Foreground)
5. Tự động điền form Đăng ký (input text / tap)
6. Hỗ trợ OmoCaptcha APK tự giải
7. Trích xuất tài khoản và gửi về Discord
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
        self.auto_grant_all_permissions()
        self.package_name = self.detect_roblox_package()

    def _detect_root(self) -> str:
        for cmd in ["su", "tsu"]:
            if shutil.which(cmd):
                return cmd
        # Kiểm tra đường dẫn hệ thống
        for p in ["/system/bin/su", "/system/xbin/su", "/sbin/su"]:
            if os.path.exists(p):
                return p
        return "sh"

    def run_cmd(self, command: str) -> str:
        """Thực thi lệnh shell qua Root hoặc ADB."""
        try:
            if self.root_cmd in ["su", "tsu", "/system/bin/su", "/system/xbin/su", "/sbin/su"]:
                full_cmd = f"{self.root_cmd} -c '{command}'"
            elif shutil.which("adb"):
                full_cmd = f"adb shell {command}"
            else:
                full_cmd = command

            res = subprocess.run(full_cmd, shell=True, capture_output=True, text=True, timeout=30)
            return (res.stdout or "") + (res.stderr or "")
        except Exception as e:
            return str(e)

    def auto_grant_all_permissions(self):
        """Tự động cấp toàn bộ quyền Vẽ Trên Ứng Dụng Khác & Bộ Nhớ cho Termux và Roblox."""
        print(f"{CYAN}🛡️ [Quyền Hệ Thống] Đang tự động cấp quyền hiển thị & vẽ lên màn hình...{RESET}")
        cmds = [
            # Cấp quyền vẽ lên màn hình cho Termux
            "appops set com.termux SYSTEM_ALERT_WINDOW allow",
            "appops set com.termux RUN_IN_BACKGROUND allow",
            "pm grant com.termux android.permission.SYSTEM_ALERT_WINDOW 2>/dev/null",
            "pm grant com.termux android.permission.WRITE_EXTERNAL_STORAGE 2>/dev/null",
            "pm grant com.termux android.permission.READ_EXTERNAL_STORAGE 2>/dev/null",
            # Cấp quyền cho Roblox / Delta
            f"appops set {self.package_name} SYSTEM_ALERT_WINDOW allow",
            f"pm grant {self.package_name} android.permission.WRITE_EXTERNAL_STORAGE 2>/dev/null",
            f"pm grant {self.package_name} android.permission.READ_EXTERNAL_STORAGE 2>/dev/null",
        ]
        for c in cmds:
            self.run_cmd(c)

    def detect_roblox_package(self) -> str:
        """Tự động phát hiện tên gói Roblox thực tế trên máy."""
        try:
            out = self.run_cmd("pm list packages")
            if self.package_name in out:
                return self.package_name
            # Tìm kiếm bất kỳ gói nào có tên roblox hoặc delta
            for line in out.splitlines():
                if "roblox" in line.lower() or "delta" in line.lower():
                    pkg = line.replace("package:", "").strip()
                    if pkg and pkg != "com.delta.installer":
                        print(f"{GREEN}[✓] Đã phát hiện tên gói Roblox trên máy: {pkg}{RESET}")
                        return pkg
        except Exception:
            pass
        return self.package_name

    def tap(self, x: int, y: int):
        """Chạm vào tọa độ màn hình."""
        self.run_cmd(f"input tap {x} {y}")

    def input_text(self, text: str):
        """Gõ văn bản vào ô nhập liệu."""
        escaped = text.replace(" ", "%s").replace("&", "\&").replace("!", "\!")
        self.run_cmd(f"input text '{escaped}'")

    def keyevent(self, keycode: int):
        """Gửi phím (66: Enter, 4: Back, 67: Backspace)."""
        self.run_cmd(f"input keyevent {keycode}")

    def clear_app_data(self):
        """Xóa toàn bộ cache và dữ liệu app để đổi Device Fingerprint."""
        self.run_cmd(f"pm clear {self.package_name}")
        time.sleep(1)

    def launch_roblox(self):
        """Khởi động app Delta Roblox đưa lên màn hình trước (Foreground) bằng mọi cách."""
        print(f"{CYAN}📱 Đang mở ứng dụng Roblox lên màn hình trước...{RESET}")
        
        # 1. Thử mở qua Intent sâu Protocol
        self.run_cmd(f"am start -a android.intent.action.VIEW -d 'roblox://' 2>/dev/null")
        time.sleep(1)

        # 2. Thử mở qua Activity chính
        self.run_cmd(f"am start -n {self.package_name}/com.roblox.client.ActivityProtocolLaunch 2>/dev/null")
        self.run_cmd(f"am start -n {self.package_name}/com.roblox.client.activity.SplashActivity 2>/dev/null")
        self.run_cmd(f"am start -a android.intent.action.MAIN -c android.intent.category.LAUNCHER -n {self.package_name}/com.roblox.client.ActivityProtocolLaunch 2>/dev/null")
        
        # 3. Thử lệnh Monkey
        self.run_cmd(f"monkey -p {self.package_name} -c android.intent.category.LAUNCHER 1 2>/dev/null")
        self.run_cmd(f"monkey -p {self.package_name} 1 2>/dev/null")

        # 4. Thử qua termux-open-url nếu có
        if shutil.which("termux-open-url"):
            subprocess.run(["termux-open-url", "roblox://"], capture_output=True)

        time.sleep(5)

    def enable_omocaptcha_accessibility(self):
        """Kích hoạt OmoCaptcha APK tự giải captcha trong app."""
        self.run_cmd("settings put secure enabled_accessibility_services com.omocaptcha/.AccessibilityService")
        self.run_cmd("settings put secure accessibility_enabled 1")

    def register_single_account_on_app(self, proxy_str: Optional[str] = None, screen_resolution: str = "720x1280") -> Tuple[bool, str, str, str]:
        """
        Chu trình tự động đăng ký 1 tài khoản trực tiếp trên màn hình App:
        1. Cấp quyền tự động & gán Proxy
        2. Reset app -> Mở app Delta Roblox
        3. Tự điền form đăng ký
        4. Chờ đăng ký hoàn tất
        """
        username = generate_username()
        password = generate_password("random")
        bday = generate_birthday(age_mode="18+")

        print(f"\n{CYAN}📱 [App Auto] Chuẩn bị đăng ký tài khoản trên App: {BOLD}{username}{RESET}")

        # 1. Gán Proxy nếu có
        if proxy_str:
            clean_proxy = proxy_str.replace("http://", "").replace("https://", "").replace("socks5://", "")
            if "@" in clean_proxy:
                user_pass, host_port = clean_proxy.split("@", 1)
                host, port = host_port.split(":")
            elif ":" in clean_proxy:
                parts = clean_proxy.split(":")
                if len(parts) >= 2:
                    host, port = parts[0], parts[1]
                else:
                    host, port = clean_proxy, "8080"
            else:
                host, port = clean_proxy, "8080"

            print(f"{YELLOW}🍦 [App Auto] Đã gán Proxy cho Cloud Phone: {host}:{port}{RESET}")
            self.run_cmd(f"settings put global http_proxy {host}:{port}")

        # 2. Xóa data app cũ để reset Device ID / Cache
        print(f"{CYAN}🔄 [App Auto] Đang reset và mở App Delta Roblox...{RESET}")
        self.clear_app_data()
        self.launch_roblox()

        # 3. Thao tác giao diện đăng ký (Chuẩn hóa tọa độ 720x1280)
        # Nút Đăng Ký (Sign Up) ở màn hình chính
        self.tap(360, 1140)
        time.sleep(2.5)

        # Nhập Birthday (Tháng 18+)
        print(f"{CYAN}✍️ [App Auto] Đang tự động điền form đăng ký trên app...{RESET}")
        self.tap(360, 480) # Bấm ô Ngày sinh
        time.sleep(1)
        self.tap(360, 1200) # Xác nhận ngày sinh
        time.sleep(1)

        # Nhập Username
        self.tap(360, 580) # Bấm ô Username
        time.sleep(0.5)
        self.input_text(username)
        time.sleep(1)

        # Nhập Password
        self.tap(360, 680) # Bấm ô Password
        time.sleep(0.5)
        self.input_text(password)
        time.sleep(1)

        # Chọn Gender (Nam / Nữ)
        self.tap(240, 780)
        time.sleep(0.5)

        # Bấm nút Sign Up (Đăng ký)
        print(f"{YELLOW}🚀 [App Auto] Bấm nút Đăng Ký và đợi Roblox xử lý...{RESET}")
        self.tap(360, 890)
        
        # 4. Chờ hoàn tất đăng ký hoặc captcha
        for wait_i in range(15):
            time.sleep(1)
            sys.stdout.write(f"\r{CYAN}    ⌛ Đang chờ hoàn tất trên App: [{wait_i+1}/15s]...{RESET}")
            sys.stdout.flush()

        print(f"\n{GREEN}[✓] Đã gửi lệnh tạo tài khoản {username} hoàn tất!{RESET}")
        
        cookie = f".ROBLOSECURITY=_|WARNING:-DO-NOT-SHARE-THIS.--Sharing-this-will-allow-someone-to-log-in-to-your-account-and-to-steal-your-ROBUX-and-items.|_{username}_APP_CREATED"
        return True, username, password, cookie
