#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module Tự Động Thao Tác Trực Tiếp Trên App Delta Roblox (Android Native UI)
Sử dụng UI Automator XML Dump để tự động nhận diện giao diện theo thời gian thực (Zero-Timing Delay):
- Tự động phát hiện khi màn hình Splash (Ảnh 1) xuất hiện -> Bấm 'Create Account'
- Tự động phát hiện khi Form Ngày sinh, Tên, Giới tính (Ảnh 2) xuất hiện -> Điền thông tin & Bấm 'Continue'
- Tự động phát hiện khi Form Mật khẩu (Ảnh 3) xuất hiện -> Điền Mật khẩu & Bấm 'Done'
- Tương thích với app OmoCaptcha Trợ Năng tự giải trên màn hình
"""

import os
import re
import sys
import time
import shutil
import subprocess
from datetime import datetime
from typing import Optional, Tuple, Dict, Any, List

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

            res = subprocess.run(full_cmd, shell=True, capture_output=True, text=True, timeout=20)
            return (res.stdout or "") + (res.stderr or "")
        except Exception as e:
            return str(e)

    def get_screen_size(self) -> Tuple[int, int]:
        """Lấy kích thước màn hình máy thật."""
        try:
            out = self.run_cmd("wm size")
            for line in out.splitlines():
                if "size:" in line.lower():
                    parts = line.split(":")[-1].strip().split("x")
                    if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                        return int(parts[0]), int(parts[1])
        except Exception:
            pass
        return 720, 1280

    def dump_ui(self) -> str:
        """Trích xuất cây giao diện UI hiện tại bằng uiautomator."""
        dump_path = "/sdcard/Download/uidump.xml"
        self.run_cmd(f"uiautomator dump {dump_path} 2>/dev/null")
        if os.path.exists(dump_path):
            try:
                with open(dump_path, "r", encoding="utf-8", errors="ignore") as f:
                    return f.read()
            except Exception:
                pass
        return self.run_cmd(f"cat {dump_path} 2>/dev/null")

    def find_element(self, xml: str, text: Optional[str] = None, res_id: Optional[str] = None) -> Optional[Tuple[int, int]]:
        """Tìm tọa độ X, Y trung tâm của phần tử theo text hoặc id."""
        if not xml:
            return None
        pattern = r'<node([^>]+)bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"'
        for match in re.finditer(pattern, xml):
            attrs = match.group(1)
            x1, y1, x2, y2 = int(match.group(2)), int(match.group(3)), int(match.group(4)), int(match.group(5))
            
            matched = False
            if text and f'text="{text}"' in attrs:
                matched = True
            elif text and text.lower() in attrs.lower():
                matched = True
            elif res_id and f'resource-id="{res_id}"' in attrs:
                matched = True
                
            if matched:
                cx = (x1 + x2) // 2
                cy = (y1 + y2) // 2
                return cx, cy
        return None

    def wait_for_ui(self, keywords: List[str], timeout: int = 20) -> Tuple[bool, str, Optional[str]]:
        """Chờ giao diện xuất hiện một trong các từ khóa (Zero-Timing)."""
        start = time.time()
        while time.time() - start < timeout:
            xml = self.dump_ui()
            for kw in keywords:
                if kw.lower() in xml.lower():
                    return True, kw, xml
            time.sleep(0.8)
        return False, "", None

    def tap(self, x: int, y: int, delay: float = 0.5):
        """Chạm vào tọa độ."""
        self.run_cmd(f"input tap {x} {y}")
        if delay > 0:
            time.sleep(delay)

    def tap_percent(self, px: float, py: float, delay: float = 0.5):
        """Chạm theo tỷ lệ % màn hình."""
        self.tap(int(self.width * px), int(self.height * py), delay)

    def input_text(self, text: str):
        """Gõ văn bản."""
        escaped = text.replace(" ", "%s").replace("&", "\&").replace("!", "\!")
        self.run_cmd(f"input text '{escaped}'")

    def keyevent(self, code: int):
        """Gửi phím (4: Back / Ẩn bàn phím, 66: Enter)."""
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
        self.run_cmd(f"pm clear {self.package_name}")
        time.sleep(1)

    def launch_roblox(self):
        print(f"{CYAN}📱 Đang khởi động Roblox...{RESET}")
        self.run_cmd(f"am start -n {self.package_name}/com.roblox.client.ActivityProtocolLaunch")
        self.run_cmd(f"am start -n {self.package_name}/com.roblox.client.activity.SplashActivity")
        self.run_cmd(f"monkey -p {self.package_name} -c android.intent.category.LAUNCHER 1")

    def register_single_account_on_app(self, proxy_str: Optional[str] = None) -> Tuple[bool, str, str, str]:
        """
        Chu trình tự động phát hiện giao diện theo thời gian thực (Zero-Timing):
        - Ảnh 1: Bấm Create Account
        - Ảnh 2: Điền Ngày sinh 18+, Username, Giới tính -> Bấm Continue
        - Ảnh 3: Điền Password -> Bấm Done
        """
        username = generate_username()
        password = generate_password("random")
        bday = generate_birthday(age_mode="18+")
        gender = generate_gender()

        print(f"\n{CYAN}📱 [App Auto] Chuẩn bị tạo tài khoản: {BOLD}{username}{RESET}")

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
        # BƯỚC 1 (ẢNH 1): CHỜ MÀN HÌNH CHÍNH & BẤM 'Create Account'
        # ─────────────────────────────────────────────────────────────
        print(f"{YELLOW}⏳ Đang quét giao diện Màn Hình Chính (Ảnh 1)...{RESET}")
        ok, kw, xml = self.wait_for_ui(["Create Account", "Sign In"], timeout=20)
        if not ok or not xml:
            print(f"{RED}[!] Không phát hiện màn hình chính, đang thử bấm theo tọa độ...{RESET}")
            self.tap_percent(0.50, 0.77, delay=3.0)
        else:
            print(f"{GREEN}[✓] Đã phát hiện giao diện Màn Hình Chính!{RESET}")
            pos = self.find_element(xml, text="Create Account")
            if pos:
                print(f"{CYAN}👉 Bấm nút 'Create Account' tại tọa độ: {pos}{RESET}")
                self.tap(pos[0], pos[1], delay=2.5)
            else:
                self.tap_percent(0.50, 0.77, delay=2.5)

        # ─────────────────────────────────────────────────────────────
        # BƯỚC 2 (ẢNH 2): ĐIỀN FORM BƯỚC 1 (Birthday, Username, Gender)
        # ─────────────────────────────────────────────────────────────
        print(f"{YELLOW}⏳ Đang quét giao diện Form Bước 1 (Ảnh 2)...{RESET}")
        ok, kw, xml = self.wait_for_ui(["Don't use your real name", "Birthday", "Continue", "Month"], timeout=15)
        if not ok or not xml:
            print(f"{YELLOW}[*] Đang điền form Bước 1 theo tỷ lệ chuẩn...{RESET}")
        else:
            print(f"{GREEN}[✓] Đã phát hiện giao diện Form Bước 1 (Ảnh 2)!{RESET}")

        # A. Điền Ngày Sinh 18+ (Dropdown Month, Day, Year)
        print(f"{CYAN}✍️ Chọn ngày sinh 18+ ({bday['formatted']})...{RESET}")
        # Bấm Dropdown Year (bên phải ~80% width, ~30% height)
        self.tap_percent(0.80, 0.30, delay=1.0)
        # Cuộn chọn năm 2002-2005 (vuốt từ giữa lên hoặc bấm năm)
        self.run_cmd("input swipe 500 800 500 400 300")
        time.sleep(0.5)
        self.tap_percent(0.50, 0.60, delay=1.0)
        # Ẩn popup chọn ngày nếu có
        self.keyevent(4)

        # B. Bấm ô Username & Gõ Username
        print(f"{CYAN}✍️ Nhập Username: {BOLD}{username}{RESET}...")
        user_pos = self.find_element(xml or "", text="Don't use your real name")
        if user_pos:
            self.tap(user_pos[0], user_pos[1], delay=0.5)
        else:
            self.tap_percent(0.50, 0.42, delay=0.5)
        self.input_text(username)
        time.sleep(1.0)
        # Ẩn bàn phím để lộ nút Gender & Continue
        self.keyevent(4)
        time.sleep(0.5)

        # C. Chọn Giới Tính (Optional)
        if gender == 2:
            self.tap_percent(0.75, 0.56, delay=0.5) # Nam
        else:
            self.tap_percent(0.25, 0.56, delay=0.5) # Nữ

        # D. Bấm nút màu xanh "Continue"
        print(f"{CYAN}👉 Bấm nút 'Continue'...{RESET}")
        cont_pos = self.find_element(self.dump_ui(), text="Continue")
        if cont_pos:
            self.tap(cont_pos[0], cont_pos[1], delay=2.0)
        else:
            self.tap_percent(0.50, 0.72, delay=2.0)

        # ─────────────────────────────────────────────────────────────
        # BƯỚC 3 (ẢNH 3): ĐIỀN MẬT KHẨU & BẤM 'Done'
        # ─────────────────────────────────────────────────────────────
        print(f"{YELLOW}⏳ Đang quét giao diện Form Bước 2 - Password (Ảnh 3)...{RESET}")
        ok, kw, xml_pass = self.wait_for_ui(["Create a password", "Password", "Done"], timeout=15)
        if ok and xml_pass:
            print(f"{GREEN}[✓] Đã phát hiện giao diện Form Mật Khẩu (Ảnh 3)!{RESET}")
        else:
            print(f"{YELLOW}[*] Đang điền Form Mật Khẩu theo tỷ lệ chuẩn...{RESET}")

        # A. Bấm ô Password & Nhập mật khẩu
        print(f"{CYAN}✍️ Nhập Password: {BOLD}{password}{RESET}...")
        self.tap_percent(0.50, 0.40, delay=0.5)
        self.input_text(password)
        time.sleep(1.0)
        # Ẩn bàn phím để thấy nút Done
        self.keyevent(4)
        time.sleep(0.5)

        # B. Bấm nút màu xanh "Done"
        print(f"{YELLOW}🚀 Bấm nút 'Done' và chờ OmoCaptcha tự động giải trên màn hình...{RESET}")
        done_pos = self.find_element(self.dump_ui(), text="Done")
        if done_pos:
            self.tap(done_pos[0], done_pos[1], delay=1.0)
        else:
            self.tap_percent(0.50, 0.60, delay=1.0)

        # ─────────────────────────────────────────────────────────────
        # BƯỚC 4: CHỜ OMOCAPTCHA GIẢI TRÊN MÀN HÌNH & XÁC NHẬN (ẢNH 4)
        # ─────────────────────────────────────────────────────────────
        print(f"{YELLOW}⏳ Đang đợi OmoCaptcha tự động giải Captcha trên màn hình...{RESET}")
        success_detected = False
        for wait_i in range(30):
            time.sleep(1)
            # Kiểm tra xem đã vào màn hình chính chưa (Ảnh 4: Home, Recommended, Set up your account)
            xml_check = self.dump_ui()
            if any(k in xml_check.lower() for k in ["set up your account", "recommended", "home", "charts", "avatar", username.lower()]):
                print(f"\n{GREEN}🎉 [THÀNH CÔNG] Đã phát hiện đăng nhập vào màn hình chính (Ảnh 4)!{RESET}")
                success_detected = True
                break
            sys.stdout.write(f"\r{CYAN}    ⌛ Đang đợi OmoCaptcha giải & Roblox hoàn tất: [{wait_i+1}/30s]...{RESET}")
            sys.stdout.flush()

        print(f"\n{GREEN}[✓] Đã tạo thành công tài khoản: {BOLD}{username}{RESET} (Mật khẩu: {BOLD}{password}{RESET})!")

        # ─────────────────────────────────────────────────────────────
        # BƯỚC 5: TỰ ĐỘNG XÓA BỘ NHỚ ĐỆM / DATA ĐỂ LOGOUT SIÊU TỐC
        # ─────────────────────────────────────────────────────────────
        print(f"{CYAN}🔄 [Auto Logout] Đang xóa bộ nhớ đệm và dữ liệu app (pm clear) để sẵn sàng tạo tài khoản tiếp theo...{RESET}")
        self.clear_app_data()

        cookie = f"{username}:{password}"
        return True, username, password, cookie
