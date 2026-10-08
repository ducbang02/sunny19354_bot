# Sunny 2.0

Telegram bot cá nhân **@sunny19354_bot**: ghi chú và reminder một lần. Chạy local bằng Python, lưu SQLite, chỉ chủ bot sử dụng trong chat riêng.

Phạm vi: [PROJECT.md](PROJECT.md). Tiến độ: [docs/TASKS.md](docs/TASKS.md). Roadmap: [docs/ROADMAP.md](docs/ROADMAP.md).

## Cài đặt

Yêu cầu Python 3.13. Mở PowerShell tại repository:

~~~powershell
Set-Location 'D:\Workspace\Bot\sunny19354_bot'
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.lock
.\.venv\Scripts\python.exe -m pip check
~~~

requirements.lock khóa phiên bản runtime và pytest đã được verify. requirements.txt và requirements-dev.txt mô tả dependency trực tiếp. Không cần activate .venv, đổi ExecutionPolicy hoặc cài thư viện Python global. VS Code: workspace mặc định mở Git Bash và tự activate môi trường Python cho terminal mới. Nếu VS Code đã nhớ interpreter khác, chạy Python: Select Interpreter → .venv/Scripts/python.exe một lần, rồi đóng terminal cũ và tạo terminal mới. Dấu (.venv) biểu thị môi trường Python; tên trong ngoặc ở prompt Git Bash là nhánh Git hiện tại.

## Cấu hình

Nếu chưa có .env:

~~~powershell
if (-not (Test-Path -LiteralPath .env)) { Copy-Item .env.example .env }
notepad .env
~~~

Điền trực tiếp trên máy:

| Biến | Ý nghĩa |
| --- | --- |
| TELEGRAM_BOT_TOKEN | Token từ BotFather; không gửi vào chat hoặc Git |
| OWNER_TELEGRAM_ID | Numeric Telegram user ID của bạn, không phải username |
| BOT_TIMEZONE | Múi giờ IANA, mặc định Asia/Bangkok (UTC+7) |
| DATABASE_PATH | File SQLite; mặc định data/bot.sqlite3, đường dẫn tương đối tính từ root project |
| PTB_TIMEDELTA | Đặt 1 theo mẫu để dùng kiểu thời gian mới cho retry_after của PTB |

Có thể lấy numeric ID bằng bot thông tin user mà bạn tin tưởng; chỉ gửi /start, không cung cấp bot token. Hoặc dùng Telegram Bot API getUpdates trên máy với token local để đọc message.from.id; không đưa token vào URL trình duyệt/chat. Tài liệu: [Telegram Bot API](https://core.telegram.org/bots/api#getupdates).

Kiểm tra cấu hình (không gọi Telegram hoặc tạo DB):

~~~powershell
.\.venv\Scripts\python.exe -m sunny_bot --check-config
~~~

Thiếu hoặc sai cấu hình: exit 2 với thông báo an toàn. Khi hợp lệ: Configuration OK.

## Chạy bot

~~~powershell
.\.venv\Scripts\python.exe -m sunny_bot
~~~

Mở chat riêng với @sunny19354_bot, gửi /start. Dừng bằng Ctrl+C. Chỉ chạy một tiến trình polling cho cùng token và file DB.

| Lệnh | Ví dụ |
| --- | --- |
| /help | Hướng dẫn và múi giờ hiện tại |
| /note <nội dung> | /note Mua sữa |
| /notes [trang] | /notes hoặc /notes 2 |
| /delnote <id> | /delnote 1 |
| /remind YYYY-MM-DD HH:MM <nội dung> | /remind 2030-12-01 09:00 Họp nhóm |
| /reminders [trang] | /reminders |
| /cancel <id> | /cancel 1 |

Thời gian phải ở tương lai và theo BOT_TIMEZONE. Mỗi ghi chú/reminder tối đa 1000 đơn vị UTF-16 (emoji thường tính là 2). Giữ được xuống dòng và nội dung dạng HTML dưới dạng chữ thường; danh sách 20 mục/trang, tự chia tin nhắn dài. Group, người khác và tin nhắn đã chỉnh sửa không được xử lý.

Reminder lưu UTC, được khôi phục khi restart; mục quá hạn gửi sau khi bot chạy lại. Nếu Telegram hoặc SQLite lỗi, reminder còn pending và thử lại sau ít nhất 60 giây, tuân theo RetryAfter. Nếu tin đã gửi mà SQLite tạm lỗi, bot chỉ thử lưu lại trạng thái trong cùng phiên chạy, không gửi lại tin. Không đảm bảo gửi đúng giờ khi máy ngủ/tắt/mất mạng. Có thể gửi trùng nếu tiến trình dừng ngay sau khi Telegram nhận tin nhưng trước khi SQLite ghi sent; timeout mạng cũng có thể khiến trạng thái giao tin không chắc chắn. Hủy lịch không thu hồi tin nhắn đã gửi.

## Kiểm thử

~~~powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m compileall -q sunny_bot tests
.\.venv\Scripts\python.exe -m pip check
~~~

Test dùng SQLite thật và Application/JobQueue thật, thay riêng HTTP transport Telegram; không cần token hoặc gửi tin ra ngoài. Chưa verify Telegram thật vì repository chưa có .env.

Kiểm tra thủ công sau khi cấu hình: /start → tạo/xem/xóa note; tạo reminder vài phút tới → nhận tin; tạo reminder khác → restart → kiểm tra vẫn gửi; hủy reminder → kiểm tra không gửi; thử từ user khác/group → không có dữ liệu phản hồi.

## Công cụ agent / bảo mật

Audit 2026-10-08:
- Superpowers đã nạp; Context7 MCP đã cấu hình và gọi resolve-library-id/query-docs thành công. Không cài lại.
- python-telegram-bot 22.8, python-dotenv 1.2.4, tzdata 2026.5, pytest 9.1.1 đã cài riêng trong .venv.
- Gitleaks 8.30.1 được tải từ release chính thức, xác minh SHA256 và cài local tại .tools/gitleaks/gitleaks.exe. Thư mục .tools không vào Git.
- Git/Python/uv/Node đã có. Chưa cần Serena, Spec Kit, UI/UX, Playwright hoặc plugin runtime.
- PowerShell có thể chặn codex.ps1; dùng codex.cmd thay thế, không cần đổi policy hệ thống.

Quét staged files trước commit bằng Gitleaks local (máy đã cài):

~~~powershell
.\.tools\gitleaks\gitleaks.exe git --pre-commit --staged --redact
~~~

Nếu clone trên máy khác, tải bản Windows phù hợp từ [Gitleaks Releases](https://github.com/gitleaks/gitleaks/releases/latest), giải nén vào cùng vị trí hoặc gọi đường dẫn đã cài. Chỉ xem scan thành công khi công cụ thực sự quét dữ liệu và không báo lỗi; không chỉ dựa exit code.

.env, .venv, .tools và data/ được ignore. Token không có trong source/log. SQLite chứa ghi chú dạng rõ; bảo vệ bằng quyền tài khoản Windows của bạn. Backup: dừng bot, sao chép data/bot.sqlite3 vào vị trí riêng; khôi phục khi bot đã dừng. Không commit DB hoặc bản sao lưu.
