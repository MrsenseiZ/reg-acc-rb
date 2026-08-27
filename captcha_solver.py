#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module Giải FunCaptcha / Arkose Labs API cho Termux
Hỗ trợ: OmoCaptcha, YesCaptcha, CapSolver, 2Captcha
"""

import time
import requests
from typing import Optional, Dict, Any

class CaptchaSolver:
    def __init__(self, provider: str = "omocaptcha", api_key: str = "", sitekey: str = "47A08D90-3D8B-4C9A-9F09-6B6F9374B358"):
        self.provider = provider.lower()
        self.api_key = api_key
        self.sitekey = sitekey
        self.website_url = "https://www.roblox.com/CreateAccount"

    def get_balance(self) -> str:
        """Kiểm tra số dư API Captcha."""
        if not self.api_key:
            return "Chưa nhập API Key"
        try:
            if self.provider == "omocaptcha":
                r = requests.post("https://api.omocaptcha.com/v2/getBalance", json={"clientKey": self.api_key}, timeout=8)
                data = r.json()
                if data.get("errorId") == 0:
                    return f"{data.get('balance', 0)} VNĐ"
            elif self.provider == "yescaptcha":
                r = requests.post("https://api.yescaptcha.com/getBalance", json={"clientKey": self.api_key}, timeout=8)
                data = r.json()
                if data.get("errorId") == 0:
                    return f"{data.get('balance', 0)} Xu"
            elif self.provider == "capsolver":
                r = requests.post("https://api.capsolver.com/getBalance", json={"clientKey": self.api_key}, timeout=8)
                data = r.json()
                if data.get("errorId") == 0:
                    return f"${data.get('balance', 0)}"
        except Exception as e:
            return f"Lỗi: {e}"
        return "N/A"

    def solve_arkose(self, blob_data: Optional[str] = None, proxy_str: Optional[str] = None) -> Optional[str]:
        """Giải FunCaptcha và trả về captchaToken."""
        if not self.api_key:
            return None

        if self.provider == "omocaptcha":
            return self._solve_omocaptcha(blob_data)
        elif self.provider == "yescaptcha":
            return self._solve_yescaptcha(blob_data)
        elif self.provider == "capsolver":
            return self._solve_capsolver(blob_data, proxy_str)
        else:
            return self._solve_omocaptcha(blob_data)

    def _solve_omocaptcha(self, blob_data: Optional[str]) -> Optional[str]:
        endpoints_create = [
            "https://api.omocaptcha.com/v2/createTask",
            "https://api.omocaptcha.com/createTask"
        ]
        task_data = {
            "type": "FuncaptchaImageTask",
            "websiteURL": self.website_url,
            "websitePublicKey": self.sitekey
        }
        if blob_data:
            task_data["data"] = f'{{"blob":"{blob_data}"}}'

        payload = {
            "clientKey": self.api_key,
            "task": task_data
        }

        task_id = None
        for url in endpoints_create:
            try:
                r = requests.post(url, json=payload, timeout=12)
                res = r.json()
                if res.get("errorId") == 0 or res.get("status") == "success":
                    task_id = res.get("taskId") or res.get("job_id")
                    if task_id:
                        break
            except Exception:
                continue

        if not task_id:
            return None

        # Polling kết quả
        endpoints_res = [
            "https://api.omocaptcha.com/v2/getTaskResult",
            "https://api.omocaptcha.com/getTaskResult"
        ]
        poll_payload = {"clientKey": self.api_key, "taskId": task_id, "job_id": task_id}

        for _ in range(35):
            time.sleep(2.5)
            for url in endpoints_res:
                try:
                    r = requests.post(url, json=poll_payload, timeout=10)
                    data = r.json()
                    status = (data.get("status") or "").lower()
                    if status in ["ready", "success"]:
                        sol = data.get("solution", {})
                        token = sol.get("token") or data.get("result")
                        if token:
                            return token
                    elif status in ["processing", "pending"]:
                        break
                except Exception:
                    continue
        return None

    def _solve_yescaptcha(self, blob_data: Optional[str]) -> Optional[str]:
        payload = {
            "clientKey": self.api_key,
            "task": {
                "type": "FunCaptchaTokenTask",
                "websiteURL": self.website_url,
                "websitePublicKey": self.sitekey
            }
        }
        if blob_data:
            payload["task"]["data"] = f'{{"blob":"{blob_data}"}}'

        try:
            r = requests.post("https://api.yescaptcha.com/createTask", json=payload, timeout=12)
            res = r.json()
            task_id = res.get("taskId")
            if not task_id:
                return None

            for _ in range(35):
                time.sleep(2.5)
                r = requests.post("https://api.yescaptcha.com/getTaskResult", json={"clientKey": self.api_key, "taskId": task_id}, timeout=10)
                data = r.json()
                if data.get("status") == "ready":
                    return data.get("solution", {}).get("token")
        except Exception:
            pass
        return None

    def _solve_capsolver(self, blob_data: Optional[str], proxy_str: Optional[str]) -> Optional[str]:
        task_data = {
            "type": "FunCaptchaTaskProxyLess",
            "websiteURL": self.website_url,
            "websitePublicKey": self.sitekey
        }
        if blob_data:
            task_data["data"] = f'{{"blob":"{blob_data}"}}'

        try:
            r = requests.post("https://api.capsolver.com/createTask", json={"clientKey": self.api_key, "task": task_data}, timeout=12)
            res = r.json()
            task_id = res.get("taskId")
            if not task_id:
                return None

            for _ in range(35):
                time.sleep(2.5)
                r = requests.post("https://api.capsolver.com/getTaskResult", json={"clientKey": self.api_key, "taskId": task_id}, timeout=10)
                data = r.json()
                if data.get("status") == "ready":
                    return data.get("solution", {}).get("token")
        except Exception:
            pass
        return None
