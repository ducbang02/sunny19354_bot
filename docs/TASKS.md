# Tasks

## Bootstrap và môi trường
- [x] Đọc AGENTS.md, SETUP.md và yêu cầu đính kèm; xác định phạm vi V1.
- [x] Chuyển roadmap/tasks vào docs/; cập nhật AGENTS.md và SETUP.md để tạo tại đây.
- [x] Audit Git, Python, uv, Node, skills/MCP và dependency người dùng đã cài.
- [x] Verify Superpowers đã nạp và Context7 MCP gọi resolve-library-id/query-docs được.
- [x] Bổ sung dependency vào .venv; khóa phiên bản tại requirements.lock; pip check và import/JobQueue smoke pass.
- [x] Cài Gitleaks local .tools, xác minh SHA256 release chính thức; không cài thêm plugin không cần thiết.
- [x] Initial commit 3c73d48 (chore: bootstrap project), đã quét secrets trước commit.
- [x] Xác nhận remote tồn tại, ban đầu trống; cấu hình origin theo URL người dùng cung cấp.
- [x] Push main (bootstrap) và feat/personal-assistant lên origin thành công.

## Milestone 1 — Foundation
- [x] Config validation, polling, giới hạn chủ bot/chat riêng, /start và /help.
- [x] Test cấu hình thiếu/sai, --check-config không tạo DB/kết nối mạng, quyền truy cập và handler.
- [ ] Verify Telegram thật bằng token người dùng tự điền vào .env; không gửi token vào chat.

## Milestone 2 — Ghi chú
- [x] Tạo/xem/xóa SQLite, validation và phản hồi tiếng Việt.
- [x] Test CRUD, ID không tồn tại, Unicode/xuống dòng, input lỗi, phân trang và persistence qua restart.
- [ ] Verify flow trên Telegram thật.

## Milestone 3 — Reminder
- [x] Tạo/xem/hủy, múi giờ, lưu UTC, phục hồi lịch và xử lý reminder quá hạn.
- [x] Test ngày/giờ lỗi, DST, hủy, restart, JobQueue đến hạn/quá hạn và lỗi API/rate limit.
- [x] Retry lỗi SQLite; tin đã gửi chỉ retry lưu trạng thái trong cùng phiên chạy.
- [x] Test hủy trong lúc đang gửi và sau khi gửi nhưng SQLite chưa ghi được trạng thái.
- [ ] Verify gửi nhắc thật và restart local.

## Milestone 4 — Quality
- [x] 61 tests pass; compileall và pip check pass.
- [x] CLI thiếu token trả mã 2 và thông báo an toàn; không có .env hoặc DB được tạo.
- [x] README hướng dẫn cài/chạy/test/cấu hình/backup và giới hạn giao tin.
- [x] Kiểm tra .env, .venv, .tools và data bị ignore; .env.example được track.
- [x] Review độc lập; sửa phát hiện Important về SQLite và bổ sung regression tests.
- [x] Gitleaks quét staged files (~39.58 KB), không phát hiện secrets; implementation commit eecadb8.
- [ ] Hoàn tất Definition of Done sau kiểm tra Telegram thật.

## Handoff — 2026-10-08
Development branch: feat/personal-assistant, đã push origin. Foundation/SQLite checkpoint: 214fd1d; notes/reminders: eecadb8. Main giữ bootstrap 3c73d48; chưa merge implementation vào main.
Implementation và kiểm thử tự động đã sẵn sàng; chưa có .env nên chưa chạy bot với Telegram thật. Bước phụ thuộc người dùng: copy .env.example thành .env, điền token/OWNER_TELEGRAM_ID tại máy, chạy --check-config rồi khởi động theo README. Không yêu cầu gửi credentials vào chat.

Môi trường: Git/Python/uv/Node có sẵn; Superpowers/Context7 đã có; thư viện thiếu đã được cài riêng .venv theo yêu cầu mới. Gitleaks local tại .tools/gitleaks/gitleaks.exe. Không cần cài global các thư viện của bot. codex.cmd dùng được khi PowerShell chặn codex.ps1; không đổi policy hệ thống.

## Execution ledger
- Task 1: Config/CLI RED 15 failures → GREEN 15 passed; kiểm tra cấu hình không có network/DB side effects.
- Task 2: SQLite RED 8 failures → GREEN suite 23 passed; CRUD, pagination, UTC, restart và conditional state transitions.
- Task 3: Application/JobQueue thật với HTTP transport giả; suite cuối 61 passed, không gửi tin ra ngoài.
- Review fix: hai regression tests tái hiện SQLite read/commit failures trước sửa; sau sửa tự retry và không gửi lại tin đã thành công trong cùng phiên. Thêm kiểm thử hủy đồng thời và hủy sau lỗi commit.
- Ruling: /notes và /reminders hiển thị toàn bộ nội dung trong chunks <=4000 UTF-16 units, thay vì cắt tóm tắt vì V1 không có lệnh đọc riêng; đổi lại danh sách dài có nhiều tin nhắn.
- Giới hạn đã ghi README: sau crash hoặc timeout giao tin có thể trùng; chưa bảo đảm exactly-once. Máy cần bật/kết nối mạng.
