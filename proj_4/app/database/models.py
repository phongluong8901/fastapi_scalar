from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4

from pydantic import EmailStr
from sqlalchemy.dialects import postgresql
from sqlalchemy import ARRAY, INTEGER
from sqlmodel import Column, Field, Relationship, SQLModel


class ShipmentStatus(str, Enum):          # Định nghĩa trạng thái đơn hàng (kiểu chuỗi và Enum)
    placed = "placed"                     # Trạng thái: đã đặt hàng
    in_transit = "in_transit"             # Trạng thái: đang vận chuyển
    out_for_delivery = "out_for_delivery" # Trạng thái: đang đi giao
    delivered = "delivered"               # Trạng thái: đã giao xong

# Lớp Shipment (Vận đơn)
class Shipment(SQLModel, table=True):     # Khai báo bảng Shipment trong Database
    __tablename__ = "shipment"            # Tên bảng thực tế trong DB là "shipment"

    id: UUID = Field(                     # Trường định danh duy nhất (Primary Key)
        sa_column=Column(                 # Dùng cấu hình cột của SQLAlchemy
            postgresql.UUID,              # Kiểu dữ liệu UUID của Postgres
            default=uuid4,                # Tự động tạo ID ngẫu nhiên khi tạo đơn mới
            primary_key=True,             # Đặt làm khóa chính
        )
    )
    created_at: datetime = Field(         # Trường lưu thời gian tạo đơn
        sa_column=Column(
            postgresql.TIMESTAMP,         # Kiểu TIMESTAMP của Postgres
            default=datetime.now,         # Mặc định lấy giờ hệ thống hiện tại
        )
    )

    content: str                          # Nội dung hàng hóa (kiểu chuỗi)
    weight: float = Field(le=25)          # Trọng lượng (số thực), ràng buộc <= 25kg
    destination: int                      # Mã bưu điện nơi đến
    status: ShipmentStatus                # Trạng thái đơn (dựa trên Enum ở trên)
    estimated_delivery: datetime          # Thời gian dự kiến giao hàng

    seller_id: UUID = Field(foreign_key="seller.id") # Khóa ngoại liên kết tới bảng Seller
    seller: "Seller" = Relationship(      # Định nghĩa quan hệ với Seller 1-1
        back_populates="shipments",       # Ánh xạ ngược lại danh sách đơn của Seller
        sa_relationship_kwargs={"lazy": "selectin"}, # Tối ưu tải dữ liệu liên quan ngay lập tức
    )

    delivery_partner_id: UUID = Field(foreign_key="delivery_partner.id") # Khóa ngoại tới Shipper
    delivery_partner: "DeliveryPartner" = Relationship( # Quan hệ với DeliveryPartner 1-1
        back_populates="shipments",       # Ánh xạ ngược lại đơn của Partner
        sa_relationship_kwargs={"lazy": "selectin"},
    )

# --- LỚP USER (Lớp cha chứa thông tin chung) ---
class User(SQLModel):                     # Lớp cha chung cho Seller và Partner
    name: str                             # Tên người dùng
    email: EmailStr                       # Kiểm tra email hợp lệ
    password_hash: str = Field(exclude=True) # Mật khẩu mã hóa, không hiển thị khi trả về JSON

# --- LỚP USER (Lớp cha chứa thông tin chung) ---
class Seller(User, table=True): # Bảng Seller kế thừa từ User
    __tablename__ = "seller"    # Tên bảng trong DB

    id: UUID = Field(
        sa_column=Column(
            postgresql.UUID,    # Khóa chính UUID (đã giải thích ở phần trước)
            default=uuid4,  
            primary_key=True,   # Khóa chính UUID
        )
    )
    created_at: datetime = Field(   # Thời gian tạo Seller
        sa_column=Column(
            postgresql.TIMESTAMP,
            default=datetime.now,
        )
    )

    shipments: list[Shipment] = Relationship(   # Định nghĩa quan hệ 1-nhiều với Shipment
        back_populates="seller",
        sa_relationship_kwargs={"lazy": "selectin"},    # 'selectin' giúp tải danh sách đơn hàng ngay lập tức khi query Seller
    )

# --- LỚP DELIVERY PARTNER (Đối tác vận chuyển - Kế thừa từ User) ---
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

    # Lưu mảng các mã bưu điện (Zip Code) mà đối tác này hỗ trợ giao hàng
    serviceable_zip_codes: list[int] = Field(
        sa_column=Column(ARRAY(INTEGER)),   #serviceable_zip_codes: [1000, 2000, 3000]
    )
    # Khả năng tối đa đối tác có thể nhận đơn hàng
    max_handling_capacity: int

    shipments: list[Shipment] = Relationship(   # Quan hệ 1-nhiều với Shipment
        back_populates="delivery_partner",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
    
    # Hàm tính toán: Lọc ra các đơn hàng chưa giao (trạng thái khác 'delivered')
    @property
    def active_shipments(self):
        return [
            shipment
            for shipment in self.shipments
            if shipment.status != ShipmentStatus.delivered
        ]
    
    # Hàm tính toán: Lấy khả năng nhận đơn tối đa trừ đi số đơn đang làm
    @property
    def current_handling_capacity(self):
        return self.max_handling_capacity - len(self.active_shipments)
    
#---
# 1. Thư viện Python chuẩn (Standard Library)
# from datetime import datetime: Dùng để xử lý ngày tháng (Ví dụ: lưu thời gian tạo vận đơn, thời gian dự kiến giao hàng).

# from enum import Enum: Dùng để tạo ra các tập hợp giá trị cố định (Ví dụ: ShipmentStatus với các trạng thái như "đã đặt", "đang giao", "đã giao"). Nó giúp code an toàn hơn vì bạn không bị gõ nhầm trạng thái.

# from uuid import UUID, uuid4:

# UUID: Kiểu dữ liệu định danh duy nhất toàn cầu (thay thế cho ID số 1, 2, 3...).

# uuid4: Hàm để tạo ra một ID ngẫu nhiên, đảm bảo không bao giờ bị trùng lặp.

# 2. Thư viện Pydantic
# from pydantic import EmailStr: Đây là một loại kiểu dữ liệu đặc biệt của Pydantic để tự động kiểm tra định dạng email (Ví dụ: nó sẽ báo lỗi ngay nếu người dùng nhập email không có ký tự @ hoặc sai cấu trúc).

# 3. Thư viện SQLAlchemy (Dialects & Types)
# Đây là thư viện cấp thấp giúp bạn làm việc trực tiếp với Database (PostgreSQL):

# from sqlalchemy.dialects import postgresql: Cho phép bạn sử dụng các kiểu dữ liệu đặc trưng của PostgreSQL (như UUID, TIMESTAMP).

# from sqlalchemy import ARRAY, INTEGER: Cho phép bạn định nghĩa các cột có kiểu dữ liệu là mảng (ARRAY) hoặc số nguyên (INTEGER) trực tiếp trong Database.

# 4. Thư viện SQLModel
# Đây là thư viện kết hợp sức mạnh của Pydantic (để kiểm tra dữ liệu) và SQLAlchemy (để giao tiếp với database):

# from sqlmodel import Column, Field, Relationship, SQLModel:

# SQLModel: Class nền tảng để định nghĩa các bảng dữ liệu (Models).

# Field: Dùng để cấu hình chi tiết cho các cột (như khóa chính, khóa ngoại, giới hạn giá trị).

# Column: Dùng khi bạn muốn định nghĩa sâu hơn về kiểu dữ liệu database (ví dụ: dùng kiểu mảng).

# Relationship: Dùng để thiết lập liên kết giữa các bảng (Ví dụ: một Seller có nhiều Shipment).

#--- @property
# 1. Tác động về logic (Business Logic)
# Nó định nghĩa lại khái niệm "đơn hàng đang xử lý" của Shipper. Thay vì mỗi lần cần biết Shipper đang bận hay rảnh, bạn lại phải viết một câu lệnh SELECT phức tạp để đếm đơn, thì giờ đây bạn chỉ cần gọi partner.active_shipments.

# Trạng thái nào được coi là đang hoạt động? Bất cứ đơn nào có trạng thái khác delivered (tức là placed, in_transit, hoặc out_for_delivery).

# Lợi ích: Code của bạn cực kỳ sạch. Bạn không phải lọc thủ công ở mọi nơi.

# 2. Tác động về hiệu suất (Performance)
# Tính toán trong bộ nhớ (In-memory calculation): Hàm này không gửi bất kỳ câu lệnh SQL nào xuống Database. Nó chỉ duyệt qua danh sách self.shipments mà bạn đã tải về từ trước (nhờ vào thuộc tính lazy="selectin" mà bạn đã cấu hình).

# Tiết kiệm tài nguyên: Vì nó chỉ hoạt động trên dữ liệu đã được nạp vào biến self.shipments của đối tượng, nó cực nhanh và không gây áp lực lên Database.
# --

# 1. Giải thích logic
# self.max_handling_capacity: Đây là con số cố định bạn lưu trong Database (tổng năng lực tối đa của Shipper).

# len(self.active_shipments): Đây là số lượng đơn hàng mà Shipper đó đang "ôm" (đang giao, chưa giao xong). Số này thay đổi liên tục.

# Tác động: Hàm này lấy Tổng năng lực trừ đi Số đơn đang giữ để ra được Số đơn còn có thể nhận thêm.

# 2. Tại sao nó quan trọng?
# Tính tức thời: Ngay khi một đơn hàng chuyển sang trạng thái delivered, hàm active_shipments (mà bạn đã định nghĩa trước đó) sẽ tự động giảm đi 1 đơn, và kết quả của current_handling_capacity sẽ tăng lên ngay lập tức mà bạn không cần lưu lại vào Database.

# Tránh lỗi dư thừa dữ liệu: Bạn không cần phải lưu một cột remaining_capacity vào Database. Vì nếu lưu vào Database, bạn sẽ phải cập nhật nó liên tục mỗi khi trạng thái đơn hàng thay đổi, điều này rất dễ gây ra lỗi sai lệch dữ liệu (ví dụ: quên cập nhật khi đơn hàng bị hủy).
