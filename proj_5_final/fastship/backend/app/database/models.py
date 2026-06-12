from datetime import datetime            # Dùng để xử lý ngày tháng
from enum import Enum                    # Dùng để định nghĩa các tập hợp giá trị cố định
from uuid import UUID, uuid4             # Dùng cho khóa chính định dạng UUID ngẫu nhiên

from pydantic import EmailStr            # Dùng để kiểm tra định dạng email hợp lệ
from sqlalchemy.dialects import postgresql # Cấu hình chuyên dụng cho Database PostgreSQL
from sqlalchemy.ext.asyncio import AsyncSession # Hỗ trợ truy vấn Database bất đồng bộ
from sqlmodel import Column, Field, Relationship, SQLModel, select # Thư viện chính để định nghĩa bảng

#Enum (Danh sách giá trị cố định)
class TagName(str, Enum):
    # Các nhãn cho đơn hàng (Ví dụ: "express", "fragile"...)
    # Hàm tag(): Truy vấn database để lấy đối tượng Tag từ tên của nó
    EXPRESS = "express" # Nhãn giao hàng hỏa tốc
    STANDARD = "standard"   # Nhãn giao hàng tiêu chuẩn
    FRAGILE = "fragile"
    HEAVY = "heavy"
    INTERNATIONAL = "international"
    DOMESTIC = "domestic"
    TEMPERATURE_CONTROLLED = "temperature_controlled"
    GIFT = "gift"
    RETURN = "return"
    DOCUMENTS = "documents"

    async def tag(self, session: AsyncSession) -> "Tag":    # Hàm lấy dữ liệu Tag từ DB
        return await session.scalar(select(Tag).where(Tag.name == self.value))  # Truy vấn lấy 1 Tag


class ShipmentStatus(str, Enum):
    # Các trạng thái của đơn hàng (placed, in_transit, ...)
    placed = "placed"                    # Đã đặt đơn
    in_transit = "in_transit"            # Đang vận chuyển
    out_for_delivery = "out_for_delivery"# Đang đi giao
    delivered = "delivered"              # Đã giao thành công
    cancelled = "cancelled"              # Đã hủy

class ShipmentTag(SQLModel, table=True): # Bảng nối giữa Đơn hàng và Nhãn
    __tablename__ = "shipment_tag"       # Tên bảng trong Database
    shipment_id: UUID = Field(foreign_key="shipment.id", primary_key=True) # Khóa ngoại trỏ tới Shipment
    tag_id: UUID = Field(foreign_key="tag.id", primary_key=True)           # Khóa ngoại trỏ tới Tag


class Tag(SQLModel, table=True):
    __tablename__ = "tag"
    id: UUID = Field(sa_column=Column(postgresql.UUID, default=uuid4, primary_key=True)) # ID định dạng UUID
    name: TagName                        # Tên nhãn (dùng Enum ở trên)
    instruction: str                     # Hướng dẫn đi kèm với nhãn
    shipments: list["Shipment"] = Relationship( # Quan hệ: 1 nhãn có nhiều đơn hàng
        back_populates="tags",           # Trỏ ngược lại thuộc tính tags ở bảng Shipment
        link_model=ShipmentTag,          # Sử dụng bảng ShipmentTag để kết nối
        sa_relationship_kwargs={"lazy": "immediate"}, # Luôn tải danh sách này ngay lập tức
    )

#Bảng Shipment (Đơn hàng) & ShipmentEvent (Lịch sử)
class Shipment(SQLModel, table=True):
    __tablename__ = "shipment"
    id: UUID = Field(sa_column=Column(postgresql.UUID, default=uuid4, primary_key=True)) # ID đơn hàng
    created_at: datetime = Field(sa_column=Column(postgresql.TIMESTAMP, default=datetime.now)) # Ngày tạo
    client_contact_email: EmailStr       # Email khách hàng
    client_contact_phone: str | None     # Số điện thoại (có thể để trống)
    content: str                         # Nội dung gói hàng
    weight: float = Field(le=25)         # Trọng lượng (lớn nhất là 25)
    destination: int                     # Mã bưu chính đích đến
    estimated_delivery: datetime | None  # Ngày giao dự kiến
    timeline: list["ShipmentEvent"] = Relationship( # Quan hệ: 1 đơn có nhiều sự kiện
        back_populates="shipment",
        sa_relationship_kwargs={"lazy": "selectin"}, # Tải dữ liệu sự kiện ngay khi gọi đơn hàng
    )
    seller_id: UUID = Field(foreign_key="seller.id") # Khóa ngoại Seller
    seller: "Seller" = Relationship(back_populates="shipments", sa_relationship_kwargs={"lazy": "selectin"})
    delivery_partner_id: UUID = Field(foreign_key="delivery_partner.id") # Khóa ngoại đối tác
    delivery_partner: "DeliveryPartner" = Relationship(back_populates="shipments", sa_relationship_kwargs={"lazy": "selectin"})
    review: "Review" = Relationship(back_populates="shipment", sa_relationship_kwargs={"lazy": "selectin"})
    tags: list[Tag] = Relationship(      # Danh sách nhãn của đơn hàng
        back_populates="shipments", link_model=ShipmentTag, sa_relationship_kwargs={"lazy": "immediate"}
    )
    @property                            # Thuộc tính ảo không lưu DB
    def status(self):                    # Trả về trạng thái mới nhất từ timeline
        return self.timeline[-1].status if len(self.timeline) > 0 else None

#ShipmentEvent: Lưu lại lịch sử thay đổi trạng thái của đơn hàng (location, status, description).
class ShipmentEvent(SQLModel, table=True):
    __tablename__ = "shipment_event"

    id: UUID = Field(
        sa_column=Column(
            postgresql.UUID,
            default=uuid4,
            primary_key=True,
        )
    )
    created_at: datetime = Field(
        sa_column=Column(
            postgresql.TIMESTAMP,
            default=datetime.now,
        )
    )

    location: int
    status: ShipmentStatus
    description: str | None = Field(default=None)

    shipment_id: UUID = Field(foreign_key="shipment.id")
    shipment: Shipment = Relationship(
        back_populates="timeline",  #link voi timeline cua Shipment table
        sa_relationship_kwargs={"lazy": "selectin"},
    )

#User: Model cơ sở (không lưu DB) chứa name, email, password_hash.
class User(SQLModel):
    name: str

    email: EmailStr
    email_verified: bool = Field(default=False)
    password_hash: str = Field(exclude=True)

#Seller: Kế thừa User, thêm địa chỉ (address) và mã vùng (zip_code).
class Seller(User, table=True):
    __tablename__ = "seller"

    id: UUID = Field(
        sa_column=Column(
            postgresql.UUID,
            default=uuid4,
            primary_key=True,
        )
    )
    created_at: datetime = Field(
        sa_column=Column(
            postgresql.TIMESTAMP,
            default=datetime.now,
        )
    )

    address: str
    zip_code: int

    shipments: list[Shipment] = Relationship(
        back_populates="seller",    #lay nhieu seller o Shipment
        sa_relationship_kwargs={"lazy": "selectin"},
    )

# ServicableLocation: Bảng trung gian xác định đối tác nào giao được cho khu vực nào.
class ServicableLocation(SQLModel, table=True):
    __tablename__ = "servicable_location"

    partner_id: UUID = Field(   #tao ket noi forein
        foreign_key="delivery_partner.id",
        primary_key=True,
    )
    location_id: int = Field(   #tao ket noi forein
        foreign_key="location.zip_code",
        primary_key=True,
    )

# DeliveryPartner: Kế thừa User, thêm max_handling_capacity và các phương thức @property để tính toán số đơn hàng đang xử lý.
class DeliveryPartner(User, table=True):
    __tablename__ = "delivery_partner"

    id: UUID = Field(
        sa_column=Column(
            postgresql.UUID,
            default=uuid4,
            primary_key=True,
        )
    )
    created_at: datetime = Field(
        sa_column=Column(
            postgresql.TIMESTAMP,
            default=datetime.now,
        )
    )

    # serviceable_zip_codes: list[int] = Field(
    #     sa_column=Column(ARRAY(INTEGER)),
    # )
    servicable_locations: list["Location"] = Relationship(  #nhieu delivery_partners
        back_populates="delivery_partners",
        link_model=ServicableLocation,
        sa_relationship_kwargs={"lazy": "immediate"}, # Ngay khi đối tượng chính được tải, hãy tải ngay lập tức toàn bộ dữ liệu quan hệ của nó
    )
    max_handling_capacity: int

    shipments: list[Shipment] = Relationship(
        back_populates="delivery_partner",
        sa_relationship_kwargs={"lazy": "selectin"},
    )

    # active_shipments (Lấy danh sách đơn đang thực hiện)
    @property
    def active_shipments(self):
        return [
            shipment
            for shipment in self.shipments
            if shipment.status != ShipmentStatus.delivered
            or shipment.status != ShipmentStatus.cancelled
            #Nó lấy những đơn có trạng thái khác delivered (đã giao) HOẶC khác cancelled (đã hủy).
        ]
    #current_handling_capacity (Tính sức chứa còn lại)
    @property
    def current_handling_capacity(self):
        return self.max_handling_capacity - len(self.active_shipments)


class Location(SQLModel, table=True):
    __tablename__ = "location"

    zip_code: int = Field(primary_key=True)
    
    # Additional metadata fields
    # estimated_delivery_days: int = Field(default=3)
    # surcharge: float = Field(default=0.0)
    # active: bool = Field(default=True)

    delivery_partners: list[DeliveryPartner] = Relationship(
        back_populates="servicable_locations",
        link_model=ServicableLocation,
        sa_relationship_kwargs={"lazy": "immediate"},
    )


class Review(SQLModel, table=True):
    __tablename__ = "review"

    id: UUID = Field(
        sa_column=Column(
            postgresql.UUID,
            default=uuid4,
            primary_key=True,
        )
    )
    created_at: datetime = Field(
        sa_column=Column(
            postgresql.TIMESTAMP,
            default=datetime.now,
        )
    )

    rating: int = Field(ge=1, le=5)
    comment: str | None = Field(default=None)

    shipment_id: UUID = Field(foreign_key="shipment.id")
    shipment: Shipment = Relationship(
        back_populates="review",
        sa_relationship_kwargs={"lazy": "selectin"},
    )

#---
# lazy="select" (Mặc định)	Truy vấn khi cần	Chỉ khi bạn gọi tag.shipments trong code, nó mới phát lệnh truy vấn DB lần 2.
# lazy="immediate"	Truy vấn ngay lập tức	Ngay khi bạn lấy Tag, nó lấy luôn shipments.
# lazy="selectin"	Tối ưu bằng IN	Lấy danh sách chính, sau đó dùng một câu lệnh duy nhất (ví dụ: SELECT ... WHERE tag_id IN (...)) để lấy tất cả dữ liệu liên quan.

#---
# 1. Tầng Dữ liệu & Ràng buộc (Database Level)
# Field (Column): Là các trường dữ liệu vật lý (như zip_code, max_handling_capacity). Đây là những cột thực sự tồn tại trong bảng Database, dùng để lưu trữ giá trị cụ thể.

# ForeignKey (Khóa ngoại): Là "cái móng" kết nối các bảng. Nó thực thi sự toàn vẹn dữ liệu (đảm bảo dữ liệu các bảng khớp nhau). Nếu không có nó, Database sẽ mất tính logic.

# 2. Tầng Truy vấn & Kết nối (ORM Level)
# Relationship (Đường ống): Là một "đường dẫn ảo" giúp Python/SQLModel tự động viết câu lệnh JOIN hoặc truy vấn con để lấy dữ liệu từ bảng khác. Nó không tồn tại trong Database.

# back_populates: Cơ chế "bắt tay" hai chiều, giúp tự động đồng bộ dữ liệu giữa hai class (ví dụ: thêm shipper vào vùng thì vùng đó cũng tự nhận shipper).

# link_model: Chỉ dùng cho quan hệ "Nhiều-Nhiều", định danh bảng trung gian để làm cầu nối.

# lazy="immediate/selectin": Cấu hình chiến thuật tải dữ liệu (tải ngay lập tức hoặc tải theo đợt) để tối ưu hiệu năng.

# 3. Tầng Nghiệp vụ (Logic Level)
# @property (Bộ lọc thông minh): Là các hàm tính toán dựa trên dữ liệu đã có sẵn trong đối tượng. Chúng không lưu trữ vào Database mà chỉ tính toán "tại chỗ" khi bạn gọi. Rất hữu ích để lọc danh sách hoặc tính toán các con số nghiệp vụ (ví dụ: current_handling_capacity).