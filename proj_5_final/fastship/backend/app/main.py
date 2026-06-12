from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRoute
from scalar_fastapi import get_scalar_api_reference

from app.api.router import master_router
from app.api.tag import APITag
from app.core.exceptions import add_exception_handlers
# from app.core.logging import logger

description = """
Delivery Management System for sellers and delivery agents

### Seller
- Submit shipment effortlessly
- Share tracking links with customers

### Delivery Agent
- Auto accept shipments
- Track and update shipment status
- Email and SMS notifications
"""
tags_metadata = [
        {
            "name": APITag.SHIPMENT.value,
            "description": "Operations related to shipments.",
        },
        {
            "name": APITag.SELLER.value,
            "description": "Operations related to seller.",
        },
        {
            "name": APITag.PARTNER.value,
            "description": "Operations related to delivery partner.",
        },
    ]


def custom_generate_unique_id_function(route: APIRoute) -> str:
    return route.name

app = FastAPI(
    title="FastShip",   # Đặt tên cho ứng dụng, tên này sẽ hiển thị trên trang tài liệu API
    description=description,    # Gán phần mô tả dự án (biến description đã khai báo phía trên)
    docs_url=None,  # Tắt trang tài liệu Swagger mặc định (/docs) vì dự án dùng Scalar thay thế
    redoc_url=None, # Tắt trang tài liệu ReDoc mặc định (/redoc)
    version="0.1.0",    # Đánh dấu phiên bản hiện tại của API
    openapi_tags=tags_metadata, # Truyền danh sách các thẻ để phân loại (group) các API trong tài liệu
    # generate_unique_id_function=custom_generate_unique_id_function,
)

# Add CORS middleware to allow requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],    # Chỉ cho phép các địa chỉ này truy cập vào API của bạn (ở đây là frontend React)
    allow_credentials=True, # Cho phép gửi cookie, session hoặc thông tin xác thực qua request
    allow_methods=["*"],    # Cho phép tất cả các phương thức HTTP (GET, POST, PUT, DELETE, v.v.)
    allow_headers=["*"],    # Cho phép tất cả các loại header trong request
)

# Add all endpoints
app.include_router(master_router)   #them router

# Add custom exception handlers
add_exception_handlers(app) # Đăng ký các trình xử lý lỗi (exception handlers) tùy chỉnh để trả về phản hồi chuẩn xác khi có lỗi xảy ra

@app.get('/')
def root():
    return {"message": "Welcome to FastShip API!"}

# Scalar API Documentation
@app.get("/docs", include_in_schema=False)
def get_scalar_docs():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title="Scalar API",
    )
