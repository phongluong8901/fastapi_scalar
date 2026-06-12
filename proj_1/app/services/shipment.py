from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.shipment import ShipmentCreate
from app.database.models import Shipment, ShipmentStatus


class ShipmentService:
    def __init__(self, session: AsyncSession):
        # Get database session to perform database operations
        self.session = session

    # Get a shipment by id 
    async def get(self, id: int) -> Shipment:
        return await self.session.get(Shipment, id)

    # Add a new shipment
    async def add(self, shipment_create: ShipmentCreate) -> Shipment:
        new_shipment = Shipment(
            **shipment_create.model_dump(),
            status=ShipmentStatus.placed,
            estimated_delivery=datetime.now() + timedelta(days=3),
        )
        self.session.add(new_shipment)
        await self.session.commit()
        await self.session.refresh(new_shipment)

        return new_shipment

    # Update an existing shipment
    async def update(self, id: int, shipment_update: dict) -> Shipment:
        shipment = await self.get(id)
        shipment.sqlmodel_update(shipment_update)

        self.session.add(shipment)
        await self.session.commit()
        await self.session.refresh(shipment)

        return shipment

    # Delete a shipment
    async def delete(self, id: int) -> None:
        await self.session.delete(await self.get(id))
        await self.session.commit()

#---
# 1. await self.session.commit(): "Nút Gửi"
# Khi bạn thực hiện các thao tác như self.session.add(new_shipment) hoặc sửa đổi thuộc tính của một object, các thay đổi đó chưa hề được lưu vào cơ sở dữ liệu. Chúng chỉ đang nằm trong "bộ nhớ tạm" (identity map) của session.

# Tại sao cần commit()?

# Nó gửi lệnh INSERT hoặc UPDATE thật sự xuống Database.

# Nó yêu cầu Database chính thức xác nhận (transaction) các thay đổi này là vĩnh viễn.

# Nếu bạn không commit(), khi bạn tắt chương trình hoặc kết thúc request, mọi thay đổi của bạn sẽ bị "bay màu" (rollback).

# 2. await self.session.refresh(shipment): "Tải lại trang"
# Sau khi commit(), Database có thể đã làm thay đổi dữ liệu của bạn mà bạn không biết.

# Tại sao cần refresh()?

# Giá trị mặc định của DB: Giả sử bảng shipment của bạn có cột created_at tự động lấy thời gian hiện tại (server_default=func.now()). Khi bạn tạo mới, code Python của bạn không biết thời gian đó là bao nhiêu. refresh() sẽ yêu cầu Database gửi lại đối tượng đã được cập nhật đầy đủ (bao gồm các giá trị mặc định do DB sinh ra).

# Đồng bộ hóa: Sau khi commit, trạng thái của object trong Python đôi khi bị "expire" (quá hạn) để đảm bảo bạn không dùng dữ liệu cũ. refresh() sẽ đọc lại dữ liệu mới nhất từ bảng, giúp bạn chắc chắn rằng object shipment trong tay bạn lúc này là "bản chuẩn" đang nằm trong Database.