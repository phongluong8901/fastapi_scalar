import asyncio
import time

from rich import print


async def endpoint(route: str) -> str:
    print(f">> handling {route}")
    
    # emulate database delay
    await asyncio.sleep(1)
    
    print(f"<< response {route}")

    # will be returned from coroutine
    return route


async def server():
    # Run test requests
    tests = (
        "GET /shipment?id=1",
        "PATCH /shipment?id=4",
        "GET /shipment?id=3",
    )

    start = time.perf_counter()

    # Task Group
    async with asyncio.TaskGroup() as task_group:
        tasks =  [
            # on task creation, corountine will
            # be executed as well
            task_group.create_task(endpoint(route))
            for route in tests
        ]

        print(
            "Task[0] Result: ",
            # manually await result for task coroutine
            await tasks[0]
        )

    end = time.perf_counter()
    print(f"Time taken: {end - start:.2f}s")


# Run server with asyncio
asyncio.run(
    server(),
)

#---
# Đoạn code này minh họa sức mạnh của Lập trình bất đồng bộ (Asynchronous Programming) trong Python. Thay vì xử lý từng yêu cầu một cách tuần tự (đợi xong cái này mới làm cái kia), chương trình này xử lý tất cả cùng lúc.

# Dưới đây là giải thích từng phần:

# 1. Hàm endpoint(route): Mô phỏng xử lý API
# async def: Định nghĩa đây là một coroutine. Nó có thể tạm dừng (pause) khi gặp lệnh await.

# await asyncio.sleep(1): Đây là "điểm khóa". Khi gặp dòng này, Python sẽ tạm dừng hàm endpoint trong 1 giây để "đợi" (giả lập việc truy vấn database). Điều quan trọng: Trong lúc đợi, Python không đứng yên mà sẽ chuyển sang chạy các công việc khác.

# 2. Hàm server(): Điều phối công việc
# async with asyncio.TaskGroup() as task_group:: Đây là cách hiện đại (từ Python 3.11+) để quản lý một nhóm tác vụ. Tất cả các tác vụ trong nhóm này sẽ chạy song song.

# task_group.create_task(...): Dòng này ra lệnh cho Python: "Hãy bắt đầu chạy hàm endpoint này ngay lập tức". Với 3 route trong tests, nó sẽ tạo ra 3 tác vụ chạy đồng thời.

# Luồng chạy của chương trình (Workflow)
# Khởi tạo: server() tạo ra 3 task cho 3 route: GET /shipment?id=1, PATCH /shipment?id=4, và GET /shipment?id=3.

# Chạy song song:

# Task 1 chạy -> in >> handling ... -> gặp await -> tạm dừng.

# Task 2 chạy -> in >> handling ... -> gặp await -> tạm dừng.

# Task 3 chạy -> in >> handling ... -> gặp await -> tạm dừng.

# Đợi: Trong vòng 1 giây tiếp theo, cả 3 task đều đang nằm trong trạng thái chờ sleep. Python tận dụng thời gian này một cách tối ưu.

# Hoàn thành: Sau 1 giây, cả 3 task cùng "tỉnh dậy", in << response ... và trả về giá trị.

# Kết quả thời gian
# Nếu bạn chạy code này, Time taken sẽ là khoảng 1.00s, thay vì 3.00s (nếu chạy tuần tự).