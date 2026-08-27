#!/data/data/com.termux/files/usr/bin/bash
# ══════════════════════════════════════════════════════════════════
#   ⚡ SCRIPT TỰ ĐỘNG CÀI ĐẶT 1-CHẠM CHO TERMUX & CLOUD PHONE 🚀
#   - Tự động cài đặt Python, Git, Wget, Curl, Android Tools
#   - Tự động tải & cài đặt Delta Roblox APK lên máy
#   - Tối ưu hóa môi trường chạy Tool
# ══════════════════════════════════════════════════════════════════

echo -e "\033[96m[1/4] 📦 Đang cập nhật hệ thống Termux...\033[0m"
pkg update -y && pkg upgrade -y

echo -e "\033[96m[2/4] 🔧 Đang cài đặt Python, Git, Wget, Curl, Android-Tools...\033[0m"
pkg install python git wget curl android-tools -y

echo -e "\033[96m[3/4] 📚 Đang cài đặt thư viện Python (requests, urllib3)...\033[0m"
pip install --upgrade pip
pip install requests urllib3

echo -e "\033[96m[4/4] 📥 Đang tải và cài đặt Delta Roblox APK vào Cloud Phone...\033[0m"
python -c "
from apk_installer import ApkInstaller
import json, os

if os.path.exists('config.json'):
    with open('config.json', 'r') as f:
        cfg = json.load(f)
    apk_info = cfg.get('roblox_apk', {})
    url = cfg.get('roblox_apk_download_link') or apk_info.get('url', 'https://delta.filenetwork.vip/file/Delta-2.735.1138.apk')
    filename = apk_info.get('filename', 'Delta-Roblox.apk')
    pkg = apk_info.get('package_name', 'com.roblox.client')
    installer = ApkInstaller(apk_url=url, filename=filename, package_name=pkg)
    if not installer.is_installed():
        if installer.download_apk():
            installer.install_apk()
    else:
        print('\033[92m[✓] App Roblox/Delta đã được cài đặt sẵn trên máy!\033[0m')
"

echo -e "\n\033[92m══════════════════════════════════════════════════════════════\033[0m"
echo -e "\033[92m  🎉 SETUP HOÀN TẤT 100%! HỆ THỐNG ĐÃ SẴN SÀNG HOẠT ĐỘNG!    \033[0m"
echo -e "\033[92m══════════════════════════════════════════════════════════════\033[0m"
echo -e "\033[93m👉 Hãy mở file config.json và điền discord_webhook cùng api_key OmoCaptcha.\033[0m"
echo -e "\033[93m👉 Lệnh chạy tool: \033[96mpython main.py\033[0m\n"
