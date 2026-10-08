# Tasks

## Current Milestone — Bootstrap
- [x] Đọc toàn bộ AGENTS.md, SETUP.md và yêu cầu đính kèm.
- [x] Kiểm tra thư mục và Git: bắt đầu với hai file hướng dẫn, chưa có repository.
- [x] Audit Python, Git, uv, Node, package Python, skills và MCP.
- [x] Tạo PROJECT.md, docs/ROADMAP.md, cấu hình mẫu và hướng dẫn cài thủ công.
- [x] Khởi tạo Git local trên main.
- [ ] Người dùng tự cài các công cụ đã chọn theo README.md.
- [ ] Verify công cụ: installed → available → agent truy cập được → basic test.
- [ ] Tạo package/baseline tối thiểu sau khi môi trường sẵn sàng; chạy kiểm tra phù hợp. Chưa có test ứng dụng để chạy ở lượt này.
- [ ] Quét secrets và tạo initial commit: chore: bootstrap project.
- [ ] Xác minh remote, authentication và push nếu repository tồn tại và có quyền.

## Milestone 1 — Foundation
- [ ] Implement config validation, polling, giới hạn chủ bot/chat riêng, /start và /help.
- [ ] Test cấu hình thiếu/sai, quyền truy cập và handler bằng fake Telegram.
- [ ] Verify bằng token do người dùng tự điền vào .env; không gửi token vào chat.

## Milestone 2 — Ghi chú
- [ ] Implement tạo/xem/xóa SQLite, validation và phản hồi tiếng Việt.
- [ ] Test CRUD, ID không tồn tại, nội dung lỗi và dữ liệu sau restart.
- [ ] Verify flow trên Telegram.

## Milestone 3 — Reminder
- [ ] Implement tạo/xem/hủy, múi giờ, lưu UTC, phục hồi lịch và reminder quá hạn.
- [ ] Test input lỗi, hủy, restart, reminder đến hạn/quá hạn.
- [ ] Verify gửi nhắc thật và restart trên local.

## Milestone 4 — Quality
- [ ] Kiểm tra lỗi mạng/API, regression, README run/test/backup và secret scan.
- [ ] Verify Definition of Done và checkpoint Git.

## Handoff — 2026-10-08
Người dùng yêu cầu tự cài công cụ lần đầu; agent chưa cài dependency/plugin nào và chưa viết feature. Superpowers/Context7 được directory báo chưa cài; chưa có MCP tương ứng trong CLI/session. Gitleaks, pytest, python-telegram-bot, python-dotenv, tzdata chưa có trong Python được kiểm tra. Git/Python/uv/Node đã có.

Terminal exec mặc định lỗi helper_unknown_error; đọc file và chạy lệnh kiểm tra được qua Node REPL/child_process. Đây không phải bằng chứng máy thiếu PowerShell. Bước tiếp theo: người dùng cài/chọn bỏ qua tool theo README, sau đó agent verify lại; chỉ tiếp tục development sau bootstrap theo SETUP.md. Initial commit/push chưa thực hiện. Remote URL đã được cung cấp nhưng quyền tạo repo/visibility chưa được xác định.

## Execution ledger
- Task 1: Config/CLI RED 15 failures → GREEN 15 passed. Safe config check has no network/DB side effects.
- Task 2: SQLite persistence RED 8 failures → GREEN suite 23 passed; CRUD, pagination, UTC, restart and conditional cancellation/sent verified.
- Ruling: /notes and /reminders will show full content in <=4000 UTF-16-unit chunks, rather than truncating summaries; otherwise there is no V1 command to read a saved long note. Cost if wrong: more Telegram messages on long lists.
