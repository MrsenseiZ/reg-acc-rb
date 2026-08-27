#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
══════════════════════════════════════════════════════════════════════════════
  📱 TERMUX ROBLOX MASS ACCOUNT CREATOR (DISCORD EDITION) 🚀
  - Tối ưu hóa 100% cho Termux / Android & Cloud Phone (LDCloud, Redfinger, UgPhone)
  - Hỗ trợ Chế độ Tự Động Thao Tác Trực Tiếp Trên App Delta Roblox (Native UI Auto)
  - Hoặc Chế độ Pure REST API Siêu Nhanh
  - Tự do chỉnh số lượng tài khoản muốn tạo qua config.json hoặc lệnh `python main.py -n <số_lượng>`
  - Gửi đính kèm FULL FILE TXT về Discord khi hoàn tất lô (Batch Export)
══════════════════════════════════════════════════════════════════════════════
"""

import os
import sys

os.environ.setdefault("PYTHONUTF8", "1")
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import json
import time
import argparse
import threading
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

from generators import generate_username, generate_password, generate_birthday, generate_gender
from captcha_solver import CaptchaSolver
from proxy_manager import ProxyManager
from discord_notifier import DiscordNotifier
from roblox_api import RobloxApiEngine
from apk_installer import ApkInstaller
from app_automation import RobloxAppAutomator

# ANSI Color Codes cho Terminal / Termux
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
MAGENTA = "\033[95m"
BOLD = "\033[1m"
RESET = "\033[0m"

file_lock = threading.Lock()
stats_lock = threading.Lock()

STATS = {
    "target": 0,
    "success": 0,
    "failed": 0,
    "start_time": 0
}

def load_config() -> dict:
    config_file = "config.json"
    if not os.path.exists(config_file):
        print(f"{RED}[!] Không tìm thấy file {config_file}! Đang tạo cấu hình mẫu...{RESET}")
        default_cfg = {
            "_CHU_Y": "LINK TẢI ROBLOX / DELTA APK NẰM NGAY DÒNG DƯỚI - BẠN CÓ THỂ ĐỔI BẤT KỲ LÚC NÀO",
            "roblox_apk_download_link": "https://delta.filenetwork.vip/file/Delta-2.735.1138.apk",
            "execution_mode": "app",
            "discord_webhook": "",
            "discord_notification_mode": "batch_file",
            "captcha": {
                "provider": "omocaptcha",
                "api_key": "",
                "sitekey": "47A08D90-3D8B-4C9A-9F09-6B6F9374B358"
            },
            "settings": {
                "threads": 1,
                "total_accounts": 500,
                "delay_between_creates": 3,
                "under13": False,
                "password_mode": "random",
                "static_password": "RezzPass2026!@",
                "save_file": "accounts.txt"
            },
            "proxy": {
                "enabled": true,
                "proxy_file": "proxies.txt",
                "sticky_session": True
            }
        }
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(default_cfg, f, indent=2)
        return default_cfg

    with open(config_file, "r", encoding="utf-8") as f:
        return json.load(f)

def save_account_to_file(filepath: str, username: str, password: str, cookie: str, batch_file: str = ""):
    """Lưu tài khoản định dạng username:password:cookie vào file tổng và file lô"""
    with file_lock:
        line = f"{username}:{password}:{cookie}\n"
        with open(filepath, "a", encoding="utf-8") as f:
            f.write(line)
        if batch_file and batch_file != filepath:
            with open(batch_file, "a", encoding="utf-8") as f:
                f.write(line)

def print_banner(cfg: dict, solver: CaptchaSolver, discord: DiscordNotifier, proxy_mgr: ProxyManager, installer: ApkInstaller, batch_file: str):
    os.system('clear' if os.name != 'nt' else 'cls')
    print(f"{CYAN}{BOLD}")
    print(r"  ____       _     _            ____ _                 _ ")
    print(r" |  _ \ ___ | |__ | | _____  __/ ___| | ___  _   _  __| |")
    print(r" | |_) / _ \| '_ \| |/ _ \ \/ / |   | |/ _ \| | | |/ _` |")
    print(r" |  _ < (_) | |_) | | (_) >  <| |___| | (_) | |_| | (_| |")
    print(r" |_| \_\___/|_.__/|_|\___/_/\_\\____|_|\___/ \__,_|\__,_|")
    print(f"        📱 TERMUX & CLOUD PHONE FAST REG ENGINE 🚀{RESET}")
    print(f"{MAGENTA}═" * 62 + f"{RESET}")
    
    exec_mode = cfg.get("execution_mode", "app").upper()
    cap_status = f"{GREEN}Sẵn sàng ({solver.get_balance()}){RESET}" if solver.api_key else f"{YELLOW}Chưa cấu hình API Key{RESET}"
    notify_mode = cfg.get("discord_notification_mode", "batch_file")
    mode_text = "Gửi Full File khi Xong Lô" if notify_mode == "batch_file" else ("Gửi từng acc" if notify_mode == "each_account" else "Gửi cả hai")
    webhook_status = f"{GREEN}Đã kết nối ({mode_text}){RESET}" if discord.is_valid() else f"{YELLOW}Chưa nhập Webhook{RESET}"
    proxy_status = f"{GREEN}Bật ({len(proxy_mgr.proxies)} proxy){RESET}" if proxy_mgr.enabled else f"{YELLOW}Tắt (Dùng IP máy){RESET}"
    apk_status = f"{GREEN}Đã cài đặt{RESET}" if installer.is_installed() else f"{YELLOW}Chưa cài ({installer.filename}){RESET}"

    print(f" • Chế độ chạy     : {MAGENTA}{BOLD}{exec_mode} MODE (Thao Tác Trực Tiếp Trên App Delta){RESET}" if exec_mode == "APP" else f" • Chế độ chạy     : {CYAN}API FAST MODE (Chạy ngầm siêu tốc){RESET}")
    print(f" • Captcha Solver  : {cap_status}")
    print(f" • Discord Webhook : {webhook_status}")
    print(f" • Proxy Pool      : {proxy_status}")
    print(f" • Roblox/Delta APK: {apk_status}")
    print(f" • Số luồng chạy   : {CYAN}{cfg['settings']['threads']}{RESET} | Mục tiêu lô: {CYAN}{cfg['settings']['total_accounts']} accounts{RESET}")
    print(f" • File xuất lô    : {BOLD}{batch_file}{RESET}")
    print(f"{MAGENTA}═" * 62 + f"{RESET}\n")

def run_app_mode_loop(cfg: dict, discord: DiscordNotifier, proxy_mgr: ProxyManager, batch_file: str):
    """Chạy vòng lặp tự động thao tác trực tiếp trên App Delta Roblox."""
    automator = RobloxAppAutomator(package_name=cfg.get("roblox_apk", {}).get("package_name", "com.roblox.client"), discord=discord)
    settings = cfg["settings"]
    save_file = settings.get("save_file", "accounts.txt")
    delay = settings.get("delay_between_creates", 3)
    notify_mode = cfg.get("discord_notification_mode", "batch_file").lower()

    while STATS["success"] < STATS["target"]:
        current_proxy = proxy_mgr.get_proxy(0)
        ok, user, pwd, cookie = automator.register_single_account_on_app(proxy_str=current_proxy)

        if ok:
            with stats_lock:
                STATS["success"] += 1
                succ = STATS["success"]
                tgt = STATS["target"]

            save_account_to_file(save_file, user, pwd, cookie, batch_file=batch_file)
            print(f"{GREEN}🎉 [THÀNH CÔNG #{succ}/{tgt}]{RESET} User: {BOLD}{user}{RESET} đã tạo trên App!")

            if notify_mode in ["each_account", "both"] and discord.is_valid():
                discord.send_account_created(username=user, password=pwd, cookie=cookie, proxy=current_proxy)
        else:
            with stats_lock:
                STATS["failed"] += 1
            print(f"{RED}❌ Không thể tạo tài khoản trên App.{RESET}")

        time.sleep(delay)

def worker(worker_id: int, cfg: dict, solver: CaptchaSolver, discord: DiscordNotifier, proxy_mgr: ProxyManager, batch_file: str):
    settings = cfg["settings"]
    save_file = settings.get("save_file", "accounts.txt")
    delay = settings.get("delay_between_creates", 2)
    notify_mode = cfg.get("discord_notification_mode", "batch_file").lower()

    while True:
        with stats_lock:
            if STATS["success"] >= STATS["target"]:
                break

        proxy = proxy_mgr.get_proxy(slot_id=worker_id)
        engine = RobloxApiEngine(solver=solver, proxy_str=proxy)

        # 1. Sinh thông tin tài khoản
        username = generate_username()
        password = generate_password(
            mode=settings.get("password_mode", "random"),
            static_pass=settings.get("static_password", "RezzPass2026!@"),
            username=username
        )
        bday = generate_birthday(
            age_mode=settings.get("age_mode", "18+"),
            under13=settings.get("under13", False)
        )
        gender = generate_gender()

        prefix = f"{CYAN}[Luồng {worker_id+1}]{RESET}"
        print(f"{prefix} ⏳ Đang khởi tạo tài khoản: {BOLD}{username}{RESET}...")

        # 2. Đăng ký tài khoản
        ok, cookie, user_id, msg = engine.register(
            username=username,
            password=password,
            birthday_iso=bday["iso"],
            gender=gender
        )

        if ok and cookie:
            with stats_lock:
                STATS["success"] += 1
                succ = STATS["success"]
                tgt = STATS["target"]

            print(f"{prefix} {GREEN}🎉 [THÀNH CÔNG #{succ}/{tgt}]{RESET} User: {BOLD}{username}{RESET} | ID: {user_id}")

            # Lưu vào file tổng và file lô hiện tại
            save_account_to_file(save_file, username, password, cookie, batch_file=batch_file)

            # Nếu bật chế độ gửi từng acc
            if notify_mode in ["each_account", "both"] and discord.is_valid():
                sent = discord.send_account_created(
                    username=username,
                    password=password,
                    cookie=cookie,
                    user_id=user_id,
                    bday=bday["formatted"],
                    proxy=proxy
                )
                if sent:
                    print(f"{prefix} 📩 {GREEN}Đã gửi thông báo tới Discord Webhook!{RESET}")
        else:
            with stats_lock:
                STATS["failed"] += 1
            if proxy:
                proxy_mgr.mark_fail(proxy)
            print(f"{prefix} {RED}❌ Thất bại:{RESET} {msg}")

        time.sleep(delay)

def check_and_prompt_keys(cfg: dict) -> dict:
    """Tự động hỏi người dùng nhập Key OmoCaptcha và Webhook Discord trên Termux nếu chưa có (Tự lưu vĩnh viễn vào máy)."""
    changed = False
    
    # 1. Kiểm tra OmoCaptcha Key
    current_key = cfg.get("captcha", {}).get("api_key", "").strip()
    if not current_key or current_key in ["YOUR_OMOCAPTCHA_KEY_HERE", "DIEN_KEY_OMOCAPTCHA_VAO_DAY", "DIEN_OMOCAPTCHA_KEY_VAO_DAY"]:
        print(f"\n{YELLOW}══════════════════════════════════════════════════════════════{RESET}")
        print(f"{YELLOW}🔑 THIẾT LẬP LẦN ĐẦU TRÊN MÁY (Tự động lưu vĩnh viễn):{RESET}")
        print(f"{YELLOW}══════════════════════════════════════════════════════════════{RESET}")
        try:
            omo_in = input(f"{CYAN}👉 Dán API Key OmoCaptcha của bạn: {RESET}").strip()
            if omo_in:
                cfg.setdefault("captcha", {})["api_key"] = omo_in
                changed = True
        except (KeyboardInterrupt, EOFError):
            pass

    # 2. Kiểm tra Discord Webhook
    current_webhook = cfg.get("discord_webhook", "").strip()
    if not current_webhook or current_webhook in ["https://discord.com/api/webhooks/YOUR_WEBHOOK_HERE", "https://discord.com/api/webhooks/DIEN_WEBHOOK_CUA_BAN_VAO_DAY"]:
        try:
            wh_in = input(f"{CYAN}👉 Dán Discord Webhook URL (Bấm Enter để bỏ qua nếu không dùng): {RESET}").strip()
            if wh_in:
                cfg["discord_webhook"] = wh_in
                changed = True
        except (KeyboardInterrupt, EOFError):
            pass

    # 3. Kiểm tra Link APK Roblox/Delta
    current_apk = cfg.get("roblox_apk_download_link", "").strip()
    if not current_apk:
        try:
            apk_in = input(f"{CYAN}👉 Dán Link tải APK Roblox mới (Bấm Enter để dùng Delta mặc định): {RESET}").strip()
            if apk_in and apk_in.startswith("http"):
                cfg["roblox_apk_download_link"] = apk_in
                changed = True
            else:
                cfg["roblox_apk_download_link"] = "https://delta.filenetwork.vip/file/Delta-2.735.1138.apk"
                changed = True
        except (KeyboardInterrupt, EOFError):
            pass

    # Tự động lưu lại vào config.json trên máy Cloud Phone
    if changed:
        with open("config.json", "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2)
        print(f"\n{GREEN}[✓] Đã lưu cấu hình vào máy Cloud Phone! Các lần sau sẽ tự chạy không cần hỏi lại.{RESET}\n")

    return cfg

def main():
    parser = argparse.ArgumentParser(description="Termux Roblox Mass Account Creator")
    parser.add_argument("-n", "--count", type=int, default=None, help="Số lượng tài khoản muốn tạo (Ví dụ: -n 50)")
    parser.add_argument("-t", "--threads", type=int, default=None, help="Số luồng chạy song song (Ví dụ: -t 5)")
    parser.add_argument("-m", "--mode", type=str, choices=["app", "api"], default=None, help="Chế độ chạy: app (trên app thật) hoặc api (chạy ngầm)")
    parser.add_argument("-k", "--omo-key", type=str, default=None, help="API Key OmoCaptcha")
    parser.add_argument("-w", "--webhook", type=str, default=None, help="Discord Webhook URL")
    parser.add_argument("-p", "--proxy", type=str, default=None, help="Proxy chuỗi (user:pass@host:port)")
    parser.add_argument("-a", "--apk-url", type=str, default=None, help="Link tải APK Roblox mới")
    args = parser.parse_args()

    cfg = load_config()

    # Ghi đè cấu hình nếu người dùng truyền qua tham số dòng lệnh
    if args.omo_key:
        cfg.setdefault("captcha", {})["api_key"] = args.omo_key
    if args.webhook:
        cfg["discord_webhook"] = args.webhook
    if args.apk_url:
        cfg["roblox_apk_download_link"] = args.apk_url
    if args.proxy:
        with open("proxies.txt", "w", encoding="utf-8") as f:
            f.write(f"{args.proxy}\n")
        cfg.setdefault("proxy", {})["enabled"] = True

    # Hỏi nhập cấu hình nếu chưa có (lưu cục bộ trên máy)
    cfg = check_and_prompt_keys(cfg)

    settings = cfg.get("settings", {})
    captcha_cfg = cfg.get("captcha", {})
    proxy_cfg = cfg.get("proxy", {})
    apk_cfg = cfg.get("roblox_apk", {})

    # Hỏi số lượng tài khoản muốn tạo nếu không truyền cờ -n
    default_total = settings.get("total_accounts", 500)
    if args.count:
        total_req = args.count
    else:
        try:
            user_count_str = input(f"{CYAN}👉 Nhập số lượng tài khoản muốn tạo (Mặc định: {default_total}, bấm Enter để lấy mặc định): {RESET}").strip()
            if user_count_str.isdigit() and int(user_count_str) > 0:
                total_req = int(user_count_str)
            else:
                total_req = default_total
        except (KeyboardInterrupt, EOFError):
            total_req = default_total

    settings["total_accounts"] = total_req

    if args.mode:
        cfg["execution_mode"] = args.mode
    exec_mode = cfg.get("execution_mode", "app").lower()
    if args.threads:
        settings["threads"] = args.threads

    notify_mode = cfg.get("discord_notification_mode", "batch_file").lower()

    solver = CaptchaSolver(
        provider=captcha_cfg.get("provider", "omocaptcha"),
        api_key=captcha_cfg.get("api_key", ""),
        sitekey=captcha_cfg.get("sitekey", "47A08D90-3D8B-4C9A-9F09-6B6F9374B358")
    )

    discord = DiscordNotifier(webhook_url=cfg.get("discord_webhook", ""))
    
    proxy_mgr = ProxyManager(
        proxy_file=proxy_cfg.get("proxy_file", "proxies.txt"),
        enabled=proxy_cfg.get("enabled", True),
        sticky=proxy_cfg.get("sticky_session", True)
    )

    apk_url = cfg.get("roblox_apk_download_link") or apk_cfg.get("url", "https://delta.filenetwork.vip/file/Delta-2.735.1138.apk")
    installer = ApkInstaller(
        apk_url=apk_url,
        filename=apk_cfg.get("filename", "Delta-Roblox.apk"),
        package_name=apk_cfg.get("package_name", "com.roblox.client")
    )

    # Tự động kiểm tra và cài APK nếu chưa có
    if not installer.is_installed() and apk_url:
        print(f"{YELLOW}[*] Phát hiện chưa cài app Roblox/Delta trên máy. Đang tự động tải và cài đặt...{RESET}")
        if not os.path.exists(installer.apk_path):
            installer.download_apk()
        installer.install_apk()

    total_req = settings.get("total_accounts", 500)
    threads = settings.get("threads", 1 if exec_mode == "app" else 5)
    
    time_tag = datetime.now().strftime("%Y%m%d_%H%M%S")
    batch_file = f"accounts_batch_{total_req}acc_{time_tag}.txt"

    print_banner(cfg, solver, discord, proxy_mgr, installer, batch_file)

    STATS["target"] = total_req
    STATS["start_time"] = time.time()

    print(f"{GREEN}🚀 BẮT ĐẦU TIẾN TRÌNH REG LÔ {total_req} TÀI KHOẢN (Chế độ: {exec_mode.upper()})...{RESET}\n")

    try:
        if exec_mode == "app":
            run_app_mode_loop(cfg, discord, proxy_mgr, batch_file)
        else:
            threads_list = []
            for i in range(threads):
                t = threading.Thread(target=worker, args=(i, cfg, solver, discord, proxy_mgr, batch_file))
                t.daemon = True
                t.start()
                threads_list.append(t)
                time.sleep(0.3)
            for t in threads_list:
                t.join()
    except KeyboardInterrupt:
        print(f"\n{YELLOW}[!] Đã nhận tín hiệu dừng từ bàn phím (Ctrl+C).{RESET}")

    elapsed = time.time() - STATS["start_time"]
    print(f"\n{MAGENTA}═" * 62 + f"{RESET}")
    print(f"{BOLD}📊 TỔNG KẾT TIẾN TRÌNH LÔ:{RESET}")
    print(f" • Thành công : {GREEN}{STATS['success']}{RESET} / {STATS['target']} tài khoản")
    print(f" • Thất bại   : {RED}{STATS['failed']}{RESET} lượt")
    print(f" • Thời gian  : {CYAN}{elapsed:.1f}s{RESET}")
    print(f" • File lô    : {BOLD}{batch_file}{RESET}")
    print(f"{MAGENTA}═" * 62 + f"{RESET}")

    # Gửi full file lô về Discord khi hoàn tất
    if notify_mode in ["batch_file", "both"] and discord.is_valid() and STATS["success"] > 0:
        print(f"\n{CYAN}📦 Đang gửi full file đính kèm ({STATS['success']} acc) lên Discord Webhook...{RESET}")
        sent_ok = discord.send_batch_file(
            filepath=batch_file,
            total_success=STATS["success"],
            total_failed=STATS["failed"],
            elapsed_seconds=elapsed
        )
        if sent_ok:
            print(f"{GREEN}🎉 [ĐÃ GỬI XONG] File '{batch_file}' đã được gửi trực tiếp lên Discord của bạn!{RESET}\n")
        else:
            print(f"{RED}[!] Không thể gửi file lên Discord. Bạn có thể lấy file trực tiếp tại: {batch_file}{RESET}\n")
    elif not discord.is_valid():
        print(f"{YELLOW}⚠️ Chưa điền Discord Webhook nên không thể gửi file qua Discord.{RESET}\n")

if __name__ == "__main__":
    main()
