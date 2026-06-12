from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_session
from app.services.shipment import ShipmentService


# Asynchronous database session dep annotation
SessionDep = Annotated[AsyncSession, Depends(get_session)]


# Shipment service dep
def get_shipment_service(session: SessionDep):
    return ShipmentService(session)


# Shipment service dep annotation
ServiceDep = Annotated[
    ShipmentService,
    Depends(get_shipment_service),
]

#---
# Đoạn code này là một kỹ thuật Dependency Injection (DI) rất chuyên nghiệp trong FastAPI. Nó giúp mã nguồn của bạn sạch sẽ, dễ bảo trì và dễ viết Unit Test.
# Tại sao dùng Annotated? Đây là cách chuẩn của FastAPI để khai báo một phụ thuộc. Thay vì viết Depends(...) lặp đi lặp lại trong mọi hàm API, bạn chỉ cần dùng SessionDep.

# Lợi ích: Khi cần thay đổi cách lấy session (ví dụ từ get_session sang một hàm khác), bạn chỉ cần sửa ở đúng một dòng này, thay vì sửa ở hàng chục file API khác nhau.

# ServiceDep = Annotated[ShipmentService, Depends(get_shipment_service)]
# Đây là điểm hay nhất: Bạn đã "đóng gói" cả quy trình lấy Service vào một biến duy nhất.

#---
# 1. ShipmentService (Mặt Định danh/Kiểu dữ liệu)
# Đây là mặt "Biết".

# Nó thông báo cho IDE và Python biết: "Cái biến này sẽ chứa các phương thức như get, add, update, delete".

# Nếu không có nó, IDE sẽ "mù". Khi bạn gõ service., nó sẽ không hiện gợi ý gì cả vì nó không biết service là cái gì.

# 2. Depends(get_shipment_service) (Mặt Hành động/Thực thi)
# Đây là mặt "Làm".

# Nó thông báo cho FastAPI biết: "Khi nào có một yêu cầu (request) tới, hãy chạy hàm get_shipment_service này để tạo ra đối tượng thật sự".

# FastAPI sẽ thực thi hàm này, lấy kết quả trả về (thường là một instance ShipmentService(...)), và "bơm" nó vào biến service của bạn.