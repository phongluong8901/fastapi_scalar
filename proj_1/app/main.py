from contextlib import asynccontextmanager

from fastapi import FastAPI
from scalar_fastapi import get_scalar_api_reference

from app.api.router import router
from app.database.session import create_db_tables


@asynccontextmanager
async def lifespan_handler(app: FastAPI):
    await create_db_tables()
    yield


app = FastAPI(
    # Server start/stop listener
    lifespan=lifespan_handler,
)


app.include_router(router)

### Scalar API Documentation
@app.get("/scalar", include_in_schema=False)
def get_scalar_docs():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title="Scalar API",
    )

#---
# Khi bạn định nghĩa app = FastAPI(lifespan=lifespan_handler), bạn đang bảo với FastAPI rằng:

# "Này FastAPI, trước khi bạn mở cổng 8000 để nhận request, hãy chạy cái hàm lifespan_handler này để chuẩn bị mọi thứ nhé."

# Nếu lifespan_handler chạy thành công: Server mới bắt đầu chạy.

# Nếu lifespan_handler gặp lỗi (ví dụ: lỗi kết nối Database): Server sẽ dừng lại ngay lập tức và báo lỗi Application startup failed.

# Trong FastAPI, lifespan là một cơ chế cho phép bạn thực hiện các tác vụ ngay khi ứng dụng vừa khởi động (startup) và ngay trước khi ứng dụng tắt hẳn (shutdown).