from fastapi import HTTPException, status
from passlib.context import CryptContext

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.seller import SellerCreate
from app.database.models import Seller
from app.utils import generate_access_token

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class SellerService:
    def __init__(self, session: AsyncSession):
        # Get database session to perform database operations
        self.session = session

    async def add(self, credentials: SellerCreate) -> Seller:
        seller = Seller(
            **credentials.model_dump(exclude=["password"]),
            # Hashed password
            password_hash=password_context.hash(credentials.password),
        )
        self.session.add(seller)
        await self.session.commit()
        await self.session.refresh(seller)

        return seller
    
    async def token(self, email, password) -> str:
        # Validate the credentials
        result = await self.session.execute(
            select(Seller).where(Seller.email == email)
        ) 
        seller = result.scalar()

        if seller is None or not password_context.verify(
            password,
            seller.password_hash,
        ):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Email or password is incorrect",
            )
        
        token = generate_access_token(data={
            "user": {
                "name": seller.name,
                "id": seller.id,
            }        })

        return token
    
#---
# 1. Ý nghĩa từng thành phần
# credentials: Là đối tượng chứa thông tin người dùng (thường là class User hoặc UserLogin dùng Pydantic).

# .model_dump(): Đây là phương thức của Pydantic (phiên bản v2 trở đi) dùng để chuyển đổi dữ liệu từ "đối tượng" sang dạng "từ điển" (dict).

# Ví dụ: Từ User(id=1, username="admin", password="123") sẽ thành {"id": 1, "username": "admin", "password": "123"}.

# exclude=["password"]: Đây là tham số "loại trừ". Nó ra lệnh cho Pydantic: "Hãy lấy tất cả dữ liệu, nhưng bỏ qua cái key tên là 'password'".

#---
# Truy vấn Database: await self.session.execute(...) thực hiện tìm kiếm người bán (Seller) dựa trên email.