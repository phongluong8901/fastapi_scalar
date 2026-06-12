from pydantic import BaseModel, EmailStr # Nhập các thư viện để định nghĩa Schema và kiểm tra Email

class BaseSeller(BaseModel):             # Lớp cơ sở (cha) chứa các thuộc tính chung
    name: str                            # Thuộc tính tên người bán
    email: EmailStr                      # Thuộc tính email (tự động kiểm tra định dạng)

class SellerRead(BaseSeller):            # Lớp dùng để TRẢ DỮ LIỆU về cho Client (Read)
    pass                                 # Kế thừa hoàn toàn từ BaseSeller (chỉ trả về name, email)

class SellerCreate(BaseSeller):          # Lớp dùng để NHẬN DỮ LIỆU khi đăng ký (Create)
    password: str                        # Thêm mật khẩu vào Schema để nhận từ Client