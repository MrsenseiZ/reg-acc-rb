#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module Giao Tiếp API Roblox (REST Signup Engine)
Tối ưu hóa siêu nhẹ cho Termux / Android, xử lý Challenge Captcha và Cookie an toàn.
"""

import re
import json
import base64
import random
import requests
from typing import Optional, Dict, Any, Tuple

from captcha_solver import CaptchaSolver
from proxy_manager import ProxyManager

USER_AGENTS = [
    # Android Mobile User Agents
    "Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.6943.99 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; Pixel 7 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.6834.163 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 12; Redmi Note 11) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.200 Mobile Safari/537.36",
    # Desktop UA Fallback
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
]

COOKIE_RE = re.compile(r"\.ROBLOSECURITY=([^;]+)", re.IGNORECASE)

class RobloxApiEngine:
    SIGNUP_URL = "https://auth.roblox.com/v2/signup"
    CSRF_URL = "https://auth.roblox.com/v2/logout"
    CHALLENGE_CONTINUE_URL = "https://apis.roblox.com/challenge/v1/continue"

    def __init__(self, solver: CaptchaSolver, proxy_str: Optional[str] = None):
        self.solver = solver
        self.proxy_str = proxy_str
        self.session = requests.Session()
        
        adapter = requests.adapters.HTTPAdapter(pool_connections=10, pool_maxsize=10, max_retries=1)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

        if self.proxy_str:
            px = ProxyManager.to_requests_proxies(self.proxy_str)
            if px:
                self.session.proxies.update(px)

        self.ua = random.choice(USER_AGENTS)
        self.session.headers.update({
            "User-Agent": self.ua,
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Content-Type": "application/json;charset=UTF-8",
            "Origin": "https://www.roblox.com",
            "Referer": "https://www.roblox.com/",
            "Sec-Ch-Ua-Mobile": "?1",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site"
        })
        self.csrf_token = ""

    def get_csrf(self) -> str:
        """Lấy CSRF Token mới nhất."""
        try:
            r = self.session.post(self.CSRF_URL, json={}, timeout=10)
            token = r.headers.get("x-csrf-token")
            if token:
                self.csrf_token = token
                self.session.headers["x-csrf-token"] = token
                return token
        except Exception:
            pass
        return ""

    def extract_cookie(self, res: requests.Response) -> str:
        """Trích xuất .ROBLOSECURITY từ headers Set-Cookie."""
        ck = res.cookies.get(".ROBLOSECURITY")
        if ck and ck.startswith("_|WARNING:"):
            return ck

        raw_headers = res.raw.headers if hasattr(res, "raw") and hasattr(res.raw, "headers") else {}
        set_cookies = raw_headers.getlist("set-cookie") if hasattr(raw_headers, "getlist") else [res.headers.get("set-cookie", "")]
        
        for sc in set_cookies:
            if ".ROBLOSECURITY=" in sc:
                m = COOKIE_RE.search(sc)
                if m:
                    val = m.group(1).strip()
                    if val.startswith("_|WARNING:"):
                        return val
        return ""

    def register(self, username: str, password: str, birthday_iso: str, gender: int = 2) -> Tuple[bool, Optional[str], Optional[int], str]:
        """
        Thực hiện chu trình đăng ký:
        1. Gửi POST /v2/signup
        2. Nếu dính Arkose Challenge -> Giải qua CaptchaSolver API
        3. Tiếp tục Challenge và lấy Cookie .ROBLOSECURITY
        Trả về: (Thành_công, Cookie, User_ID, Thông_báo)
        """
        if not self.csrf_token:
            self.get_csrf()

        payload = {
            "username": username,
            "password": password,
            "birthday": birthday_iso,
            "gender": gender,
            "isTosAgreementBoxChecked": True,
            "context": "MultiverseSignupForm",
            "agreementIds": [
                "848d7d8f-dd51-46b0-8438-e621644e5bc5",
                "54d8a8f0-d9c8-472a-9f9a-7ff6e13d7c61"
            ]
        }

        try:
            res = self.session.post(self.SIGNUP_URL, json=payload, timeout=15)
            
            # Cập nhật CSRF nếu hết hạn
            if res.status_code == 403 and res.headers.get("x-csrf-token") and not res.headers.get("rblx-challenge-id"):
                self.csrf_token = res.headers.get("x-csrf-token")
                self.session.headers["x-csrf-token"] = self.csrf_token
                res = self.session.post(self.SIGNUP_URL, json=payload, timeout=15)

            # Trường hợp 1: Thành công trực tiếp không dính Captcha (Clean IP)
            if res.status_code == 200:
                cookie = self.extract_cookie(res)
                data = res.json()
                user_id = data.get("userId")
                return True, cookie, user_id, "Thành công (Không dính Captcha)"

            # Trường hợp 2: Dính Arkose FunCaptcha Challenge
            if res.status_code == 403 and res.headers.get("rblx-challenge-id"):
                challenge_id = res.headers.get("rblx-challenge-id")
                challenge_type = res.headers.get("rblx-challenge-type", "captcha")
                raw_meta = res.headers.get("rblx-challenge-metadata", "")

                blob_data = None
                unified_id = ""
                
                if raw_meta:
                    try:
                        decoded_meta = json.loads(base64.b64decode(raw_meta).decode('utf-8'))
                        unified_id = decoded_meta.get("unifiedCaptchaId", "")
                        shared_params = decoded_meta.get("sharedParameters", {})
                        blob_data = decoded_meta.get("dataExchangeBlob") or shared_params.get("blob")
                    except Exception:
                        pass

                # Gọi Solver giải FunCaptcha
                captcha_token = self.solver.solve_arkose(blob_data=blob_data, proxy_str=self.proxy_str)
                if not captcha_token:
                    return False, None, None, "Thất bại: Không giải được Captcha (Hết hạn hoặc lỗi Solver)"

                # Gửi kết quả giải tới Roblox Challenge API
                continue_meta = {
                    "unifiedCaptchaId": unified_id,
                    "captchaToken": captcha_token,
                    "actionType": "Signup"
                }
                
                continue_payload = {
                    "challengeId": challenge_id,
                    "challengeType": challenge_type,
                    "challengeMetadata": json.dumps(continue_meta)
                }

                # Gửi xác thực challenge
                c_res = self.session.post(self.CHALLENGE_CONTINUE_URL, json=continue_payload, timeout=12)
                
                # Thử gửi lại request đăng ký
                retry_headers = {
                    "rblx-challenge-id": challenge_id,
                    "rblx-challenge-type": challenge_type,
                    "rblx-challenge-metadata": base64.b64encode(json.dumps(continue_meta).encode('utf-8')).decode('utf-8')
                }
                res = self.session.post(self.SIGNUP_URL, json=payload, headers=retry_headers, timeout=15)

                if res.status_code == 200:
                    cookie = self.extract_cookie(res)
                    data = res.json()
                    user_id = data.get("userId")
                    return True, cookie, user_id, "Thành công (Đã vượt Captcha)"
                else:
                    return False, None, None, f"Lỗi hoàn tất đăng ký ({res.status_code}): {res.text[:100]}"

            # Các lỗi khác (Tên trùng, rate limit, IP blacklist)
            err_msg = res.text[:120]
            try:
                err_json = res.json()
                if "errors" in err_json and len(err_json["errors"]) > 0:
                    err_msg = err_json["errors"][0].get("message", err_msg)
            except Exception:
                pass
            return False, None, None, f"Roblox từ chối ({res.status_code}): {err_msg}"

        except Exception as e:
            return False, None, None, f"Lỗi kết nối: {e}"
