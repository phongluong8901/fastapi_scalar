from datetime import datetime
from enum import Enum
from sqlmodel import Field, SQLModel

# Định nghĩa các trạng thái cố định cho đơn hàng
class ShipmentStatus(str, Enum):
    # Dùng Enum để đảm bảo dữ liệu status chỉ được phép nhận 4 giá trị này
    placed = "placed"
    in_transit = "in_transit"
    out_for_delivery = "out_for_delivery"
    delivered = "delivered"

# Định nghĩa bảng 'shipment' trong cơ sở dữ liệu
class Shipment(SQLModel, table = True):
    # Tên bảng thực tế trong database
    __tablename__ = "shipment"

    # id là khóa chính, tự động sinh và tăng dần (default=None giúp SQLModel hiểu đây là auto-increment)
    id: int = Field(default=None, primary_key=True)
    
    # Các cột dữ liệu của bảng
    content: str               # Nội dung hàng hóa
    weight: float = Field(le=25) # Cân nặng (phải <= 25)
    destination: int           # Mã điểm đến
    
    # Trường này sử dụng Enum đã định nghĩa ở trên để ràng buộc giá trị
    status: ShipmentStatus     
    
    # Thời gian giao hàng (kiểu datetime để lưu cả ngày và giờ)
    estimated_delivery: datetime