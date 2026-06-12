from datetime import datetime, timedelta, timezone # Thư viện xử lý thời gian
from json import JSONDecodeError, dumps            # Xử lý định dạng JSON
from pathlib import Path                           # Xử lý đường dẫn file
from typing import Any, Mapping                    # Định nghĩa kiểu dữ liệu linh hoạt
from uuid import uuid4                            # Tạo mã định danh duy nhất (UUID)

import jwt                                        # Thư viện xử lý JSON Web Tokens
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer # Thư viện tạo token an toàn cho URL

from app.config import security_settings           # Import cấu hình bảo mật từ file config

# Khởi tạo bộ mã hóa/giải mã token an toàn với khóa bí mật
_serializer = URLSafeTimedSerializer(security_settings.JWT_SECRET)

# Xác định đường dẫn thư mục hiện tại và thư mục templates
APP_DIR = Path(__file__).resolve().parent
TEMPLATE_DIR = APP_DIR / "templates"


def generate_access_token(data: dict, expiry: timedelta = timedelta(days=7)) -> str:
    return jwt.encode( # Tạo chuỗi JWT từ dữ liệu
        payload={
            **data,                             # Giải nén nội dung dữ liệu người dùng
            "jti": str(uuid4()),               # Tạo ID duy nhất cho token (chống replay attack)
            "exp": datetime.now(timezone.utc) + expiry, # Thiết lập thời gian hết hạn
        },
        algorithm=security_settings.JWT_ALGORITHM, # Thuật toán mã hóa
        key=security_settings.JWT_SECRET,           # Khóa bí mật
    )

def decode_access_token(token: str) -> dict | None:
    try:
        return jwt.decode( # Giải mã và kiểm tra tính hợp lệ của JWT
            jwt=token,
            key=security_settings.JWT_SECRET,
            algorithms=[security_settings.JWT_ALGORITHM],
        )
    except jwt.PyJWTError: # Nếu token lỗi hoặc hết hạn, trả về None
        return None

#Xử lý URL Safe Token (Dùng cho kích hoạt tài khoản/quên mật khẩu)
def generate_url_safe_token(data: dict, salt: str | None = None) -> str:
    return _serializer.dumps(data, salt=salt) # Tạo token chuỗi an toàn cho URL

def decode_url_safe_token(token: str, salt: str | None = None, expiry: timedelta | None = None) -> dict | None:
    try:
        return _serializer.loads( # Giải mã và kiểm tra token
            token,
            salt=salt,
            max_age=expiry.total_seconds() if expiry else None, # Kiểm tra nếu token quá hạn
        )
    except (BadSignature, SignatureExpired): # Nếu chữ ký sai hoặc hết hạn, trả về None
        return None

#Tiện ích Debug (In dữ liệu ra màn hình)
def print_label(data: Any, title: str | None = None):
    from rich import print        # Thư viện in ấn đẹp mắt
    from rich.panel import Panel # Tạo khung bao quanh dữ liệu

    try:
        # Nếu data là dict, chuyển thành chuỗi JSON để in cho dễ đọc
        data = dumps(data, indent=4) if isinstance(data, (dict, Mapping)) else data
    except JSONDecodeError:
        pass

    print() # In dòng trống
    print( # In dữ liệu trong một khung Panel
        Panel(
            data,
            title=title, # Tiêu đề khung
        ),
        end="\n\n",
    )

#---



