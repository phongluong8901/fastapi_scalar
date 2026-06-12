from fastapi import HTTPException, status
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import User
from app.utils import generate_access_token

from .base import BaseService

password_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


class UserService(BaseService): 
    def __init__(self, model: User, session: AsyncSession):
        self.model = model
        self.session = session

    async def _add_user(self, data: dict) -> User:
        user = self.model(
            **data, # **data: "giải nén" từ điển (dictionary) thành các tham số (ví dụ: name="A", email="a@b.com", password="123")
            password_hash=password_context.hash(data["password"]),
        )
        return await self._add(user)    #Lưu vào Database thông qua hàm _add() đã kế thừa từ BaseService

    async def _get_by_email(self, email) -> User | None:
        return await self.session.scalar(
            select(self.model).where(self.model.email == email)
        )

    async def _generate_token(self, email, password) -> str:
        # Validate the credentials
        user = await self._get_by_email(email)

        if user is None or not password_context.verify(
            password,
            user.password_hash,
        ):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Email or password is incorrect",
            )

        return generate_access_token(
            data={
                "user": {
                    "name": user.name,
                    "id": str(user.id),
                },
            }
        )

#---
# Dưới đây là những gì UserService của bạn có thể làm nhờ việc kế thừa:

# Các phương thức kế thừa từ BaseService:

# _get(id): Truy vấn bất kỳ User nào theo UUID.

# _add(entity): Thêm một User mới vào Database.

# _update(entity): Cập nhật thông tin User.

# _delete(entity): Xóa một User.

# Phương thức tự thân (của riêng UserService):

# _add_user(data): Phương thức này bổ sung logic nghiệp vụ (hash mật khẩu) trước khi gọi phương thức _add của lớp cha.

# _get_by_email(email): Phương thức tìm kiếm chuyên biệt cho User.

# _generate_token(email, password): Phương thức xử lý logic đăng nhập.

#---
# async def _get_by_email(self, email) -> User | None:
#     # 1. select(self.model): Tạo câu lệnh "SELECT * FROM [bảng]"
#     # 2. .where(self.model.email == email): Thêm điều kiện lọc "WHERE email = '...'"
#     # 3. self.session.scalar(...): Đây là chìa khóa để lấy kết quả
#     return await self.session.scalar(
#         select(self.model).where(self.model.email == email)
#     )