# Roadmap

## 0 — Bootstrap (đã hoàn tất local)
Đã chốt phạm vi V1, chuyển tài liệu tiến độ vào docs/, audit và bổ sung dependency còn thiếu trong .venv, verify công cụ và tạo initial commit.

## 1 — Foundation
Ứng dụng polling chạy được; cấu hình được validate; giới hạn chủ bot/chat riêng; /start và /help. Kiểm tra cấu hình lỗi, người lạ và phản hồi Telegram thật.

## 2 — Ghi chú end-to-end
Tạo/xem/xóa ghi chú bằng SQLite; validate nội dung/ID; kiểm tra persistence qua restart.

## 3 — Reminder end-to-end
Tạo/xem/hủy reminder một lần; UTC và múi giờ; phục hồi lịch sau restart; xử lý thời điểm sai và reminder quá hạn.

## 4 — Quality và chạy local (hiện tại)
Implementation milestone 1–3 đã qua kiểm thử tự động, gồm retry API/SQLite và hủy đồng thời. Handler và JobQueue đã được kiểm tra với API Telegram thật bằng database test riêng, gồm khôi phục sau khi tạo lại Application. Còn xác minh luồng nhận lệnh qua polling từ tài khoản Telegram của chủ bot; xem checklist tại TASKS.md.

## Backlog đề xuất (chưa triển khai)
- Bản tin BBC hằng ngày: chọn chuyên mục, ngôn ngữ và giờ gửi; dùng RSS/API được phép, tiêu đề và link nguồn, không sao chép toàn bài.
- Reminder lặp lại và /today để xem việc trong ngày.
- Tìm kiếm ghi chú, nhãn và export/backup.
- Chạy 24/7 trên VPS sau khi thống nhất vận hành/chi phí.
- Điều khiển PC: milestone riêng, chỉ lệnh allowlist, xác thực chủ bot, xác nhận thao tác nguy hiểm; không chạy shell tùy ý từ tin nhắn.
- AI chat hoặc voice note khi có nhu cầu rõ và thống nhất chi phí/quyền dữ liệu.
