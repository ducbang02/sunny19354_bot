# Roadmap

## 0 — Bootstrap (hiện tại)
Đọc context; chốt phạm vi V1; tạo tài liệu, cấu hình mẫu và danh sách dependency; audit công cụ. Người dùng tự cài lần đầu. Verify công cụ, baseline rồi initial commit.

## 1 — Foundation
Ứng dụng polling chạy được; cấu hình được validate; giới hạn chủ bot/chat riêng; /start và /help. Kiểm tra cấu hình lỗi, người lạ và phản hồi Telegram thật.

## 2 — Ghi chú end-to-end
Tạo/xem/xóa ghi chú bằng SQLite; validate nội dung/ID; kiểm tra persistence qua restart.

## 3 — Reminder end-to-end
Tạo/xem/hủy reminder một lần; UTC và múi giờ; phục hồi lịch sau restart; xử lý thời điểm sai và reminder quá hạn.

## 4 — Quality và chạy local
Regression test, lỗi Telegram/mạng, tránh lộ secrets trong log, hướng dẫn sử dụng/backup. Chủ bot kiểm tra trên Telegram; checkpoint Git và push khi remote/auth được xác nhận.

## Backlog đề xuất (chưa triển khai)
- Bản tin BBC hằng ngày: chọn chuyên mục, ngôn ngữ và giờ gửi; dùng RSS/API được phép, tiêu đề và link nguồn, không sao chép toàn bài.
- Reminder lặp lại và /today để xem việc trong ngày.
- Tìm kiếm ghi chú, nhãn và export/backup.
- Chạy 24/7 trên VPS sau khi thống nhất vận hành/chi phí.
- Điều khiển PC: milestone riêng, chỉ lệnh allowlist, xác thực chủ bot, xác nhận thao tác nguy hiểm; không chạy shell tùy ý từ tin nhắn.
- AI chat hoặc voice note khi có nhu cầu rõ và thống nhất chi phí/quyền dữ liệu.
