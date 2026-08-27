# 🚀 TERMUX ROBLOX MASS ACCOUNT CREATOR (DISCORD EDITION)

Tool tạo tài khoản Roblox tự động tốc độ cao được thiết kế **riêng biệt 100% cho Termux trên Android & Cloud Phone** (LDCloud, Redfinger, UgPhone, v.v.) kết hợp **Tự Động Tải & Cài Đặt APK Delta Roblox** và **Gửi Đính Kèm FULL File Lô (500 acc) Về Discord Webhook**.

---

## ✨ Tính Năng Nổi Bật

1. **📦 Tự Động Gửi Full File Lô TXT Về Discord Khi Hoàn Tất:**
   - Khi bạn đặt mục tiêu reg 500 acc (hoặc số lượng tùy chỉnh), tool sẽ âm thầm chạy và lưu vào file riêng của lô đó (ví dụ: `accounts_batch_500acc_20260827_231500.txt`).
   - **Khi reg xong đủ 500 acc (hoặc khi bạn bấm Ctrl+C dừng tool):** Tool sẽ tự động đính kèm toàn bộ file TXT này và upload trực tiếp lên kênh Discord của bạn kèm bảng thống kê tổng kết. Không bị tình trạng spam hàng trăm tin nhắn lẻ!
2. **📥 Tự Động Tải & Cài Đặt APK Delta Roblox Mới:**
   - Đặt sẵn link tải APK mới nhất ngay đầu file `config.json`: `https://delta.filenetwork.vip/file/Delta-2.735.1138.apk`.
   - Script setup tự động tải và cài đặt vào Cloud Phone qua Root (`su`/`tsu`), ADB hoặc Package Installer.
3. **🛡️ Hỗ Trợ Proxy Xoay Dân Cư (Nettify, Luna, Webshare):**
   - Hỗ trợ định dạng `user:pass@host:port` và `host:port:user:pass`.
   - Tự động gắn Sticky Session xoay IP cho từng luồng/từng tài khoản.
4. **⚡ Siêu Nhẹ – Tối Ưu 100% Cho Termux:**
   - Chạy Pure REST API, tốn chưa tới **30MB RAM** (không dùng Chrome PC nặng nề), tránh sập RAM Cloud Phone.
5. **🔐 Tự Động Vượt FunCaptcha (Arkose Labs):**
   - Tích hợp API **OmoCaptcha**, **YesCaptcha**, **CapSolver**.

---

## ⚙️ Cấu Hình `config.json`

```json
{
  "_CHU_Y": "LINK TẢI ROBLOX / DELTA APK NẰM NGAY DÒNG DƯỚI - BẠN CÓ THỂ ĐỔI BẤT KỲ LÚC NÀO",
  "roblox_apk_download_link": "https://delta.filenetwork.vip/file/Delta-2.735.1138.apk",

  "discord_webhook": "https://discord.com/api/webhooks/DIEN_WEBHOOK_CUA_BAN_VAO_DAY",
  "discord_notification_mode": "batch_file",

  "captcha": {
    "provider": "omocaptcha",
    "api_key": "DIEN_KEY_OMOCAPTCHA_VAO_DAY",
    "sitekey": "47A08D90-3D8B-4C9A-9F09-6B6F9374B358"
  },

  "settings": {
    "threads": 5,
    "total_accounts": 500,
    "delay_between_creates": 2,
    "under13": false,
    "password_mode": "random",
    "static_password": "RezzPass2026!@",
    "save_file": "accounts.txt"
  },

  "proxy": {
    "enabled": true,
    "proxy_file": "proxies.txt",
    "sticky_session": true
  }
}
```

> **Giải thích `discord_notification_mode`:**
> - `"batch_file"` (Mặc định): Chạy xong toàn bộ lô (ví dụ 500 acc) mới gửi đính kèm 1 file TXT lên Discord.
> - `"each_account"`: Gửi tin nhắn embed cho từng tài khoản ngay khi vừa reg xong.
> - `"both"`: Gửi cả từng acc vừa gửi full file khi xong lô.

---

## 📲 Hướng Dẫn Cài Đặt & Chạy 1-Chạm

```bash
# 1. Chạy setup 1-chạm (Tự cài môi trường + Tự tải cài Delta Roblox APK)
bash setup.sh

# 2. Điền Webhook Discord và Key OmoCaptcha trong config.json
nano config.json

# 3. Khởi động Tool
python main.py
```
