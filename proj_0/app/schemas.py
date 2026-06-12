from datetime import datetime
from pydantic import BaseModel, Field
from app.database.models import ShipmentStatus

# Dùng làm khung chung cho các schema khác kế thừa
class BaseShipment(BaseModel):
    # Nội dung hàng hóa, bắt buộc là chuỗi
    content: str
    # Cân nặng là số thực, ràng buộc tối đa 25 đơn vị
    weight: float = Field(le=25)
    # Mã điểm đến là số nguyên
    destination: int

# Dùng để trả dữ liệu cho phía người dùng (Client)
class ShipmentRead(BaseShipment):
    # Trạng thái đơn hàng (sử dụng Enum đã định nghĩa trước)
    status: ShipmentStatus
    # Thời gian dự kiến giao hàng
    estimated_delivery: datetime

# Dùng khi Client gửi dữ liệu tạo đơn hàng mới
class ShipmentCreate(BaseShipment):
    # Kế thừa hoàn toàn từ BaseShipment, không thêm trường mới
    pass

# Dùng khi cập nhật đơn hàng (cho phép sửa từng phần)
class ShipmentUpdate(BaseModel):
    # Cho phép cập nhật trạng thái hoặc để trống (None)
    status: ShipmentStatus | None = Field(default=None)
    # Cho phép cập nhật thời gian hoặc để trống (None)
    estimated_delivery: datetime | None = Field(default=None)