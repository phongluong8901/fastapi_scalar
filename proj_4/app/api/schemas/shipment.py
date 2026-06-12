from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field

from app.database.models import ShipmentStatus


# --- CÁC SCHEMA CHO SHIPMENT ---

# Lớp cơ sở chứa các thuộc tính bắt buộc khi tạo mới
class BaseShipment(BaseModel):
    content: str               # Nội dung hàng hóa
    weight: float = Field(le=25) # Trọng lượng (tối đa 25kg)
    destination: int           # Mã bưu điện nơi đến

# Lớp dùng để TRẢ DỮ LIỆU về cho Client (Read)
class ShipmentRead(BaseShipment):
    id: UUID                   # Trả về ID của đơn hàng
    status: ShipmentStatus     # Trả về trạng thái hiện tại
    estimated_delivery: datetime # Trả về thời gian dự kiến

# Lớp dùng để NHẬN DỮ LIỆU khi tạo đơn (Create)
class ShipmentCreate(BaseShipment):
    pass                       # Chỉ cần name, weight, destination từ BaseShipment

# Lớp dùng để CẬP NHẬT đơn hàng (Update)
class ShipmentUpdate(BaseModel):
    # Dùng | None và default=None để cho phép người dùng chỉ cập nhật 1 trong 2 trường
    status: ShipmentStatus | None = Field(default=None)
    estimated_delivery: datetime | None = Field(default=None)