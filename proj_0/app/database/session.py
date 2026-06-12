from typing import Annotated
from fastapi import Depends
from sqlalchemy import create_engine
from sqlmodel import Session, SQLModel

# Khởi tạo "động cơ" (engine) để kết nối với cơ sở dữ liệu
engine = create_engine(
    # Đường dẫn file SQLite (sẽ tạo ra file sqlite.db trong thư mục dự án)
    url="sqlite:///sqlite.db",
    # echo=True: Tự động in ra các câu lệnh SQL ra console (giúp bạn debug/học SQL)
    echo=True,
    # Riêng với SQLite, cần dòng này để cho phép các thread khác nhau truy cập vào cùng 1 file
    connect_args={"check_same_thread": False},
)

# Hàm khởi tạo các bảng trong Database
def create_db_tables():
    # Import model Shipment để SQLModel biết cần tạo bảng nào
    from .models import Shipment  # noqa: F401 (ngăn trình kiểm tra code báo lỗi import thừa)
    # Lệnh thực thi tạo tất cả bảng dựa trên các Class đã kế thừa SQLModel
    SQLModel.metadata.create_all(bind=engine)

# Hàm cung cấp phiên làm việc (Session) với Database
def get_session():
    # 'with' đảm bảo session luôn được đóng sau khi request xử lý xong
    with Session(bind=engine) as session:
        yield session # Trả về session để các API sử dụng

# Định nghĩa kiểu dữ liệu rút gọn (Dependency Injection)
# Mỗi khi dùng SessionDep trong hàm API, FastAPI sẽ tự gọi get_session()
SessionDep = Annotated[Session, Depends(get_session)]