from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.database.redis import add_jti_to_blacklist

from ..dependencies import SellerServiceDep, get_seller_access_token
from ..schemas.seller import SellerCreate, SellerRead

router = APIRouter(prefix="/seller", tags=["Seller"])


### Register a new seller
@router.post("/signup", response_model=SellerRead)
async def register_seller(seller: SellerCreate, service: SellerServiceDep):
    return await service.add(seller)


### Login a seller
@router.post("/token")
async def login_seller(
    request_form: Annotated[OAuth2PasswordRequestForm, Depends()],
    service: SellerServiceDep,
):
    token = await service.token(request_form.username, request_form.password)
    return {
        "access_token": token,
        "type": "jwt",
    }


### Logout a seller
@router.get("/logout")
async def logout_seller(
    token_data: Annotated[dict, Depends(get_seller_access_token)],
):
    await add_jti_to_blacklist(token_data["jti"])
    return {
        "detail": "Successfully logged out"
    }

#---
# Khi một người dùng gọi GET /seller/logout:

# Depends(get_seller_access_token): FastAPI chạy trước để kiểm tra token.

# oauth2_scheme_seller: Lấy token từ header Authorization: Bearer <token>.

# _get_access_token:

# Gọi decode_access_token để giải mã.

# Kiểm tra is_jti_blacklisted: Nếu token đã bị đưa vào danh sách đen trong Redis, nó sẽ chặn ngay lập tức (trả về lỗi 401).

# Nếu hợp lệ, nó trả về thông tin data (một dict chứa jti).

# logout_seller: Cuối cùng, hàm này được chạy với token_data hợp lệ, gọi add_jti_to_blacklist để lưu jti vào Redis. Từ giờ trở đi, token này coi như "chết".