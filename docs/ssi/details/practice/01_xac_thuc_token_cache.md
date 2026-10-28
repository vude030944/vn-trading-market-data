<!--
Nguon goc (source): https://developers.ssi.com.vn/docs/tutorials/auth
Tieu de goc: 1. Xác thực & Token Cache
Cap nhat (fetched): 2026-08-17
-->

> **Nguồn:** <https://developers.ssi.com.vn/docs/tutorials/auth>

# 1\. Xác thực & Token Cache

Đăng nhập và lấy Access Token, cache token để tái sử dụng giữa các lần chạy

## Mục tiêu

Đăng nhập vào hệ thống FastConnect và lấy token cho toàn bộ API call sau đó. Sử dụng token cache để tránh authenticate lại mỗi lần chạy script.

## Luồng xử lý
```text
Client App → Auth API → token_cache.json
```

  1. Tạo `Config` → `Auth` → gọi `ensure_auth(auth, otp=...)`
  2. `ensure_auth` load token từ cache, authenticate nếu chưa có, refresh nếu hết hạn
  3. Auth service trả về `accessToken`, `refreshToken`, `expiresIn` và lưu vào `token_cache.json`
  4. Mọi request sau đó gắn `Authorization: Bearer <accessToken>`
  5. Nếu token hết hạn ở lần sau thì tự động refresh, không cần OTP lại

## auth_helper — Token Cache Module

Module `auth_helper.py` giúp tái sử dụng token giữa các lần chạy script:

python/auth_helper.py
```python
"""
auth_helper — Token cache để tái sử dụng token giữa các lần chạy
==================================================================
Thay vì gọi authenticate() mỗi lần chạy script, module này:
  1. Load token đã lưu từ file token_cache.json (nếu có)
  2. Nếu chưa có → authenticate lần đầu và lưu xuống file
  3. Nếu token hết hạn → refresh và lưu lại
  4. Nếu token còn hạn → dùng trực tiếp, không gọi API

Cách dùng (sync):
    from auth_helper import ensure_auth
    with Auth(config) as auth:
        ensure_auth(auth)

Cách dùng (async):
    from auth_helper import ensure_auth_async
    async with AsyncAuth(config) as auth:
        await ensure_auth_async(auth)
"""

import json
import os

from ssi_sdk.models import Token

TOKEN_FILE = os.path.join(os.path.dirname(__file__), "token_cache.json")

def load_token() -> Token | None:
    """Load token từ file, trả về None nếu file không tồn tại."""
    if not os.path.exists(TOKEN_FILE):
        return None
    with open(TOKEN_FILE, "r", encoding="utf-8") as f:
        _token = json.load(f)
    return Token.from_dict(_token)

def save_token(token: Token) -> None:
    """Lưu token xuống file."""
    with open(TOKEN_FILE, "w", encoding="utf-8") as f:
        json.dump(token.to_dict(), f, indent=2)
    print(f"Token đã lưu vào {TOKEN_FILE}")

def ensure_auth(auth, otp: str | None = None) -> None:
    """Đảm bảo auth có token hợp lệ (sync)."""
    cached_token = load_token()
    if cached_token is None:
        print("Không tìm thấy file token, đang authenticate...")
        cached_token = auth.token_manager.authenticate(otp=otp) if otp else auth.token_manager.authenticate()
        save_token(cached_token)
        print("Authenticate thành công, token đã lưu.")
    auth.token_manager.set_token(cached_token)
    if auth.token_manager.is_token_expired:
        print("Token đã hết hạn, đang refresh...")
        cached_token = auth.token_manager.refresh()
        save_token(cached_token)
        print("Refresh token thành công.")
    else:
        print("Token còn hạn, dùng token từ file.")

async def ensure_auth_async(auth, otp: str | None = None) -> None:
    """Đảm bảo auth có token hợp lệ (async)."""
    cached_token = load_token()
    if cached_token is None:
        print("Không tìm thấy file token, đang authenticate...")
        cached_token = await auth.token_manager.authenticate(otp=otp) if otp else await auth.token_manager.authenticate()
        save_token(cached_token)
        print("Authenticate thành công, token đã lưu.")
    await auth.token_manager.set_token(cached_token)
    if auth.token_manager.is_token_expired:
        print("Token đã hết hạn, đang refresh...")
        cached_token = await auth.token_manager.refresh()
        save_token(cached_token)
        print("Refresh token thành công.")
    else:
        print("Token còn hạn, dùng token từ file.")
```

## Sample Code — Sync

python/sample_01_auth.py
```python
from ssi_sdk import Auth, Trading, Config
from auth_helper import ensure_auth

config = Config(
    client_id="<your_client_id>",
    api_key="<your_api_key>",
    api_secret="<your_api_secret>",
    private_key="<your_private_key>",
)

with Auth(config) as auth:
    # Bước 1-2: Xác thực, nhận accessToken + refreshToken
    ensure_auth(auth)
    token = auth.token
    print("Access Token :", token.access_token[:40], "...")
    print("Token Type   :", token.token_type)
    print("Expires At   :", token.expires_at)

    # Bước 3: Token đã được SDK lưu tự động
    # Mọi request kế tiếp sẽ gắn header Authorization: Bearer <accessToken>

    # Bước 4: Kiểm tra token hết hạn & refresh
    if auth.is_token_expired:
        new_token = auth.refresh()
        print("Token mới:", new_token.access_token[:40], "...")

    # Xác nhận token hoạt động bằng cách gọi API
    with Trading(auth) as trading:
        accounts = trading.account.get_account_info()
        print(f"\nXác thực thành công! Tìm thấy {len(accounts)} tài khoản:")
        for acc in accounts:
            print(f"  - {acc.account_no} ({acc.account_type.value})")
```

## Sample Code — Async

python/sample_01_auth_async.py
```python
import asyncio
from ssi_sdk import AsyncAuth, AsyncTrading, Config
from auth_helper import ensure_auth_async

config = Config(
    client_id="<your_client_id>",
    api_key="<your_api_key>",
    api_secret="<your_api_secret>",
    private_key="<your_private_key>",
)

async def main():
    async with AsyncAuth(config) as auth:
        await ensure_auth_async(auth)
        token = auth.token
        print("Access Token :", token.access_token[:40], "...")

        if auth.is_token_expired:
            new_token = await auth.refresh()
            print("Token mới:", new_token.access_token[:40], "...")

        async with AsyncTrading(auth) as trading:
            accounts = await trading.account.get_account_info()
            print(f"\nXác thực thành công! Tìm thấy {len(accounts)} tài khoản:")
            for acc in accounts:
                print(f"  - {acc.account_no} ({acc.account_type.value})")

asyncio.run(main())
```

## Sample Code — Approve OTP (Sync)

Với tài khoản đã kích hoạt Smart OTP, thay vì nhập mã số, người dùng có thể bấm "Duyệt" trực tiếp trên app. SDK tự động poll cho đến khi user duyệt xong hoặc hết số lần thử.

python/sample_01_auth_approve_otp.py
```python
from ssi_sdk import Auth, Config

config = Config(
    client_id="<your_client_id>",
    api_key="<your_api_key>",
    api_secret="<your_api_secret>",
    private_key="<your_private_key>",
)

with Auth(config) as auth:
    # Bước 1: gửi yêu cầu duyệt tới app Smart OTP, nhận transaction_id
    otp_result = auth.request_otp()
    transaction_id = otp_result["transactionId"]
    print("Đã gửi yêu cầu duyệt. Vui lòng mở app Smart OTP và bấm Duyệt.")

    # Bước 2: SDK tự poll cho đến khi user bấm duyệt (hoặc hết poll_max_retries)
    token = auth.ensure_authenticated(
        transaction_id=transaction_id,
        poll_interval=5,
        poll_max_retries=5,
    )
    print("Duyệt thành công! Access Token:", token.access_token[:40], "...")
```

## Sample Code — Approve OTP (Async)

python/sample_01_auth_approve_otp_async.py
```python
import asyncio
from ssi_sdk import AsyncAuth, Config

config = Config(
    client_id="<your_client_id>",
    api_key="<your_api_key>",
    api_secret="<your_api_secret>",
    private_key="<your_private_key>",
)

async def main():
    async with AsyncAuth(config) as auth:
        # Bước 1: gửi yêu cầu duyệt tới app Smart OTP, nhận transaction_id
        otp_result = await auth.request_otp()
        transaction_id = otp_result["transactionId"]
        print("Đã gửi yêu cầu duyệt. Vui lòng mở app Smart OTP và bấm Duyệt.")

        # Bước 2: SDK tự poll cho đến khi user bấm duyệt (hoặc hết poll_max_retries)
        token = await auth.ensure_authenticated(
            transaction_id=transaction_id,
            poll_interval=5,
            poll_max_retries=5,
        )
        print("Duyệt thành công! Access Token:", token.access_token[:40], "...")

asyncio.run(main())
```

Cách này chỉ áp dụng cho tài khoản đã kích hoạt Smart OTP. Tài khoản dùng OTP SMS/email thông thường vẫn dùng `ensure_auth(auth, otp=...)` như phần Sample Code ở trên.

## Lưu ý quan trọng

  * **Không hard-code credentials** trong mã nguồn. Sử dụng biến môi trường hoặc file cấu hình.
  * **OTP** chỉ cần ở lần authenticate đầu tiên. Các lần sau dùng refresh token.
  * **Token cache** (`token_cache.json`) nên được thêm vào `.gitignore`.
  * SDK tự động gắn `Authorization: Bearer <accessToken>` cho mọi request.
