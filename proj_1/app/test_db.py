import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from config import settings # Đảm bảo import đúng đường dẫn settings của bạn

async def check_connection():
    print(f"--- Đang kiểm tra cấu hình từ .env ---")
    print(f"Server: {settings.POSTGRES_SERVER}")
    print(f"DB: {settings.POSTGRES_DB}")
    print(f"User: {settings.POSTGRES_USER}")
    
    # Tạo engine async
    engine = create_async_engine(settings.POSTGRES_URL)
    
    try:
        async with engine.connect() as conn:
            # Thực thi một lệnh SQL đơn giản để kiểm tra kết nối
            result = await conn.execute(text("SELECT 1"))
            print("\n✅ Kết nối tới PostgreSQL THÀNH CÔNG!")
            print(f"Kết quả truy vấn thử nghiệm: {result.scalar()}")
    except Exception as e:
        print("\n❌ Kết nối THẤT BẠI!")
        print(f"Lỗi chi tiết: {e}")
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(check_connection())