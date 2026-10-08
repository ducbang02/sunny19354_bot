# Sunny 2.0 — sunny19354_bot

## Overview
Telegram bot cá nhân @sunny19354_bot giúp chủ bot ghi chú và tạo reminder. Bot đã được tạo qua BotFather. V1 đã qua kiểm thử tự động và kiểm tra handler/JobQueue với API Telegram thật. Luồng nhận lệnh từ tài khoản người dùng qua polling còn chờ xác minh; chi tiết tại docs/TASKS.md.

## Target Users
Một chủ bot, sử dụng trong chat riêng Telegram.

## Problem
Ghi nhanh thông tin và nhận nhắc việc ngay trong Telegram, dữ liệu còn sau khi khởi động lại.

## Goals
V1 nhỏ, chạy local, dùng được trọn luồng và không cần dịch vụ trả phí.

## Core Features / V1 Scope
- /start, /help: hướng dẫn tiếng Việt.
- /note <nội dung>, /notes, /delnote <id>: tạo, xem và xóa ghi chú.
- /remind YYYY-MM-DD HH:MM <nội dung>, /reminders, /cancel <id>: reminder một lần, thời gian cụ thể để tránh hiểu nhầm ngôn ngữ tự nhiên.
- Lưu SQLite; khôi phục lịch reminder khi restart. Reminder quá hạn được gửi khi bot chạy lại. Không bảo đảm giao tin đúng một lần khi tiến trình dừng đúng lúc gửi.
- Chỉ xử lý người có OWNER_TELEGRAM_ID trong chat riêng; thiếu cấu hình hợp lệ thì không khởi động.

## Non-Goals
Chưa có AI chat, web UI, nhiều người dùng, cloud deployment, tin BBC, điều khiển PC, reminder lặp lại hoặc phân tích thời gian tự nhiên. Các ý tưởng mở rộng nằm trong docs/ROADMAP.md.

## Main User Flows
1. Chủ bot gửi /note Mua sữa → xác thực → lưu SQLite → trả ID → /notes hiển thị lại.
2. Chủ bot gửi /remind với thời điểm tương lai → validate → lưu SQLite → lên lịch → gửi nhắc trong chat riêng.
3. Restart → đọc reminder chưa gửi → khôi phục lịch, xử lý reminder quá hạn.
4. Người khác hoặc group gửi lệnh → không cho truy cập dữ liệu hay thực thi chức năng.

## Tech Stack
- Python 3.13: đã có trên máy, phù hợp ngôn ngữ ưu tiên.
- python-telegram-bot 22.x với job-queue: xử lý Telegram và hẹn giờ trong một thư viện.
- sqlite3 trong standard library: lưu ghi chú/reminder, chưa cần database server.
- python-dotenv: đọc .env theo yêu cầu; tzdata hỗ trợ múi giờ IANA trên Windows.
- pytest trong .venv: kiểm tra business logic, persistence và handler bằng fake Telegram, không dùng token thật.
- Long polling: chạy local, không cần public endpoint hay webhook.
- Chưa thêm service layer, plugin runtime hoặc dependency phục vụ ý tưởng tương lai.

## External Services
Telegram Bot API. Không tích hợp OpenAI API hay nguồn tin trong V1.

## Security Considerations
Token chỉ nằm trong .env hoặc biến môi trường; không log token, request URL chứa token hoặc nội dung ghi chú. Không nhận token qua chat. Kiểm tra quyền ở mọi command/callback. Dùng SQL tham số hóa. .env, SQLite và bản sao lưu không vào Git. Chủ bot cấu hình numeric Telegram user ID, không xác thực bằng username.

## Deployment
Windows local trước. Máy cần bật và kết nối Internet để gửi nhắc đúng giờ. Múi giờ mặc định Asia/Bangkok (UTC+7), lưu thời điểm UTC. Chạy 24/7 và môi trường cloud sẽ chọn sau.

## Git
Origin: https://github.com/ducbang02/sunny19354_bot.git. Remote tồn tại và trống tại lần kiểm tra ban đầu. Bootstrap ở main; implementation ở feat/personal-assistant. Trạng thái checkpoint/push ghi tại docs/TASKS.md.

## Definition of Done
- Flow ghi chú và reminder chạy end-to-end trong Telegram với chủ bot.
- Người khác/group không truy cập được; input lỗi có phản hồi rõ.
- Dữ liệu còn sau restart; reminder tương lai và quá hạn được xử lý.
- Test phù hợp pass; không có regression chặn luồng chính.
- Hướng dẫn setup/run/test đầy đủ, secrets được kiểm tra trước commit.
- Bootstrap chỉ hoàn tất sau khi xử lý lựa chọn tool, kiểm tra môi trường, baseline, initial commit và remote/push theo quyền hiện có.
