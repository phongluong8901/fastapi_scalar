from datetime import datetime, timedelta
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.shipment import ShipmentCreate
from app.database.models import Seller, Shipment, ShipmentStatus

from .base import BaseService
from .delivery_partner import DeliveryPartnerService


class ShipmentService(BaseService):
    def __init__(
        self,
        session: AsyncSession,
        partner_service: DeliveryPartnerService,    #Đây là kỹ thuật Dependency Injection. Bạn "tiêm" kết nối database và dịch vụ đối tác vào.
    ):
        super().__init__(Shipment, session) #Ra lệnh cho lớp cha (BaseService) cấu hình để làm việc với bảng Shipment và sử dụng session này để giao tiếp với Postgres.
        self.partner_service = partner_service  #Lưu lại "chuyên gia" logistics để sau này gọi hàm gán đơn hàng.

    # Get a shipment by id
    async def get(self, id: UUID) -> Shipment | None:
        return await self._get(id)

    # Add a new shipment
    async def add(self, shipment_create: ShipmentCreate, seller: Seller) -> Shipment:
        new_shipment = Shipment(
            **shipment_create.model_dump(),
            status=ShipmentStatus.placed,
            estimated_delivery=datetime.now() + timedelta(days=3),
            seller_id=seller.id,
        )
        # Assign delivery partner to the shipment
        partner = await self.partner_service.assign_shipment(
            new_shipment,
        )
        # Add the delivery partner foreign key
        new_shipment.delivery_partner_id = partner.id

        return await self._add(new_shipment)

    # Update an existing shipment
    async def update(self, shipment: Shipment) -> Shipment:
        return await self._update(shipment)

    # Delete a shipment
    async def delete(self, id: int) -> None:
        await self._delete(await self.get(id))


#--- 
# 1. Ý nghĩa của dòng này
# super(): Truy cập vào lớp cha, trong trường hợp này là BaseService.

# __init__: Hàm khởi tạo của lớp cha.

# (Shipment, session): Bạn đang truyền 2 thông tin quan trọng lên cho BaseService:

# Shipment: Đây là Model dữ liệu (SQLModel) mà dịch vụ này sẽ quản lý.

# session: Đây là kết nối (session) với database hiện tại.