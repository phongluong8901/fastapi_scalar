from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException, status
from scalar_fastapi import get_scalar_api_reference

# Nhập các Models, Schemas và Dependency từ các file đã giải thích trước đó
from app.database.models import Shipment, ShipmentStatus
from app.database.session import SessionDep, create_db_tables
from .schemas import ShipmentCreate, ShipmentRead, ShipmentUpdate

# Lifespan: Quản lý vòng đời ứng dụng (Chạy code khi khởi động/tắt app)
@asynccontextmanager
async def lifespan_handler(app: FastAPI):
    create_db_tables() # Tự động tạo bảng trong DB khi app vừa khởi chạy
    yield # App bắt đầu chạy
    # Code sau yield sẽ chạy khi app tắt (nếu cần dọn dẹp)

# Khởi tạo ứng dụng FastAPI với lifespan đã định nghĩa
app = FastAPI(lifespan=lifespan_handler)

### READ: Lấy thông tin đơn hàng theo ID
@app.get("/shipment", response_model=ShipmentRead)
def get_shipment(id: int, session: SessionDep):
    # Dùng session để truy vấn bảng Shipment theo id
    shipment = session.get(Shipment, id)
    # Nếu không tìm thấy, trả về lỗi 404
    if shipment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Given id doesn't exist!")
    return shipment

### CREATE: Tạo đơn hàng mới
@app.post("/shipment", response_model=None)
def submit_shipment(shipment: ShipmentCreate, session: SessionDep) -> dict[str, int]:
    # Tạo object Shipment từ dữ liệu nhận vào (model_dump) 
    # cộng thêm giá trị mặc định (status='placed', thời gian giao hàng)
    new_shipment = Shipment(
        **shipment.model_dump(),
        status=ShipmentStatus.placed,
        estimated_delivery=datetime.now() + timedelta(days=3),
    )
    session.add(new_shipment) # Thêm vào session
    session.commit()          # Lưu vào DB
    session.refresh(new_shipment) # Cập nhật lại đối tượng để có ID mới được tạo
    return {"id": new_shipment.id}

### PATCH: Cập nhật thông tin đơn hàng
@app.patch("/shipment", response_model=ShipmentRead)
def update_shipment(id: int, shipment_update: ShipmentUpdate, session: SessionDep):
    # Lấy dữ liệu update, loại bỏ những trường rỗng (None)
    update = shipment_update.model_dump(exclude_none=True)
    if not update:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No data provided to update")

    shipment = session.get(Shipment, id)
    if shipment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Given id doesn't exist!")
    # Hàm sqlmodel_update tự động cập nhật các giá trị mới vào object
    shipment.sqlmodel_update(update)
    session.add(shipment)
    session.commit()
    session.refresh(shipment)
    return shipment

### DELETE: Xóa đơn hàng
@app.delete("/shipment")
def delete_shipment(id: int, session: SessionDep) -> dict[str, str]:
    session.delete(session.get(Shipment, id))
    session.commit()
    return {"detail": f"Shipment with id #{id} is deleted!"}

### DOCS: Tích hợp Scalar để xem API tài liệu
@app.get("/scalar", include_in_schema=False)
def get_scalar_docs():
    return get_scalar_api_reference(openapi_url=app.openapi_url, title="Scalar API")


# #--- giai thich get
# 1. Trạm tiếp nhận (Dependency Injection)
# def get_shipment(id: int, session: SessionDep):

# FastAPI làm gì: Trước khi code trong hàm chạy, FastAPI nhìn vào tham số id và session.

# Nó sẽ tự động trích xuất id từ đường dẫn (query parameter) và "bơm" một session (kết nối database) đã được mở sẵn từ get_session() (trong file session.py) vào hàm này. Nếu id không phải là số nguyên, FastAPI sẽ tự động trả về lỗi 422 ngay lập tức mà không cần bạn viết thêm dòng code nào.

# 2. Trạm truy vấn (Database Lookup)
# shipment = session.get(Shipment, id)

# Workflow: Code của bạn yêu cầu session: "Hãy tìm trong bảng Shipment xem có dòng nào mang id này không?".

# Kết quả:

# Nếu có: SQLModel trả về một đối tượng (object) chứa đầy đủ thông tin (content, weight, status, v.v.).

# Nếu không: Kết quả trả về là None.

# 3. Trạm kiểm soát logic (Validation/Error Handling)
# if shipment is None:

# Workflow: Bạn thực hiện một phép kiểm tra đơn giản.

# Nếu shipment là None: Nghĩa là ID người dùng nhập không tồn tại.

# raise HTTPException(...): Bạn "ném" ra một lỗi (Exception). FastAPI bắt lấy lỗi này, dừng toàn bộ việc thực thi hàm và trả về cho người dùng phản hồi HTTP với mã 404 Not Found kèm theo dòng tin nhắn "Given id doesn't exist!".

# Nếu shipment không phải là None: Code bỏ qua khối if này và chạy tiếp xuống dòng dưới.

# 4. Trạm phản hồi (Response Serialization)
# return shipment

# Workflow: Bạn trả về đối tượng Shipment (kiểu SQLModel).

# FastAPI làm gì: FastAPI nhìn vào response_model=ShipmentRead mà bạn đã khai báo ở dòng đầu tiên.

# Nó sẽ lọc đối tượng shipment này: Nó chỉ lấy ra những trường nào có trong ShipmentRead (content, weight, destination, status, estimated_delivery).

# Nó chuyển đổi (serialize) đối tượng này thành định dạng JSON.

# Cuối cùng, nó gửi gói tin JSON đó về cho người dùng với mã 200 OK.

# #--
# 1. Request (RQ)
# Người dùng (Client) muốn lấy thông tin của đơn hàng có ID là 1. Họ sẽ gửi một HTTP GET request tới server:

# Method: GET
# URL: http://localhost:8000/shipment?id=1

# Giải thích:

# GET: Phương thức lấy dữ liệu.

# /shipment: Endpoint bạn đã định nghĩa.

# ?id=1: Tham số query truyền vào để xác định bạn muốn lấy đơn hàng nào.

# 2. Response (RP)
# Sau khi FastAPI thực hiện quy trình "kiểm soát" (đã giải thích ở trên), nó sẽ trả về kết quả dưới dạng JSON:

# Status Code: 200 OK
# Body:

# JSON


# {
#   "content": "Laptop Dell XPS 15",
#   "weight": 2.5,
#   "destination": 101,
#   "status": "placed",
#   "estimated_delivery": "2026-06-13T14:30:00"
# }

# #--
# 1. id: int (Tác dụng Validation - Kiểm soát dữ liệu đầu vào)
# Khi bạn khai báo id: int, FastAPI sẽ thực hiện kiểm tra kiểu dữ liệu (Type Hinting) ngay khi request đến:

# Tự động ép kiểu: Nếu người dùng gửi id=1 (dưới dạng chuỗi trong URL), FastAPI sẽ tự động chuyển nó thành số nguyên (int) trước khi đưa vào hàm.

# Tự động bắt lỗi: Nếu người dùng gửi id=abc, FastAPI sẽ tự động chặn lại và trả về lỗi 422 Unprocessable Entity với thông báo lỗi cụ thể (ví dụ: "field is not a valid integer"). Bạn không cần viết một dòng if nào để kiểm tra xem id có phải là số hay không.

# #--
# Để trả lời ngắn gọn: Kết nối đến Database (File SQLite) đã được mở ngay khi hàm get_shipment bắt đầu chạy, nhưng việc tìm kiếm dữ liệu thì chỉ xảy ra ở dòng session.get.

# Dưới đây là chi tiết thứ tự thực hiện:

# 1. Tại thời điểm tham số session: SessionDep được truyền vào:
# Ngay khi dòng def get_shipment(...) được kích hoạt, FastAPI sẽ gọi hàm get_session() mà bạn đã định nghĩa trong session.py:

# Code thực thi: with Session(bind=engine) as session:

# Kết nối: Lúc này, Session chính thức thiết lập kết nối tới file sqlite.db.

# Trạng thái: Bạn đã có một "phiên làm việc" (session) sẵn sàng trong tay.

# 2. Tại dòng shipment = session.get(Shipment, id):
# Đây mới là lúc SQL được thực thi.

# Hành động: Khi bạn gọi .get(), SQLModel sẽ chuyển đổi lệnh này thành câu truy vấn SQL (kiểu như SELECT * FROM shipment WHERE id = 1).

# Tìm kiếm: Câu lệnh SQL này được gửi qua "đường ống" (kết nối) đã mở ở bước 1 để vào file sqlite.db.

# Kết quả: Database trả về dữ liệu, SQLModel biến nó thành đối tượng Shipment và gán vào biến shipment.