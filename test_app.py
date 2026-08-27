#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script Kiểm Tra & Tinh Chỉnh Thao Tác Từng Bước (Interactive Step-by-Step Tester)
Giúp kiểm tra từng nút bấm trên màn hình thực tế của Cloud Phone trong 30 giây!
"""

import os
import sys
import time
from app_automation import RobloxAppAutomator, CYAN, GREEN, YELLOW, RED, BOLD, RESET

def main():
    print(f"\n{YELLOW}══════════════════════════════════════════════════════════════{RESET}")
    print(f"{YELLOW}🛠️  CÔNG CỤ KIỂM TRA & TEST TRỰC TIẾP MÀN HÌNH CLOUD PHONE    {RESET}")
    print(f"{YELLOW}══════════════════════════════════════════════════════════════{RESET}\n")

    auto = RobloxAppAutomator()
    print(f" • Tên gói app: {CYAN}{auto.package_name}{RESET}")
    print(f" • Kích thước màn hình: {CYAN}{auto.width}x{auto.height}{RESET}")
    print(f" • Phương thức: {CYAN}{auto.root_cmd}{RESET}\n")

    # BƯỚC 1: XÓA DATA & MỞ ROBLOX
    print(f"{BOLD}[1/4] 🚀 TEST MỞ APP ROBLOX:{RESET}")
    auto.clear_app_data()
    auto.launch_roblox()
    time.sleep(4)
    input(f"{CYAN}👉 Nhìn vào màn hình: App Roblox đã mở lên màn hình chính chưa? Bấm Enter để test bấm nút 'Create Account'...{RESET}")

    # BƯỚC 2: BẤM NÚT CREATE ACCOUNT
    print(f"\n{BOLD}[2/4] 👉 TEST BẤM NÚT 'Create Account':{RESET}")
    ok = auto.click_element_by_text("Create Account", timeout=6)
    if not ok:
        print(f"{YELLOW}[*] Bấm theo tỷ lệ màn hình (0.50, 0.77)...{RESET}")
        auto.tap_percent(0.50, 0.77, delay=2.0)
    
    time.sleep(2)
    input(f"{CYAN}👉 Nhìn vào màn hình: Đã chuyển sang Form Ngày Sinh & Tên (Ảnh 2) chưa? Bấm Enter để test điền thông tin...{RESET}")

    # BƯỚC 3: ĐIỀN FORM BƯỚC 1 & BẤM CONTINUE
    print(f"\n{BOLD}[3/4] ✍️ TEST ĐIỀN FORM BƯỚC 1 & BẤM 'Continue':{RESET}")
    # Chọn năm sinh
    auto.tap_percent(0.80, 0.30, delay=0.8)
    auto.run_cmd("input swipe 500 800 500 400 250")
    time.sleep(0.5)
    auto.tap_percent(0.50, 0.60, delay=0.8)
    auto.keyevent(4) # Ẩn popup

    # Gõ tên test
    test_user = "TestUser" + str(int(time.time()) % 10000)
    print(f" • Gõ username: {test_user}")
    auto.tap_percent(0.50, 0.42, delay=0.5)
    auto.input_text(test_user)
    time.sleep(0.5)
    auto.keyevent(4)

    # Chọn giới tính Nam
    auto.tap_percent(0.75, 0.56, delay=0.5)

    # Bấm Continue
    print(" • Bấm nút 'Continue'...")
    if not auto.click_element_by_text("Continue", timeout=5):
        auto.tap_percent(0.50, 0.72, delay=2.0)

    time.sleep(2)
    input(f"{CYAN}👉 Nhìn vào màn hình: Đã chuyển sang Form Mật Khẩu (Ảnh 3) chưa? Bấm Enter để test gõ mật khẩu...{RESET}")

    # BƯỚC 4: ĐIỀN MẬT KHẨU & BẤM DONE
    print(f"\n{BOLD}[4/4] 🔑 TEST ĐIỀN MẬT KHẨU & BẤM 'Done':{RESET}")
    auto.tap_percent(0.50, 0.40, delay=0.5)
    auto.input_text("TestPass2026!@")
    time.sleep(0.5)
    auto.keyevent(4) # Ẩn bàn phím

    print(" • Bấm nút 'Done'...")
    if not auto.click_element_by_text("Done", timeout=5):
        auto.tap_percent(0.50, 0.60, delay=1.5)

    print(f"\n{GREEN}🎉 HOÀN TẤT BÀI TEST TỪNG BƯỚC!{RESET}\n")

if __name__ == "__main__":
    main()
