from pydantic import BaseModel, EmailStr, Field


# --- CÁC SCHEMA CHO DELIVERY PARTNER ---

# Lớp cơ sở chứa thông tin cốt lõi của một đối tác
class BaseDeliveryPartner(BaseModel):
    name: str                        # Tên đối tác
    email: EmailStr                  # Email (tự động kiểm tra định dạng)
    serviceable_zip_codes: list[int] # Danh sách mã bưu điện hỗ trợ
    max_handling_capacity: int       # Năng lực xử lý đơn hàng tối đa

# Lớp dùng để TRẢ DỮ LIỆU về cho Client (Read)
class DeliveryPartnerRead(BaseDeliveryPartner):
    pass                             # Trả về toàn bộ thông tin cơ bản (không trả mật khẩu)

# Lớp dùng để CẬP NHẬT thông tin đối tác (Update)
class DeliveryPartnerUpdate(BaseModel):
    # Sử dụng '| None = Field(default=None)' để cho phép cập nhật từng phần
    # Người dùng chỉ cần gửi những trường muốn thay đổi, trường khác để trống
    serviceable_zip_codes: list[int] | None = Field(default=None)
    max_handling_capacity: int | None = Field(default=None)

# Lớp dùng để ĐĂNG KÝ đối tác mới (Create)
class DeliveryPartnerCreate(BaseDeliveryPartner):
    password: str                    # Thêm mật khẩu để nhận từ Client khi tạo tài khoản