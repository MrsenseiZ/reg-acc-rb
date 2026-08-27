#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module Tự Động Tải & Cài Đặt APK Roblox / Delta Trên Termux & Cloud Phone
Hỗ trợ cài qua: Root (su/tsu), ADB Shell, hoặc Termux Package Installer Intent.
"""

import os
import sys
import time
import shutil
import subprocess
import requests

CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
RESET = "\033[0m"

class ApkInstaller:
    def __init__(self, apk_url: str, filename: str = "Delta-Roblox.apk", package_name: str = "com.roblox.client"):
        self.apk_url = apk_url.strip()
        self.filename = filename
        self.package_name = package_name
        self.apk_path = os.path.abspath(self.filename)

    def download_apk(self) -> bool:
        """Tải APK với thanh tiến trình trực quan."""
        if not self.apk_url:
            print(f"{RED}[!] Không có link tải APK trong cấu hình!{RESET}")
            return False

        print(f"\n{CYAN}[+] Đang kết nối tới máy chủ tải APK: {self.apk_url}{RESET}")
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Linux; Android 14; Mobile) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Mobile Safari/537.36"
            }
            res = requests.get(self.apk_url, headers=headers, stream=True, timeout=30)
            if res.status_code != 200:
                print(f"{RED}[!] Lỗi tải APK (HTTP {res.status_code}){RESET}")
                return False

            total_size = int(res.headers.get('content-length', 0))
            downloaded = 0
            start_time = time.time()

            print(f"{CYAN}[+] Đang tải về file: {self.filename} ({total_size / (1024*1024):.2f} MB)...{RESET}")

            with open(self.apk_path, "wb") as f:
                for chunk in res.iter_content(chunk_size=1024 * 128):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            percent = (downloaded / total_size) * 100
                            mb_down = downloaded / (1024 * 1024)
                            mb_total = total_size / (1024 * 1024)
                            speed = (downloaded / 1024) / max(0.1, time.time() - start_time)
                            sys.stdout.write(f"\r{CYAN}    ⏳ Tiến độ: [{percent:5.1f}%] {mb_down:.1f}/{mb_total:.1f} MB ({speed:.0f} KB/s){RESET}")
                            sys.stdout.flush()

            print(f"\n{GREEN}[✓] Đã tải thành công APK về: {self.apk_path}{RESET}")
            return True

        except Exception as e:
            print(f"\n{RED}[!] Lỗi trong quá trình tải APK: {e}{RESET}")
            return False

    def is_installed(self) -> bool:
        """Kiểm tra app Roblox đã được cài đặt trên máy chưa."""
        try:
            res = subprocess.run(["pm", "list", "packages", self.package_name], capture_output=True, text=True)
            if self.package_name in res.stdout:
                return True
        except Exception:
            pass
        return False

    def install_apk(self) -> bool:
        """Cài đặt file APK lên thiết bị Android / Cloud Phone."""
        if not os.path.exists(self.apk_path):
            print(f"{RED}[!] Không tìm thấy file {self.apk_path} để cài đặt!{RESET}")
            return False

        print(f"\n{YELLOW}[*] Đang thực hiện cài đặt {self.filename}...{RESET}")

        # Phương pháp 1: Cài đặt thông qua Root (su / tsu - Phổ biến trên Cloud Phone)
        for root_cmd in ["su", "tsu"]:
            if shutil.which(root_cmd):
                try:
                    print(f"{CYAN} -> Đang thử quyền Root ({root_cmd}) để cài đặt trực tiếp...{RESET}")
                    cmd = f"{root_cmd} -c 'pm install -r -d {self.apk_path}'"
                    ret = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=90)
                    if "Success" in ret.stdout or "Success" in ret.stderr:
                        print(f"{GREEN}[✓] Cài đặt APK thành công qua quyền Root!{RESET}")
                        return True
                except Exception:
                    pass

        # Phương pháp 2: Cài đặt thông qua ADB Shell (Nếu có kết nối localhost)
        if shutil.which("adb"):
            try:
                print(f"{CYAN} -> Đang thử cài đặt qua ADB Shell...{RESET}")
                ret = subprocess.run(["adb", "install", "-r", "-d", self.apk_path], capture_output=True, text=True, timeout=90)
                if "Success" in ret.stdout or "Success" in ret.stderr:
                    print(f"{GREEN}[✓] Cài đặt APK thành công qua ADB!{RESET}")
                    return True
            except Exception:
                pass

        # Phương pháp 3: Gọi trình cài đặt chuẩn Android (termux-open / package-installer intent)
        try:
            print(f"{CYAN} -> Đang mở Trình cài đặt Gói Android (Package Installer)...{RESET}")
            # Chuyển APK ra thư mục public /sdcard/Download để hệ điều hành có quyền đọc
            sdcard_dest = f"/sdcard/Download/{self.filename}"
            try:
                shutil.copyfile(self.apk_path, sdcard_dest)
                install_target = sdcard_dest
            except Exception:
                install_target = self.apk_path

            if shutil.which("termux-open"):
                subprocess.run(["termux-open", "--view", install_target])
                print(f"{GREEN}[✓] Đã kích hoạt giao diện cài đặt trên màn hình Cloud Phone! Vui lòng bấm Cài Đặt (Install).{RESET}")
                return True
            else:
                subprocess.run(["am", "start", "-a", "android.intent.action.VIEW", "-d", f"file://{install_target}", "-t", "application/vnd.android.package-archive"])
                print(f"{GREEN}[✓] Đã kích hoạt Package Installer qua Intent! Vui lòng bấm Install trên màn hình.{RESET}")
                return True
        except Exception as e:
            print(f"{RED}[!] Không thể kích hoạt cài đặt tự động: {e}{RESET}")

        return False

    def launch_app(self):
        """Khởi động app Roblox."""
        print(f"{CYAN}[+] Đang khởi động app {self.package_name}...{RESET}")
        try:
            subprocess.run(["monkey", "-p", self.package_name, "-c", "android.intent.category.LAUNCHER", "1"], capture_output=True)
            print(f"{GREEN}[✓] Đã gửi lệnh mở app Roblox.{RESET}")
        except Exception as e:
            print(f"{RED}[!] Lỗi mở app: {e}{RESET}")
