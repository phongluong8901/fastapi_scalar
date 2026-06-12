from fastapi import APIRouter, HTTPException, status

from ..dependencies import SellerDep, ShipmentServiceDep
from ..schemas.shipment import ShipmentCreate, ShipmentRead, ShipmentUpdate


router = APIRouter(prefix="/shipment", tags=["Shipment"])


### Read a shipment by id
@router.get("/", response_model=ShipmentRead)
async def get_shipment(id: int, service: ShipmentServiceDep):
    # Check for shipment with given id
    shipment = await service.get(id)

    if shipment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Given id doesn't exist!",
        )

    return shipment


### Create a new shipment with content and weight
@router.post("/", response_model=ShipmentRead)
async def submit_shipment(
    seller: SellerDep,
    shipment: ShipmentCreate,
    service: ShipmentServiceDep,
):
    return await service.add(shipment)


### Update fields of a shipment
@router.patch("/", response_model=ShipmentRead)
async def update_shipment(
    id: int,
    shipment_update: ShipmentUpdate,
    service: ShipmentServiceDep,
):
    # Update data with given fields
    update = shipment_update.model_dump(exclude_none=True)

    if not update:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No data provided to update",
        )

    return await service.update(id, update)


### Delete a shipment by id
@router.delete("/")
async def delete_shipment(id: int, service: ShipmentServiceDep) -> dict[str, str]:
    # Remove from database
    await service.delete(id)

    return {"detail": f"Shipment with id #{id} is deleted!"}

#--- seller: SellerDep
# Luồng xử lý (Execution Flow)
# Khi một người dùng gửi yêu cầu tạo shipment (kèm theo token trong header), FastAPI sẽ thực hiện các bước sau theo thứ tự "vắt sữa" phụ thuộc:

# Xác thực Token:

# FastAPI thấy submit_shipment cần seller: SellerDep.

# SellerDep gọi get_current_seller.

# get_current_seller cần token_data từ get_access_token.

# get_access_token tự động lấy token từ Header (oauth2_scheme) và gọi decode_access_token. Nếu token sai hoặc hết hạn, nó quăng lỗi 401 ngay lập tức.

# Lấy đối tượng Seller:

# Sau khi có token_data, get_current_seller dùng token_data["user"]["id"] để truy vấn DB thông qua session.

# Đối tượng seller này được trả về và "bơm" vào tham số seller trong hàm của bạn.

# Khởi tạo Service:

# FastAPI thấy service: ShipmentServiceDep.

# Nó chạy get_shipment_service, hàm này sử dụng SessionDep (được cung cấp bởi get_session) để tạo ra một instance ShipmentService(session).

# Thực thi nghiệp vụ:

# Sau khi tất cả các phụ thuộc trên đã xong xuôi và không lỗi, hàm submit_shipment mới thực sự được gọi.

# Lúc này, bạn chỉ cần dùng service.add(shipment) là xong.
