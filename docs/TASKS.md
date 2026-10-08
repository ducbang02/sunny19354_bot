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
- [x] Verify token local, owner chat và menu 8 lệnh qua Telegram API thật; không lộ token.
- [ ] Verify lệnh từ tài khoản Telegram thật đi qua polling vào bot đang chạy.

## Milestone 2 — Ghi chú
- [x] Tạo/xem/xóa SQLite, validation và phản hồi tiếng Việt.
- [x] Test CRUD, ID không tồn tại, Unicode/xuống dòng, input lỗi, phân trang và persistence qua restart.
- [x] Verify handler tạo/xem/xóa ghi chú và phản hồi qua Telegram API thật với DB test riêng.

## Milestone 3 — Reminder
- [x] Tạo/xem/hủy, múi giờ, lưu UTC, phục hồi lịch và xử lý reminder quá hạn.
- [x] Test ngày/giờ lỗi, DST, hủy, restart, JobQueue đến hạn/quá hạn và lỗi API/rate limit.
- [x] Retry lỗi SQLite; tin đã gửi chỉ retry lưu trạng thái trong cùng phiên chạy.
- [x] Test hủy trong lúc đang gửi và sau khi gửi nhưng SQLite chưa ghi được trạng thái.
- [x] Verify gửi nhắc thật bằng JobQueue và phục hồi DB/lịch khi tạo lại Application test.
- [ ] Verify luồng tạo reminder từ tài khoản Telegram thật qua polling và restart tiến trình bot chính.

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
Người dùng đã điền .env; --check-config pass. Bot chính đang chạy. Đã kiểm tra handler/JobQueue với API Telegram thật, dùng DB tạm riêng và không dừng bot chính. Còn luồng nhận lệnh từ tài khoản Telegram qua polling và restart tiến trình chính; không yêu cầu gửi credentials vào chat.

Môi trường: Git/Python/uv/Node có sẵn; Superpowers/Context7 đã có; thư viện thiếu đã được cài riêng .venv theo yêu cầu mới. Gitleaks local tại .tools/gitleaks/gitleaks.exe. Không cần cài global các thư viện của bot. codex.cmd dùng được khi PowerShell chặn codex.ps1; không đổi policy hệ thống.

## Execution ledger
- Task 1: Config/CLI RED 15 failures → GREEN 15 passed; kiểm tra cấu hình không có network/DB side effects.
- Task 2: SQLite RED 8 failures → GREEN suite 23 passed; CRUD, pagination, UTC, restart và conditional state transitions.
- Task 3: Application/JobQueue thật với HTTP transport giả; suite cuối 61 passed, không gửi tin ra ngoài.
- Review fix: hai regression tests tái hiện SQLite read/commit failures trước sửa; sau sửa tự retry và không gửi lại tin đã thành công trong cùng phiên. Thêm kiểm thử hủy đồng thời và hủy sau lỗi commit.
- Ruling: /notes và /reminders hiển thị toàn bộ nội dung trong chunks <=4000 UTF-16 units, thay vì cắt tóm tắt vì V1 không có lệnh đọc riêng; đổi lại danh sách dài có nhiều tin nhắn.
- Giới hạn đã ghi README: sau crash hoặc timeout giao tin có thể trùng; chưa bảo đảm exactly-once. Máy cần bật/kết nối mạng.

## Terminal workspace — 2026-10-08
- [x] Thêm .vscode/settings.json: Git Bash mặc định, chọn .venv và auto activation cho terminal mới.
- [x] Kiểm tra JSON và tên setting với manifest extension Python đã cài; README có hướng dẫn chọn lại interpreter nếu VS Code đã nhớ lựa chọn cũ.
- [x] Người dùng xác nhận terminal hoạt động sau khởi động lại; agent không trực tiếp quan sát UI.

## Terminal repair — 2026-10-08
- [x] Tái hiện Git Bash mới chưa activate .venv và Git báo dubious ownership do .git thuộc tài khoản sandbox.
- [x] Đổi default profile cấp người dùng từ bash (MSYS2) sang Git Bash; giữ nguyên các setting khác.
- [x] Thêm activation block trong ~/.bashrc, chỉ áp dụng khi terminal khởi động trong project này; không phụ thuộc Python extension đã chọn interpreter.
- [x] Thêm safe.directory đúng D:/Workspace/Bot/sunny19354_bot cho tài khoản Sunny; không tin cậy wildcard.
- [x] Sao lưu settings.json, .bashrc và .gitconfig trước khi sửa tại C:/Users/Sunny/.codex/backups/terminal-20261008-195712.
- [x] Git Bash login/interactive mới: Python dùng venv, prompt có (.venv), __git_ps1 trả (feat/personal-assistant); lặp lại kiểm tra vẫn pass. Ngoài project không tự activate venv.
- Lưu ý: kiểm tra bằng tiến trình Git Bash thật; agent chưa quan sát trực tiếp terminal UI VS Code. Cấu hình áp dụng cho terminal tạo mới.

## VS Code terminal follow-up — 2026-10-08
User reported Terminal > New Terminal and + still open CMD. Prior verification covered a separately launched Git Bash, not the VS Code UI. Native Computer Use connection failed twice (native pipe unavailable). User settings had returned to MSYS2. Set Git Bash to the explicit executable path at user/workspace levels and backed up user settings again. VS Code window reload and actual integrated-terminal verification remain pending; do not claim this UI issue resolved from the standalone-shell test alone.

Follow-up: người dùng xác nhận ổn sau khởi động lại. File .vscode/settings.json hiện bị xóa trong working tree; giữ nguyên thay đổi này, không tự khôi phục.

## Feature verification — 2026-10-08
- [x] Chạy suite với .env thật tồn tại: phát hiện test CLI missing-owner đọc lại owner từ .env (60 pass, 1 fail). Cô lập subprocess bằng PYTHON_DOTENV_DISABLED=1 theo docs python-dotenv; suite cuối 61 pass.
- [x] Config check, pip check và compileall pass.
- [x] Live smoke: 10 nhóm kiểm tra pass, Telegram chấp nhận 17 tin nhắn tới chat riêng của owner: menu/auth; start/help; note CRUD/Unicode/newline/literal HTML; ID thiếu; từ chối user/group/edited; input lỗi; remind/list/cancel/UTC; stale job; SQLite persistence; restore idempotent; reminder quá hạn/tương lai gửi thật.
- [x] Dùng SQLite tạm riêng và dọn sau test; không đọc/sửa DB cá nhân, không chạy polling thứ hai, không dừng bot chính. Hai Python process bot hiện tại là launcher và child, không phải hai poller riêng.
- Giới hạn: update đầu vào được mô phỏng vào Application.process_update, còn HTTP Telegram và JobQueue chạy thật. Tạo lại Application kiểm tra khôi phục state, chưa phải restart tiến trình chính. Browser/desktop automation không kết nối được trong session này nên chưa tự gửi command từ tài khoản Telegram qua UI. Definition of Done end-to-end vẫn để pending.
