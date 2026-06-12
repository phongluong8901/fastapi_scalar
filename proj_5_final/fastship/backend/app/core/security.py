from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel


oauth2_scheme_seller = OAuth2PasswordBearer(tokenUrl="/seller/token", scheme_name="Seller")
oauth2_scheme_partner = OAuth2PasswordBearer(tokenUrl="/partner/token", scheme_name="Delivery Partner")


class TokenData(BaseModel):
    access_token: str
    token_type: str


# 1. OAuth2PasswordBearer là gì?
# Đây là một công cụ của FastAPI dựa trên tiêu chuẩn OAuth2. Nó đóng vai trò như một "lễ tân" kiểm tra vé (token):

# Khi có một Request (yêu cầu) gửi lên server, nó sẽ tự động tìm trong phần Authorization header để xem có Bearer [TOKEN] hay không.

# Nếu không có token, hoặc token không hợp lệ, nó sẽ từ chối truy cập (trả về lỗi 401 Unauthorized) ngay lập tức trước khi Request kịp chạm tới các hàm xử lý bên trong.

# 2. Tại sao bạn cần 2 cái khác nhau (_seller và _partner)?
# Hệ thống của bạn có 2 nhóm người dùng với quyền hạn khác nhau:

# oauth2_scheme_seller: Dùng cho các route (đường dẫn) dành riêng cho người bán (ví dụ: tạo đơn hàng, quản lý kho). Nó chỉ cho phép token được cấp từ /seller/token.

# oauth2_scheme_partner: Dùng cho các route dành riêng cho shipper (ví dụ: nhận đơn, cập nhật trạng thái). Nó chỉ cho phép token được cấp từ /partner/token.