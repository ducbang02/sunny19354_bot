# Sunny 2.0

Bot Telegram cá nhân @sunny19354_bot: ghi chú và reminder. Đang bootstrap, chưa có chương trình bot để chạy. Phạm vi: PROJECT.md; tiến độ: docs/TASKS.md.

## Audit môi trường — 2026-10-08

| Nhóm | Công cụ | Trạng thái / đề xuất |
| --- | --- | --- |
| Runtime | Python 3.13.15, Git 2.53, uv 0.11.8, Node 24.18 | Đã chạy version check; không cần cài lại |
| Codex plugin/skill | Superpowers | Chưa cài; nên dùng để hỗ trợ planning/debugging/verification |
| MCP/plugin | Context7 | Chưa cài trong directory; CLI/session chưa có MCP tương ứng; nên dùng để tra docs |
| Dev tool | Gitleaks | Không tìm thấy trên PATH; nên cài để kiểm tra secrets |
| Dev dependency | pytest | Chưa có trong Python hiện tại; cài local trong .venv |
| Runtime dependencies | python-telegram-bot, python-dotenv, tzdata | Chưa có trong Python hiện tại; requirements.txt đã chuẩn bị |
| Skill | Ponytail | Chưa có trong danh sách skill phiên này; tùy chọn, AGENTS.md đã chứa nguyên tắc cốt lõi |
| Tool | Serena, Spec Kit | Chưa cần cho V1 nhỏ |
| UI/browser | UI/UX Pro Max, Playwright MCP | Chưa cần cho Telegram bot không có web UI |
| Dev tool | Ruff | Không tìm thấy; tùy chọn sau, chưa thêm dependency |
| Shell | PowerShell 7 (pwsh) | Không thấy trên PATH; Windows PowerShell hiện tại đã chạy được, không bắt buộc cài |

Kết quả package chỉ áp dụng interpreter Python đã kiểm tra, không kết luận về mọi môi trường khác trên máy. Công cụ hỗ trợ agent không phải dependency runtime của bot.

## 1. Tự cài Superpowers và Context7

Trong Codex, mở phần plugin và tìm **Superpowers**, **Context7**, rồi chọn cài và hoàn tất bước kết nối nếu được yêu cầu. Hai plugin này đã được tìm thấy trong directory với trạng thái chưa cài. Cài ở Codex, không clone source tool vào repository bot.

Sau đó mở phiên Codex mới hoặc restart nếu ứng dụng yêu cầu. Nhờ agent kiểm tra skills/tools đã load và thực hiện một tra cứu docs bằng Context7; chỉ hiện trong danh sách chưa đủ chứng minh công cụ hoạt động. Nếu dùng nhiều bề mặt Codex/IDE, verify lại tại nơi sẽ phát triển bot.

Nguồn: [Superpowers](https://github.com/obra/superpowers), [Context7](https://github.com/upstash/context7), [OpenAI Docs về skills](https://learn.chatgpt.com/docs/build-skills).

## 2. Tự cài thư viện Python trong project

Mở terminal PowerShell tại repository, chạy từng lệnh:

~~~powershell
Set-Location 'D:\Workspace\Bot\sunny19354_bot'
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -m pytest --version
.\.venv\Scripts\python.exe -c "import telegram, dotenv, tzdata; from telegram.ext import JobQueue; print('Imports OK; PTB', telegram.__version__)"
~~~

Gọi trực tiếp Python trong .venv nên không cần activate hay thay ExecutionPolicy. Lệnh install sẽ cài thư viện bot và pytest vào project, không cài global. Chưa có test ứng dụng; pytest --version chỉ kiểm tra cài đặt. Sau khi cài, agent sẽ kiểm tra phiên bản đã resolve và khóa dependency trước checkpoint phù hợp.

Nguồn thư viện: [python-telegram-bot](https://docs.python-telegram-bot.org/en/stable/).

## 3. Tự cài Gitleaks

Mở [Gitleaks Releases](https://github.com/gitleaks/gitleaks/releases/latest), tải archive Windows phù hợp kiến trúc máy ở Assets và giải nén vào thư mục công cụ riêng. Có thể thêm thư mục chứa gitleaks.exe vào User PATH rồi mở terminal mới; hoặc gọi bằng đường dẫn đầy đủ, không cần PATH.

~~~powershell
# Nếu đã thêm vào PATH:
gitleaks version
gitleaks dir . --redact
~~~

Nếu dùng đường dẫn đầy đủ, ví dụ:

~~~powershell
& 'C:\Tools\gitleaks\gitleaks.exe' version
& 'C:\Tools\gitleaks\gitleaks.exe' dir . --redact
~~~

Đổi đường dẫn ví dụ thành vị trí bạn đã giải nén. Chỉ exit code 0 mới coi scan đạt. Gitleaks hiện được maintainer thông báo chỉ nhận security patches; vẫn phù hợp bước quét secrets của bootstrap này. [Nguồn](https://github.com/gitleaks/gitleaks).

## 4. Cấu hình riêng trên máy

~~~powershell
Copy-Item .env.example .env
~~~

Chỉ chạy copy khi chưa có .env. Tự điền TELEGRAM_BOT_TOKEN và numeric OWNER_TELEGRAM_ID bằng editor; không paste token vào chat. SQLite/runtime data và .env đã được ignore. Chưa có feature để lấy user ID trong bot; agent sẽ hướng dẫn lấy ID qua Telegram sau khi foundation sẵn sàng, không cần gửi token.

## Tiếp tục

Báo lại những mục đã cài hoặc muốn bỏ qua. Agent verify môi trường, chuẩn bị baseline, quét secrets, commit bootstrap rồi triển khai milestone đầu. Không bắt buộc cài Superpowers/Context7 để bot chạy; có thể chọn bỏ qua. Chưa commit, chưa kết nối remote hoặc push; remote dự kiến https://github.com/ducbang02/sunny19354_bot.git. Chưa tự tạo GitHub repository vì prompt chưa xác nhận quyền tạo/visibility.
