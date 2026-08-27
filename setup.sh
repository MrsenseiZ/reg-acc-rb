#!/data/data/com.termux/files/usr/bin/bash
# ══════════════════════════════════════════════════════════════════
#   ⚡ SCRIPT TỰ ĐỘNG CÀI ĐẶT 1-CHẠM CHO TERMUX & CLOUD PHONE 🚀
#   - Tự động tạo thư mục lối tắt trong /sdcard/Download
#   - Tự động cài đặt Python, Git, Wget, Curl, Android Tools
#   - Tự động phát hiện & cài đặt Delta Roblox APK và MT Manager APK
#   - Tối ưu hóa môi trường chạy Tool
# ══════════════════════════════════════════════════════════════════

echo -e "\033[96m[1/6] 📁 Đang tự động kết nối thư mục vào /sdcard/Download/reg-acc-rb...\033[0m"
termux-setup-storage 2>/dev/null
TOOL_DIR="$(pwd)"

# Tạo thư mục lối tắt trong Download cho MT Manager thấy ngay
for dl_dir in "/sdcard/Download" "/storage/emulated/0/Download"; do
    if [ -d "$dl_dir" ]; then
        ln -sf "$TOOL_DIR" "$dl_dir/reg-acc-rb" 2>/dev/null
        ln -sf "$TOOL_DIR/proxies.txt" "$dl_dir/proxies.txt" 2>/dev/null
        ln -sf "$TOOL_DIR/config.json" "$dl_dir/config.json" 2>/dev/null
        echo -e "\033[92m[✓] Đã tạo thư mục thành công tại: $dl_dir/reg-acc-rb\033[0m"
        echo -e "\033[92m[✓] Đã tạo file proxy tại: $dl_dir/proxies.txt (Dễ dàng mở bằng MT Manager)\033[0m"
        break
    fi
done

echo -e "\033[96m[2/6] 📦 Đang cập nhật hệ thống Termux...\033[0m"
pkg update -y && pkg upgrade -y

echo -e "\033[96m[3/6] 🔧 Đang cài đặt Python, Git, Wget, Curl, Android-Tools...\033[0m"
pkg install python git wget curl android-tools -y

echo -e "\033[96m[4/6] 📚 Đang cài đặt thư viện Python (requests, urllib3)...\033[0m"
pip install --upgrade pip
pip install requests urllib3

echo -e "\033[96m[5/6] 📁 Đang kiểm tra & cài đặt MT Manager APK...\033[0m"
python -c "
from apk_installer import ApkInstaller
import json, os

mt_installer = ApkInstaller(apk_url='https://www.binmt.cc/download/MT2.16.5.apk', filename='MT_Manager.apk', package_name='bin.mt.plus')
if not mt_installer.is_installed():
    local_apk = mt_installer.find_local_apk()
    if local_apk and 'MT' in local_apk:
        mt_installer.apk_path = local_apk
        mt_installer.install_apk()
    else:
        if mt_installer.download_apk():
            mt_installer.install_apk()
else:
    print('\033[92m[✓] MT Manager đã được cài đặt sẵn trên máy!\033[0m')
"

echo -e "\033[96m[6/6] 📥 Đang kiểm tra & cài đặt Delta Roblox APK...\033[0m"
python -c "
from apk_installer import ApkInstaller
import json, os

cfg = {}
if os.path.exists('config.json'):
    with open('config.json', 'r') as f:
        cfg = json.load(f)

url = cfg.get('roblox_apk_download_link', 'https://delta.filenetwork.vip/file/Delta-2.735.1138.apk')
installer = ApkInstaller(apk_url=url, filename='Delta-Roblox.apk', package_name='com.roblox.client')

if not installer.is_installed():
    local_apk = installer.find_local_apk()
    if local_apk:
        print(f'\033[92m[✓] Đã phát hiện file Delta APK có sẵn tại: {local_apk}\033[0m')
        installer.apk_path = local_apk
        installer.install_apk()
    else:
        if installer.download_apk():
            installer.install_apk()
else:
    print('\033[92m[✓] App Roblox/Delta đã được cài đặt sẵn trên máy!\033[0m')
"

echo -e "\n\033[92m══════════════════════════════════════════════════════════════\033[0m"
echo -e "\033[92m  🎉 SETUP HOÀN TẤT 100%! HỆ THỐNG ĐÃ SẴN SÀNG HOẠT ĐỘNG!    \033[0m"
echo -e "\033[92m══════════════════════════════════════════════════════════════\033[0m"
echo -e "\033[93m👉 Bạn có thể mở MT Manager vào thư mục Download -> reg-acc-rb -> proxies.txt để dán proxy.\033[0m"
echo -e "\033[93m👉 Lệnh chạy tool: \033[96mpython main.py\033[0m\n"
