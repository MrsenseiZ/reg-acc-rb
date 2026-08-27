#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module Quản lý Proxy & Sticky Session cho Termux
Hỗ trợ HTTP/HTTPS/SOCKS5, cấp phát đa luồng và tương thích mọi định dạng Proxy (Nettify, Luna, Webshare, v.v.).
"""

import os
import shutil
import random
import string
import subprocess
import threading
from typing import Optional, List, Dict

class ProxyManager:
    def __init__(self, proxy_file: str = "proxies.txt", enabled: bool = True, sticky: bool = True):
        self.proxy_file = proxy_file
        self.enabled = enabled
        self.sticky = sticky
        self.proxies: List[str] = []
        self.fail_counts: Dict[str, int] = {}
        self.lock = threading.Lock()
        
        if self.enabled:
            self.load_proxies()

    def format_proxy(self, raw: str) -> Optional[str]:
        """Chuẩn hóa mọi định dạng proxy về http://user:pass@host:port"""
        s = raw.strip()
        if not s or s.startswith("#"):
            return None
        if s.startswith("http://") or s.startswith("https://") or s.startswith("socks5://"):
            return s
        
        # Định dạng dạng user:pass@host:port (như ảnh Nettify)
        if "@" in s:
            return f"http://{s}"

        # Định dạng dạng host:port:user:pass
        parts = s.split(":")
        if len(parts) == 4:
            host, port, user, pwd = parts
            return f"http://{user}:{pwd}@{host}:{port}"
        # Định dạng dạng host:port (không pass)
        elif len(parts) == 2:
            return f"http://{parts[0]}:{parts[1]}"
        return f"http://{s}"

    def load_proxies(self) -> int:
        if not os.path.exists(self.proxy_file):
            return 0
        loaded = []
        with open(self.proxy_file, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                p = self.format_proxy(line)
                if p:
                    loaded.append(p)
        with self.lock:
            self.proxies = loaded
            self.fail_counts.clear()
        return len(self.proxies)

    def mark_fail(self, proxy_str: Optional[str]):
        if not proxy_str:
            return
        with self.lock:
            self.fail_counts[proxy_str] = self.fail_counts.get(proxy_str, 0) + 1

    def get_proxy(self, slot_id: int = 0) -> Optional[str]:
        if not self.enabled or not self.proxies:
            return None
        with self.lock:
            valid = [p for p in self.proxies if self.fail_counts.get(p, 0) < 4]
            if not valid:
                self.fail_counts.clear()
                valid = self.proxies
            base_proxy = valid[slot_id % len(valid)]

            if self.sticky and "@" in base_proxy:
                sid = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
                if "-session-" not in base_proxy and "_session-" not in base_proxy:
                    try:
                        proto, rest = base_proxy.split("://", 1)
                        user_pass, host_port = rest.split("@", 1)
                        if ":" in user_pass:
                            user, pwd = user_pass.split(":", 1)
                            user = f"{user}-session-{sid}"
                            return f"{proto}://{user}:{pwd}@{host_port}"
                    except Exception:
                        pass
            return base_proxy

    @staticmethod
    def to_requests_proxies(proxy_str: Optional[str]) -> Optional[dict]:
        if not proxy_str:
            return None
        p = proxy_str
        if p.startswith("socks5://"):
            p = "socks5h://" + p[len("socks5://"):]
        return {"http": p, "https": p}

    @staticmethod
    def set_android_global_proxy(host: str, port: int) -> bool:
        """Gán Proxy HTTP toàn hệ thống Android / Cloud Phone qua Root hoặc ADB."""
        cmds = [
            f"settings put global http_proxy {host}:{port}",
            f"settings put global global_http_proxy_host {host}",
            f"settings put global global_http_proxy_port {port}"
        ]
        success = False
        for root_cmd in ["su", "tsu"]:
            if shutil.which(root_cmd):
                try:
                    for c in cmds:
                        subprocess.run(f"{root_cmd} -c '{c}'", shell=True, capture_output=True, timeout=5)
                    success = True
                    break
                except Exception:
                    pass
        if not success and shutil.which("adb"):
            try:
                for c in cmds:
                    subprocess.run(["adb", "shell"] + c.split(), capture_output=True, timeout=5)
                success = True
            except Exception:
                pass
        return success

    @staticmethod
    def clear_android_global_proxy() -> bool:
        """Xóa Proxy toàn hệ thống Android / Cloud Phone."""
        cmds = [
            "settings put global http_proxy :0",
            "settings delete global http_proxy",
            "settings delete global global_http_proxy_host",
            "settings delete global global_http_proxy_port"
        ]
        for root_cmd in ["su", "tsu"]:
            if shutil.which(root_cmd):
                try:
                    for c in cmds:
                        subprocess.run(f"{root_cmd} -c '{c}'", shell=True, capture_output=True, timeout=5)
                    return True
                except Exception:
                    pass
        if shutil.which("adb"):
            try:
                for c in cmds:
                    subprocess.run(["adb", "shell"] + c.split(), capture_output=True, timeout=5)
                return True
            except Exception:
                pass
        return False
