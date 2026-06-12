# import logging

# import logtail

# logger = logging.getLogger("fastship")
# logger.setLevel(logging.INFO)

# logtail_handler = logtail.LogtailHandler(
#     source_token="your-toke",
#     host="your-host",
# )
# logtail_handler.setFormatter(
#     logging.Formatter(
#         "[%(levelname)s]: %(message)s"
#     )
# )
# logger.addHandler(logtail_handler)


#---
# logger = logging.getLogger("fastship"): Tạo ra một "người ghi chép" riêng cho dự án của bạn có tên là fastship. Tất cả các log từ dự án sẽ được đóng dấu tên này để dễ quản lý.

# logger.setLevel(logging.INFO): Thiết lập "độ nhạy" của log. Ở mức INFO, hệ thống sẽ ghi lại mọi tin nhắn thông báo, cảnh báo (WARNING) và lỗi (ERROR). Nếu bạn để ERROR, nó chỉ ghi lại các lỗi nghiêm trọng.

# logtail.LogtailHandler(...): Đây là cái "ống dẫn". Nó kết nối ứng dụng của bạn với dịch vụ Logtail thông qua source_token. Bất cứ log nào được đẩy vào logger sẽ được cái handler này gửi đi qua internet tới Logtail.

# logging.Formatter(...): Định dạng cách hiển thị tin nhắn. Hiện tại bạn đang để định dạng: [LEVEL]: nội dung thông báo.

# Ví dụ: [INFO]: Đã khởi tạo kết nối database thành công.

# logger.addHandler(logtail_handler): Gắn cái "ống dẫn" đó vào "người ghi chép".