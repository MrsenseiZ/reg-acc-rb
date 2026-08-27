#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module Gửi Thông Báo Tài Khoản & Gửi Full File Lô Về Discord Webhook
Hỗ trợ gửi từng account hoặc gửi đính kèm file TXT khi hoàn tất cả lô (Batch).
"""

import os
import time
import json
import requests
from datetime import datetime
from typing import Optional, Dict, Any

class DiscordNotifier:
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url.strip() if webhook_url else ""

    def is_valid(self) -> bool:
        return bool(self.webhook_url and self.webhook_url.startswith("https://discord.com/api/webhooks/"))

    def send_account_created(self, username: str, password: str, cookie: str, user_id: Optional[int] = None, bday: str = "", proxy: Optional[str] = None) -> bool:
        """Gửi embed thông báo tạo từng acc thành công về Discord."""
        if not self.is_valid():
            return False

        profile_url = f"https://www.roblox.com/users/{user_id}/profile" if user_id else f"https://www.roblox.com/search/users?keyword={username}"
        proxy_display = proxy.split("@")[-1] if proxy and "@" in proxy else (proxy or "Direct IP (Không dùng Proxy)")

        embed = {
            "title": "🎉 ROBLOX ACCOUNT CREATED SUCCESSFULLY!",
            "description": f"Tài khoản Roblox mới vừa được khởi tạo thành công từ **Cloud Phone (Termux)**!",
            "url": profile_url,
            "color": 5814783, # Cyan / Emerald Neon Green
            "fields": [
                {
                    "name": "👤 Username",
                    "value": f"`{username}`",
                    "inline": True
                },
                {
                    "name": "🔑 Password",
                    "value": f"`{password}`",
                    "inline": True
                },
                {
                    "name": "🆔 User ID",
                    "value": f"[{user_id}]({profile_url})" if user_id else "`N/A`",
                    "inline": True
                },
                {
                    "name": "📅 Ngày sinh",
                    "value": f"`{bday or '2000-01-01'}`",
                    "inline": True
                },
                {
                    "name": "🛡️ Proxy IP",
                    "value": f"`{proxy_display}`",
                    "inline": True
                },
                {
                    "name": "🔗 Profile",
                    "value": f"[Xem Trang Cá Nhân]({profile_url})",
                    "inline": True
                },
                {
                    "name": "🍪 .ROBLOSECURITY Cookie (Bấm copy)",
                    "value": f"```{cookie}```",
                    "inline": False
                }
            ],
            "footer": {
                "text": "⚡ Termux Cloud Phone Bot • RezzTOOL Engine",
                "icon_url": "https://images.rbxcdn.com/2b356da0fbab61db57b2de9ced8808d9.ico"
            },
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

        payload = {
            "username": "Roblox Cloud Creator",
            "avatar_url": "https://tr.rbxcdn.com/30DAY-AvatarHeadshot-B101D05B73E0C1CF85C0CEAC33B0A956-Png/150/150/AvatarHeadshot/Webp/noFilter",
            "embeds": [embed]
        }

        for attempt in range(3):
            try:
                res = requests.post(self.webhook_url, json=payload, timeout=10)
                if res.status_code in [200, 204]:
                    return True
                elif res.status_code == 429:
                    retry_after = res.json().get("retry_after", 1.5)
                    time.sleep(retry_after)
                    continue
            except Exception:
                time.sleep(1)
        return False

    def send_batch_file(self, filepath: str, total_success: int, total_failed: int, elapsed_seconds: float) -> bool:
        """Gửi đính kèm file accounts.txt chứa toàn bộ lô tài khoản vừa tạo về Discord Webhook."""
        if not self.is_valid():
            return False
        if not os.path.exists(filepath):
            return False

        filename = os.path.basename(filepath)
        filesize_kb = os.path.getsize(filepath) / 1024
        mins, secs = divmod(int(elapsed_seconds), 60)
        time_str = f"{mins}m {secs}s" if mins > 0 else f"{secs}s"
        speed = (total_success / max(1, elapsed_seconds)) * 60

        embed = {
            "title": "📦 HOÀN TẤT ĐĂNG KÝ LÔ TÀI KHOẢN ROBLOX!",
            "description": f"Đã hoàn thành toàn bộ tiến trình tạo lô tài khoản trên **Termux Cloud Phone**!\nFile danh sách tài khoản đã được đính kèm bên dưới 👇",
            "color": 3066993, # Neon Teal/Green
            "fields": [
                {
                    "name": "✅ Thành công",
                    "value": f"**`{total_success}` tài khoản**",
                    "inline": True
                },
                {
                    "name": "❌ Thất bại",
                    "value": f"`{total_failed}` lượt",
                    "inline": True
                },
                {
                    "name": "⏱️ Thời gian chạy",
                    "value": f"`{time_str}` (~{speed:.1f} acc/phút)",
                    "inline": True
                },
                {
                    "name": "📁 Tên File",
                    "value": f"`{filename}` ({filesize_kb:.1f} KB)",
                    "inline": True
                },
                {
                    "name": "📝 Định dạng",
                    "value": "`username:password:cookie`",
                    "inline": True
                }
            ],
            "footer": {
                "text": "⚡ Termux Cloud Phone Bot • Batch Export",
                "icon_url": "https://images.rbxcdn.com/2b356da0fbab61db57b2de9ced8808d9.ico"
            },
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

        payload = {
            "username": "Roblox Batch Exporter",
            "avatar_url": "https://tr.rbxcdn.com/30DAY-AvatarHeadshot-B101D05B73E0C1CF85C0CEAC33B0A956-Png/150/150/AvatarHeadshot/Webp/noFilter",
            "content": f"📢 **THÔNG BÁO HOÀN THÀNH LÔ `{total_success}` ACC!** File danh sách tài khoản đã được tải lên bên dưới:",
            "embeds": [embed]
        }

        for attempt in range(3):
            try:
                with open(filepath, "rb") as f:
                    files = {
                        "file": (filename, f, "text/plain")
                    }
                    res = requests.post(
                        self.webhook_url,
                        data={"payload_json": json.dumps(payload)},
                        files=files,
                        timeout=35
                    )
                    if res.status_code in [200, 204]:
                        return True
                    elif res.status_code == 429:
                        retry_after = res.json().get("retry_after", 2.0)
                        time.sleep(retry_after)
                        continue
            except Exception:
                time.sleep(1)
        return False
