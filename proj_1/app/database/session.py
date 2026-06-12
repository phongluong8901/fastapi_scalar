from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

from app.config import settings

# Create a database engine to connect with database
engine = create_async_engine(
    # database type/dialect and file name
    url=settings.POSTGRES_URL,
    # Log sql queries
    echo=True,
)


async def create_db_tables():
    async with engine.begin() as connection:
        from app.database.models import Shipment  # noqa: F401
        await connection.run_sync(SQLModel.metadata.create_all)


async def get_session():
    async_session = sessionmaker(
        bind=engine, class_=AsyncSession, expire_on_commit=False,
    )

    async with async_session() as session:
        yield session

# #---
# 1. Nếu không dùng async (Đồng bộ - Blocking)
# Khi người dùng tạo đơn hàng, chương trình sẽ chạy như sau:

# Lưu đơn hàng vào DB: Mất 0.5 giây (chờ DB phản hồi).

# Gửi email xác nhận: Mất 2 giây (chờ máy chủ SMTP phản hồi).

# Trả kết quả cho người dùng: Tổng cộng mất 2.5 giây.

# Trong 2.5 giây đó, nếu có 100 người khác cùng gửi yêu cầu, server của bạn sẽ bị treo hoàn toàn vì mỗi request đều phải đợi 2.5 giây mới xong.

# --
# 2. Nếu dùng async (Bất đồng bộ - Non-blocking)
# Với async, code của bạn sẽ trông như thế này:

# Python


# @app.post("/orders")
# async def create_order(order: Order, db: AsyncSession = Depends(get_session)):
#     # 1. Lưu vào DB (await sẽ giúp giải phóng CPU)
#     await db.execute(...) 
    
#     # 2. Gửi email (await ở đây là chìa khóa)
#     await send_email_async(...)
    
#     return {"status": "success"}
# Luồng hoạt động lúc này:

# Gửi lệnh Lưu đơn vào DB: FastAPI gửi lệnh đi và "treo" tác vụ đó lại (không tốn CPU để ngồi đợi).

# Ngay lập tức: FastAPI quay sang phục vụ người dùng thứ 2, thứ 3...

# Khi DB phản hồi: Hệ thống tự quay lại hoàn tất việc lưu đơn.

# Gửi Email: Tương tự, nó không chờ SMTP trả về kết quả mà tiếp tục phục vụ người dùng tiếp theo.

# Kết quả là: Thời gian phản hồi của 1 request có thể vẫn là 2.5 giây, nhưng khả năng chịu tải (throughput) của server tăng lên gấp hàng trăm lần.


# #---
# # 1. Nhập các thư viện cần thiết
# from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
# from sqlalchemy.orm import sessionmaker
# from sqlmodel import SQLModel
# from app.config import settings

# # 2. Khởi tạo Engine (Bộ máy điều khiển kết nối)
# engine = create_async_engine(
#     url=settings.POSTGRES_URL, # Lấy chuỗi kết nối từ .env
#     echo=True,                 # In ra terminal mọi câu lệnh SQL mà SQLAlchemy chạy
# )

# Dòng này làm gì: Nó thiết lập một "cổng kết nối" giữa ứng dụng và PostgreSQL. Nó chưa kết nối ngay, mà chỉ chuẩn bị sẵn cấu hình để khi nào cần thì sử dụng.

# --
# Python


# # 3. Định nghĩa hàm tạo bảng
# async def create_db_tables():
#     async with engine.begin() as connection:
#         from app.database.models import Shipment
#         # Thực hiện tạo bảng
#         await connection.run_sync(SQLModel.metadata.create_all)
# async with engine.begin() as connection: Mở một giao dịch (transaction) với Database. Nếu mọi thứ thành công, nó sẽ lưu (commit); nếu lỗi, nó sẽ hủy (rollback).

# connection.run_sync: Đây là bước "cầu nối". Vì lệnh SQLModel.metadata.create_all (tự tạo bảng dựa trên code) là lệnh đồng bộ (sync), nhưng chúng ta đang ở trong môi trường async. 
# Lệnh này giúp chạy lệnh tạo bảng an toàn mà không làm treo chương trình.

# --
# Python


# # 4. Định nghĩa hàm lấy Session (Phiên làm việc)
# async def get_session():
#     async_session = sessionmaker(
#         bind=engine, class_=AsyncSession, expire_on_commit=False,
#     )
# sessionmaker: Đây là "nhà máy" sản xuất ra các Session. Mỗi khi bạn cần truy vấn Database, bạn sẽ dùng cái này để tạo ra một đối tượng AsyncSession.

# expire_on_commit=False: Một thiết lập quan trọng, ngăn chặn SQLAlchemy tự động xóa sạch dữ liệu trong model sau khi bạn thực hiện commit. 
# Điều này giúp bạn vẫn có thể đọc dữ liệu từ model sau khi đã lưu vào DB.

# Python

# --

#     async with async_session() as session:
#         yield session
# async with async_session() as session: Mở một phiên làm việc cụ thể.

# yield session: Đây là chìa khóa của FastAPI Dependency Injection.

# Khi một API của bạn cần database, nó sẽ "mượn" cái session này.

# Hàm get_session dừng lại ở yield để API sử dụng session đó làm việc.

# Sau khi API chạy xong (gửi kết quả về cho người dùng), code sẽ chạy tiếp phần sau yield,
# tự động đóng session lại để trả kết nối về cho Database (tránh bị tràn kết nối).

# --
# Tóm tắt luồng hoạt động:
# Khởi động: Ứng dụng tạo engine (kết nối).

# Startup (Lifespan): Gọi create_db_tables để đảm bảo Database đã có các bảng cần thiết.

# Khi có người dùng gọi API: * Hàm get_session được gọi.

# Một session được tạo ra qua yield.

# API thực hiện truy vấn (await session.exec(...)).

# session tự động đóng, giải phóng kết nối cho Database.