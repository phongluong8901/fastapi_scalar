from fastapi.security import OAuth2PasswordBearer


oauth2_scheme_seller = OAuth2PasswordBearer(tokenUrl="/seller/token")
oauth2_scheme_partner = OAuth2PasswordBearer(tokenUrl="/partner/token")

#---
# Ý nghĩa của từng dòng:
# OAuth2PasswordBearer là một công cụ tích hợp sẵn của FastAPI giúp bạn quản lý luồng xác thực theo chuẩn OAuth2.

# tokenUrl="/seller/token": Đây là "địa chỉ" (endpoint) mà client (ví dụ: giao diện web hoặc app mobile) sẽ gửi username và password tới để đổi lấy một cái Token.

# oauth2_scheme_...: Biến này đóng vai trò như một "người gác cổng". Khi bạn dùng nó trong các route của API, FastAPI sẽ tự động:

# Kiểm tra xem trong header của request có chứa cái Token (thường là Authorization: Bearer <token>) hay không.

# Nếu không có token, nó sẽ tự động chặn request và trả về lỗi 401 Unauthorized.

# Nếu có token, nó sẽ trích xuất token đó ra để bạn sử dụng.

# #---
# Tại sao bạn lại có 2 cái scheme riêng biệt?
# Vì bạn có 2 loại đối tượng truy cập (Seller và Delivery Partner), mỗi loại có một logic xác thực riêng:

# Sự phân tách: Bạn không thể dùng chung một luồng xác thực vì mỗi nhóm có URL nhận token khác nhau (/seller/token vs /partner/token).

# Bảo mật: Bạn có thể kiểm tra xem token đó là của Seller hay của Partner thông qua các scheme này.