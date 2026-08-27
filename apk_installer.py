#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module Tự Động Tải & Cài Đặt APK Roblox / Delta Trên Termux & Cloud Phone
Hỗ trợ:
1. Tải qua Curl / Wget / Requests (Bypass Cloudflare)
2. Tự động quét và cài đặt nếu file đã có trong /sdcard/Download/
3. Tự động mở trình duyệt Cloud Phone nếu bị chặn IP
4. Cài đặt qua: Root (su/tsu), ADB Shell, hoặc Package Installer.
"""

import os
import sys
import glob
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

    def find_local_apk(self) -> Optional[str]:
        """Tự động tìm kiếm file APK có sẵn trong thư mục hiện tại hoặc /sdcard/Download/"""
        search_dirs = [".", "/sdcard/Download", "/sdcard/Downloads", "/storage/emulated/0/Download"]
        patterns = [self.filename, "*Delta*.apk", "*delta*.apk", "*roblox*.apk", "*Roblox*.apk"]
        
        for d in search_dirs:
            if not os.path.exists(d):
                continue
            for pat in patterns:
                matches = glob.glob(os.path.join(d, pat))
                for m in matches:
                    if os.path.isfile(m) and os.path.getsize(m) > 10 * 1024 * 1024:
                        return os.path.abspath(m)
        return None

    def download_apk(self) -> bool:
        """Tải APK với thanh tiến trình trực quan (Bypass Cloudflare bằng Curl/Wget)."""
        # Kiểm tra nếu máy đã có sẵn file tải về từ trước
        existing_apk = self.find_local_apk()
        if existing_apk:
            print(f"{GREEN}[✓] Tìm thấy file APK có sẵn: {existing_apk} ({os.path.getsize(existing_apk)/(1024*1024):.1f} MB)! Đang tiến hành cài đặt...{RESET}")
            self.apk_path = existing_apk
            return True

        if not self.apk_url:
            print(f"{RED}[!] Không có link tải APK trong cấu hình!{RESET}")
            return False

        print(f"\n{CYAN}[+] Đang kết nối tới máy chủ tải APK: {self.apk_url}{RESET}")

        # 1. Thử tải bằng CURL chuyên dụng (Chống Cloudflare 403)
        if shutil.which("curl"):
            try:
                print(f"{CYAN}[+] Đang tải APK bằng CURL (Chống chặn Cloudflare)...{RESET}")
                ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
                cmd = ["curl", "-k", "-L", "-A", ua, "--progress-bar", "-o", self.apk_path, self.apk_url]
                ret = subprocess.run(cmd)
                if ret.returncode == 0 and os.path.exists(self.apk_path) and os.path.getsize(self.apk_path) > 10 * 1024 * 1024:
                    print(f"\n{GREEN}[✓] Đã tải thành công APK ({os.path.getsize(self.apk_path)/(1024*1024):.1f} MB) về: {self.apk_path}{RESET}")
                    return True
            except Exception as e:
                print(f"{YELLOW}[!] Curl gặp lỗi: {e}, thử phương án tiếp theo...{RESET}")

        # 2. Thử tải bằng WGET
        if shutil.which("wget"):
            try:
                print(f"{CYAN}[+] Đang tải APK bằng WGET...{RESET}")
                ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
                cmd = ["wget", "--no-check-certificate", "-U", ua, "-O", self.apk_path, self.apk_url]
                ret = subprocess.run(cmd)
                if ret.returncode == 0 and os.path.exists(self.apk_path) and os.path.getsize(self.apk_path) > 10 * 1024 * 1024:
                    print(f"\n{GREEN}[✓] Đã tải thành công APK về: {self.apk_path}{RESET}")
                    return True
            except Exception:
                pass

        # 3. Nếu máy chủ Cloudflare chặn IP máy ảo -> Tự động mở Trình duyệt Cloud Phone để tải
        print(f"\n{YELLOW}[!] Máy chủ link APK đang bật Cloudflare chặn tải trực tiếp qua dòng lệnh.{RESET}")
        print(f"{CYAN}🌐 Đang tự động mở Trình duyệt trên Cloud Phone để tải về...{RESET}")
        
        try:
            if shutil.which("termux-open-url"):
                subprocess.run(["termux-open-url", self.apk_url])
            else:
                subprocess.run(["am", "start", "-a", "android.intent.action.VIEW", "-d", self.apk_url])
            print(f"{GREEN}[✓] Đã mở link trên trình duyệt! Bạn chỉ cần bấm Tải về trên trình duyệt Cloud Phone.{RESET}")
        except Exception:
            pass

        print(f"\n{YELLOW}💡 Mẹo: Bạn chỉ cần mở Chrome trên Cloud Phone tải file APK về thư mục Download, Tool sẽ tự động nhận diện và cài đặt!{RESET}")
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
        if not os.path.exists(self.apk_path) or os.path.getsize(self.apk_path) < 1024 * 1024:
            local = self.find_local_apk()
            if local:
                self.apk_path = local
            else:
                print(f"{RED}[!] Không tìm thấy file APK hợp lệ để cài đặt!{RESET}")
                return False

        print(f"\n{YELLOW}[*] Đang thực hiện cài đặt {os.path.basename(self.apk_path)}...{RESET}")

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
