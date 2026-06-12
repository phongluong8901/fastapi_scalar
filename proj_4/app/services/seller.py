from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.seller import SellerCreate
from app.database.models import Seller

from .user import UserService


class SellerService(UserService):
    def __init__(self, session: AsyncSession):
        super().__init__(Seller, session)

    async def add(self, seller_create: SellerCreate) -> Seller:
        return await self._add_user(
            seller_create.model_dump()
        )

    async def token(self, email, password) -> str:
        return await self._generate_token(email, password)


#---
# Cụ thể, SellerService hiện đang sở hữu hai lớp quyền năng:

# 1. Quyền năng từ UserService (Kế thừa)
# Mặc dù bạn không viết lại, SellerService vẫn có thể truy cập các phương thức sau:

# _add_user(...): Dùng để mã hóa mật khẩu và lưu vào database.

# _get_by_email(...): Dùng để tìm kiếm người bán theo email.

# _generate_token(...): Dùng để kiểm tra mật khẩu và tạo JWT.

# 2. Quyền năng từ BaseService (Kế thừa gián tiếp)
# Vì UserService kế thừa BaseService, nên SellerService cũng có luôn các phương thức CRUD cơ bản:

# _get(id)

# _add(entity)

# _update(entity)

# _delete(entity)

#---
# Dòng lệnh super().__init__(Seller, session) là cách gọi hàm khởi tạo của lớp cha. Trong trường hợp của bạn, lớp cha chính là UserService.

# Hãy tưởng tượng nó như một "hợp đồng chuyển giao": SellerService nói với UserService rằng: "Hãy dùng cấu trúc và các chức năng của bạn để phục vụ cho đối tượng Seller và sử dụng session này để kết nối Database".

# Giải mã chi tiết:
# super(): Đây là từ khóa trong Python dùng để tham chiếu đến lớp cha (UserService).

# __init__: Là hàm khởi tạo. Khi bạn tạo một đối tượng SellerService, hàm này được chạy đầu tiên để thiết lập mọi thứ.

# (Seller, session): Đây là 2 tham số bạn truyền lên cho UserService.