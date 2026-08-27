#!/data/data/com.termux/files/usr/bin/bash
# ══════════════════════════════════════════════════════════════════
#   ⚡ SCRIPT TỰ ĐỘNG CÀI ĐẶT 1-CHẠM CHO TERMUX & CLOUD PHONE 🚀
#   - Tự động cài đặt Python, Git, Wget, Curl, Android Tools
#   - Tự động tải & cài đặt MT Manager APK vào Cloud Phone
#   - Tự động hỏi/dán link tải Delta Roblox APK trực tiếp trên Termux
#   - Tối ưu hóa môi trường chạy Tool
# ══════════════════════════════════════════════════════════════════

echo -e "\033[96m[1/5] 📦 Đang cập nhật hệ thống Termux...\033[0m"
pkg update -y && pkg upgrade -y

echo -e "\033[96m[2/5] 🔧 Đang cài đặt Python, Git, Wget, Curl, Android-Tools...\033[0m"
pkg install python git wget curl android-tools -y

echo -e "\033[96m[3/5] 📚 Đang cài đặt thư viện Python (requests, urllib3)...\033[0m"
pip install --upgrade pip
pip install requests urllib3

echo -e "\033[96m[4/5] 📁 Đang tải và cài đặt MT Manager APK vào Cloud Phone...\033[0m"
python -c "
from apk_installer import ApkInstaller
import json, os

mt_url = 'https://www.binmt.cc/download/MT2.16.5.apk'
if os.path.exists('config.json'):
    with open('config.json', 'r') as f:
        cfg = json.load(f)
    mt_url = cfg.get('mt_manager_download_link', mt_url)

mt_installer = ApkInstaller(apk_url=mt_url, filename='MT_Manager.apk', package_name='bin.mt.plus')
if not mt_installer.is_installed():
    print('\033[93m[*] Đang tải MT Manager...\033[0m')
    if mt_installer.download_apk():
        mt_installer.install_apk()
else:
    print('\033[92m[✓] MT Manager đã được cài đặt sẵn trên máy!\033[0m')
"

echo -e "\033[96m[5/5] 📥 Đang chuẩn bị tải Delta Roblox APK...\033[0m"
python -c "
from apk_installer import ApkInstaller
import json, os

cfg = {}
if os.path.exists('config.json'):
    with open('config.json', 'r') as f:
        cfg = json.load(f)

default_url = cfg.get('roblox_apk_download_link', 'https://delta.filenetwork.vip/file/Delta-2.735.1138.apk')
print('\033[93m👉 Dán link tải Roblox/Delta APK mới (Hoặc bấm Enter để dùng link Delta mặc định):\033[0m')
try:
    user_url = input('Link APK: ').strip()
    if user_url and user_url.startswith('http'):
        url = user_url
        cfg['roblox_apk_download_link'] = url
        with open('config.json', 'w') as f:
            json.dump(cfg, f, indent=2)
        print(f'\033[92m[✓] Đã lưu link APK mới vào máy: {url}\033[0m')
    else:
        url = default_url
except Exception:
    url = default_url

installer = ApkInstaller(apk_url=url, filename='Delta-Roblox.apk', package_name='com.roblox.client')
if not installer.is_installed():
    if installer.download_apk():
        installer.install_apk()
else:
    print('\033[92m[✓] App Roblox/Delta đã được cài đặt sẵn trên máy!\033[0m')
"

echo -e "\n\033[92m══════════════════════════════════════════════════════════════\033[0m"
echo -e "\033[92m  🎉 SETUP HOÀN TẤT 100%! HỆ THỐNG ĐÃ SẴN SÀNG HOẠT ĐỘNG!    \033[0m"
echo -e "\033[92m══════════════════════════════════════════════════════════════\033[0m"
echo -e "\033[93m👉 Lệnh chạy tool: \033[96mpython main.py\033[0m\n"
