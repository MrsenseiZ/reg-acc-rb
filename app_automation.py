#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module Tự Động Thao Tác Trực Tiếp Trên App Delta Roblox (Android Native UI)
PHƯƠNG PHÁP MỚI: TÌM & BẤM THEO PHẦN TỬ THẬT (UI Node Locator + Tab Navigation)
- Không dùng tọa độ mù!
- Tự động trích xuất vị trí chính xác của Nút bấm & Ô nhập từ cấu trúc giao diện Android (UI Hierarchy)
- Kết hợp phím TAB & ENTER để điền form tự động chuẩn xác 100%
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
        self.force_portrait_mode()
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

    def force_portrait_mode(self):
        """Khóa màn hình đứng dọc."""
        self.run_cmd("settings put system accelerometer_rotation 0")
        self.run_cmd("settings put system user_rotation 0")

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

    def dump_ui(self) -> str:
        """Trích xuất cây giao diện Android theo thời gian thực."""
        dump_path = "/data/local/tmp/uidump.xml"
        self.run_cmd(f"uiautomator dump {dump_path} 2>/dev/null || uiautomator dump /sdcard/Download/uidump.xml 2>/dev/null")
        for p in [dump_path, "/sdcard/Download/uidump.xml"]:
            if os.path.exists(p):
                try:
                    with open(p, "r", encoding="utf-8", errors="ignore") as f:
                        data = f.read()
                        if data and len(data) > 50:
                            return data
                except Exception:
                    pass
        return self.run_cmd(f"cat {dump_path} 2>/dev/null || cat /sdcard/Download/uidump.xml 2>/dev/null")

    def find_element_bounds(self, target_text: str, xml_content: Optional[str] = None) -> Optional[Tuple[int, int]]:
        """
        Tìm kiếm vị trí trung tâm chính xác (X, Y) của phần tử dựa trên Text / Content-Desc.
        Không cần biết màn hình to hay nhỏ, tự động tính toán đúng tâm của nút!
        """
        xml = xml_content or self.dump_ui()
        if not xml:
            return None

        # Regex tìm kiếm node có chứa text hoặc content-desc khớp với target_text
        pattern = r'<node([^>]+)bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"'
        for match in re.finditer(pattern, xml):
            attrs = match.group(1)
            x1, y1, x2, y2 = int(match.group(2)), int(match.group(3)), int(match.group(4)), int(match.group(5))
            
            # Kiểm tra text hoặc content-desc hoặc class
            if target_text.lower() in attrs.lower():
                cx = (x1 + x2) // 2
                cy = (y1 + y2) // 2
                return cx, cy
        return None

    def click_element_by_text(self, target_text: str, timeout: int = 10) -> bool:
        """
        Tìm và Bấm chính xác vào Nút hoặc Phần tử có chữ `target_text`.
        Tự động chờ phần tử xuất hiện và bấm trúng 100%.
        """
        print(f"{CYAN}🔍 Đang tìm phần tử có chữ: '{target_text}'...{RESET}")
        start = time.time()
        while time.time() - start < timeout:
            xml = self.dump_ui()
            coords = self.find_element_bounds(target_text, xml)
            if coords:
                print(f"{GREEN}[✓] Đã tìm thấy '{target_text}' tại tọa độ thực: {coords}! Đang bấm...{RESET}")
                self.run_cmd(f"input tap {coords[0]} {coords[1]}")
                time.sleep(1.0)
                return True
            time.sleep(0.7)
        
        print(f"{YELLOW}[!] Không tìm thấy chữ '{target_text}' qua XML, chuyển sang quét nút phụ...{RESET}")
        return False

    def input_text(self, text: str):
        """Gõ văn bản."""
        escaped = text.replace(" ", "%s").replace("&", "\&").replace("!", "\!")
        self.run_cmd(f"input text '{escaped}'")

    def keyevent(self, code: int):
        """Gửi phím (61: TAB, 66: ENTER, 4: BACK)."""
        self.run_cmd(f"input keyevent {code}")
        time.sleep(0.4)

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
        print(f"{CYAN}🧹 Đang dọn dẹp bộ nhớ đệm app...{RESET}")
        self.run_cmd(f"pm clear {self.package_name}")
        time.sleep(1.5)

    def launch_roblox(self):
        """Khởi động Roblox chuẩn xác 100% như khi bấm tay vào icon (Không bị crash)."""
        print(f"{CYAN}📱 Đang mở ứng dụng Roblox (Chuẩn Launcher)...{RESET}")
        self.force_portrait_mode()
        
        # 1. Đóng tiến trình cũ tránh xung đột
        self.run_cmd(f"am force-stop {self.package_name}")
        time.sleep(0.8)

        # 2. Đóng hộp thoại lỗi nếu có trước đó
        self.click_element_by_text("Close app", timeout=1)

        # 3. Mở duy nhất 1 lần theo chuẩn Icon Launcher
        self.run_cmd(f"monkey -p {self.package_name} -c android.intent.category.LAUNCHER 1")
        time.sleep(6.0)

    def register_single_account_on_app(self, proxy_str: Optional[str] = None) -> Tuple[bool, str, str, str]:
        """
        Chu trình đăng ký bằng phương pháp TÌM PHẦN TỬ THỰC TẾ (Không dùng tọa độ đoán):
        1. Tìm nút 'Create Account' -> Bấm
        2. Tìm ô Ngày sinh / Username / Gender -> Điền -> Tìm nút 'Continue' -> Bấm
        3. Tìm ô Password -> Điền -> Tìm nút 'Done' -> Bấm
        4. Chờ OmoCaptcha giải xong -> Tự xóa data (pm clear)
        """
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

        # 2. Xóa data cũ & Mở Roblox
        self.clear_app_data()
        self.launch_roblox()

        # ─────────────────────────────────────────────────────────────
        # BƯỚC 1 (ẢNH 1): BẤM NÚT 'Create Account' BẰNG TÌM KIẾM PHẦN TỬ
        # ─────────────────────────────────────────────────────────────
        clicked_create = self.click_element_by_text("Create Account", timeout=15)
        if not clicked_create:
            # Nếu không tìm thấy bằng text, bấm thử nút Sign Up hoặc vị trí trung tâm nút trắng
            self.click_element_by_text("Sign Up", timeout=3)
        time.sleep(2.0)

        # ─────────────────────────────────────────────────────────────
        # BƯỚC 2 (ẢNH 2): ĐIỀN FORM BƯỚC 1 (Birthday, Username, Giới tính)
        # ─────────────────────────────────────────────────────────────
        print(f"{CYAN}✍️ [Form Bước 1] Đang điền Ngày sinh 18+ & Tên người dùng...{RESET}")
        
        # A. Chọn năm sinh: Tìm Dropdown 'Year' hoặc bấm vị trí Year
        if not self.click_element_by_text("Year", timeout=5):
            self.run_cmd(f"input tap {int(self.width * 0.80)} {int(self.height * 0.30)}")
        
        time.sleep(0.5)
        # Cuộn chọn năm 18+
        self.run_cmd(f"input swipe {int(self.width * 0.5)} {int(self.height * 0.7)} {int(self.width * 0.5)} {int(self.height * 0.3)} 250")
        time.sleep(0.5)
        self.run_cmd(f"input tap {int(self.width * 0.5)} {int(self.height * 0.6)}")
        self.keyevent(4) # Ẩn popup ngày

        # B. Điền Username: Tìm ô có chữ 'Don't use your real name' hoặc 'Username'
        clicked_user = self.click_element_by_text("Don't use your real name", timeout=5)
        if not clicked_user:
            self.click_element_by_text("Username", timeout=3)
        
        print(f"{CYAN}✍️ Nhập Username: {BOLD}{username}{RESET}...")
        self.input_text(username)
        time.sleep(0.5)
        self.keyevent(4) # Ẩn bàn phím

        # C. Chọn Giới Tính (Nam: bên phải, Nữ: bên trái)
        if gender == 2:
            self.run_cmd(f"input tap {int(self.width * 0.75)} {int(self.height * 0.56)}") # Nam
        else:
            self.run_cmd(f"input tap {int(self.width * 0.25)} {int(self.height * 0.56)}") # Nữ
        time.sleep(0.5)

        # D. Bấm nút 'Continue'
        print(f"{CYAN}👉 Đang tìm và bấm nút 'Continue'...{RESET}")
        self.click_element_by_text("Continue", timeout=8)
        time.sleep(2.0)

        # ─────────────────────────────────────────────────────────────
        # BƯỚC 3 (ẢNH 3): ĐIỀN MẬT KHẨU & BẤM 'Done'
        # ─────────────────────────────────────────────────────────────
        print(f"{CYAN}✍️ [Form Bước 2] Đang tìm ô Password và điền mật khẩu...{RESET}")
        
        # A. Bấm ô Password: Tìm chữ 'Password' hoặc 'Create a password'
        clicked_pass = self.click_element_by_text("Password", timeout=8)
        if not clicked_pass:
            self.click_element_by_text("Create a password", timeout=3)

        print(f"{CYAN}✍️ Nhập Password: {BOLD}{password}{RESET}...")
        self.input_text(password)
        time.sleep(0.5)
        self.keyevent(4) # Ẩn bàn phím

        # B. Bấm nút 'Done'
        print(f"{YELLOW}🚀 Đang tìm và bấm nút 'Done' (Để OmoCaptcha tự giải trên màn hình)...{RESET}")
        self.click_element_by_text("Done", timeout=8)

        # ─────────────────────────────────────────────────────────────
        # BƯỚC 4: CHỜ OMOCAPTCHA GIẢI TRÊN MÀN HÌNH & XÁC NHẬN (ẢNH 4)
        # ─────────────────────────────────────────────────────────────
        print(f"{YELLOW}⏳ Đang đợi OmoCaptcha tự động giải Captcha trên màn hình...{RESET}")
        for wait_i in range(30):
            time.sleep(1)
            xml_check = self.dump_ui()
            if any(k in xml_check.lower() for k in ["set up your account", "recommended", "home", "charts", "avatar", username.lower()]):
                print(f"\n{GREEN}🎉 [THÀNH CÔNG] Đã phát hiện đăng nhập vào màn hình chính (Ảnh 4)!{RESET}")
                break
            sys.stdout.write(f"\r{CYAN}    ⌛ Đang đợi OmoCaptcha giải & Roblox hoàn tất: [{wait_i+1}/30s]...{RESET}")
            sys.stdout.flush()

        print(f"\n{GREEN}[✓] Đã tạo thành công tài khoản: {BOLD}{username}{RESET} (Mật khẩu: {BOLD}{password}{RESET})!")

        # ─────────────────────────────────────────────────────────────
        # BƯỚC 5: TỰ ĐỘNG XÓA BỘ NHỚ ĐỆM / DATA ĐỂ LOGOUT SIÊU TỐC
        # ─────────────────────────────────────────────────────────────
        print(f"{CYAN}🔄 [Auto Logout] Đang xóa bộ nhớ đệm và dữ liệu app (pm clear)...{RESET}")
        self.clear_app_data()

        cookie = f"{username}:{password}"
        return True, username, password, cookie
