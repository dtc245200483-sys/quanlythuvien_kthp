# Hệ thống Quản lý Thư viện Tích hợp AI Tra cứu Sách

Đồ án học phần **Ứng dụng Trí tuệ Nhân tạo** (ICTU) — Nhóm 02:
- Phạm Vũ Quang Hưng
- Trần Thị Thu Huyền

---

## 1. Yêu cầu hệ thống tối thiểu

- **Hệ điều hành:** Windows 10/11 (64-bit), macOS hoặc Linux.
- **Python:** Phiên bản **3.10, 3.11 hoặc 3.12** *(khuyến nghị Python 3.11; hạn chế dùng Python 3.13 do một số thư viện AI như PyTorch/Sentence-Transformers/ChromaDB chưa hỗ trợ hoàn toàn)*.
- **Cơ sở dữ liệu:** Microsoft SQL Server 2017/2019/2022 (bản Express hoặc Developer đều được) kèm SQL Server Management Studio (SSMS).
- **Driver kết nối:** [ODBC Driver 17 for SQL Server](https://learn.microsoft.com/vi-vn/sql/connect/odbc/download-odbc-driver-for-sql-server) (bắt buộc cài trên Windows khi chạy thủ công).
- **Kết nối mạng Internet:** Cần thiết cho lần khởi tạo đầu tiên (để tải trọng số model Embedding ~120MB và kết nối OpenRouter LLM API).
- **(Tùy chọn) Docker & Docker Compose:** Dành cho phương thức chạy container hóa.

---

## 2. Cấu trúc thư mục dự án

- `Frontend/` — Giao diện Web HTML/CSS/Vanilla JS (đã được Backend tự động mount tại `http://localhost:8000/`).
- `Backend/` — Web API xây dựng bằng FastAPI, SQLAlchemy, Alembic, SQL Server (xem `Backend/api_docs.md`).
- `chatbotAI/` — Module RAG AI độc lập: Vector Store ChromaDB, Sentence-Transformers Embedding, OpenRouter LLM Client.
- `docs/` — Tài liệu đặc tả yêu cầu (SRS), kiến trúc hệ thống, Use Case, thiết kế AI Engine.
- `qa/` — Bộ kiểm thử tự động độc lập của QA (Backend & UI test cases).

---

## 3. Hướng dẫn cài đặt & Chạy ứng dụng

Bạn có thể lựa chọn 1 trong 2 cách triển khai dưới đây:

### CÁCH 1: Chạy thủ công trên máy Local (Mặc định)

Thực hiện tuần tự các bước dưới đây bằng terminal PowerShell:

#### Bước 1: Mở thư mục Backend và khởi tạo môi trường ảo
```powershell
cd Backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

#### Bước 2: Cài đặt các thư viện phụ thuộc
```powershell
pip install -r requirements.txt
pip install -r ..\chatbotAI\requirements.txt
```
*(Tùy chọn: Nếu muốn chạy kiểm thử tự động, cài thêm: `pip install -r requirements-dev.txt`)*

#### Bước 3: Cấu hình biến môi trường (.env)
1. **Cấu hình Backend (`Backend/.env`):**
   Copy từ bản mẫu:
   ```powershell
   copy .env.example .env
   ```
   Mở file `.env` vừa tạo và chỉnh lại chuỗi kết nối `DATABASE_URL` cho đúng với instance SQL Server trên máy bạn:
   - Nếu dùng SQL Server mặc định:
     `DATABASE_URL=mssql+pyodbc://@localhost/LibraryDB?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes&TrustServerCertificate=yes`
   - Nếu dùng bản SQLEXPRESS:
     `DATABASE_URL=mssql+pyodbc://@localhost\SQLEXPRESS/LibraryDB?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes&TrustServerCertificate=yes`

2. **Cấu hình Chatbot AI (`chatbotAI/.env`):**
   Copy từ bản mẫu:
   ```powershell
   copy ..\chatbotAI\.env.example ..\chatbotAI\.env
   ```
   Mở file `chatbotAI/.env`, điền API Key từ [OpenRouter](https://openrouter.ai/):
   ```env
   OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxxxxxxxxx
   ```

#### Bước 4: Tạo Database và chạy Migration
Tạo Database `LibraryDB` trên SQL Server (nếu chưa có):
```powershell
sqlcmd -S "localhost" -E -Q "IF DB_ID('LibraryDB') IS NULL CREATE DATABASE LibraryDB;"
```
*(Nếu máy dùng SQLEXPRESS, thay `"localhost"` bằng `"localhost\SQLEXPRESS"`)*

Nâng cấp schema bảng bằng Alembic:
```powershell
python -m alembic upgrade head
```

#### Bước 5: Nạp dữ liệu mẫu toàn diện & Khởi tạo Vector Store
Chạy một lệnh duy nhất để tạo sẵn toàn bộ 5 tài khoản mẫu, 63 cuốn sách thực tế, phiếu mượn, tiền phạt và đồng bộ dữ liệu vào ChromaDB:
```powershell
python scripts/seed_full.py
```

#### Bước 6: Khởi động Server
```powershell
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

### CÁCH 2: Chạy tự động bằng Docker & Docker Compose (Khuyến nghị / Điểm cộng)

Nếu máy đã cài sẵn **Docker Desktop**, bạn có 2 cách khởi chạy:

**Cách nhanh nhất (Khuyến nghị):**
👉 Chỉ cần nhấp đúp chuột vào file **`run/1_chay_docker.bat`** — hệ thống sẽ tự động bật container, nạp dữ liệu và mở sẵn trình duyệt web tại `http://localhost:8000/`.

**Cách chạy bằng lệnh (Terminal):**
#### Bước 1: Khởi động hệ thống (Backend + SQL Server 2022)
```powershell
cd docker
docker compose up -d --build
```
*Lệnh này sẽ tự động tải SQL Server 2022, cài đặt ODBC Driver 17, build image Backend và kết nối mạng nội bộ.*

#### Bước 2: Khởi tạo bảng CSDL và nạp dữ liệu mẫu All-in-One
```powershell
# Tạo Database trong container SQL Server (nếu chưa có)
docker compose exec sqlserver /opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P "Password123!" -C -Q "IF DB_ID('LibraryDB') IS NULL CREATE DATABASE LibraryDB;"

# Nâng cấp bảng CSDL bằng Alembic
docker compose exec backend python -m alembic upgrade head

# Nạp 5 tài khoản mẫu, 63 cuốn sách thực tế và đồng bộ ChromaDB
docker compose exec backend python scripts/seed_full.py
```

#### Bước 3: Kiểm tra và dừng container
- Truy cập ngay hệ thống tại: `http://localhost:8000/`
- Khi muốn dừng hệ thống:
  ```powershell
  cd docker
  docker compose down
  ```
  *(Hoặc nhấp đúp chuột vào file `run/2_dung_docker.bat`).*
*(Dữ liệu SQL Server và Vector Store của ChromaDB được lưu bền vững qua volume, không bị mất khi tắt container).*

---

## 4. Truy cập giao diện & Tài khoản Demo

Khi server đang chạy (dù chạy theo Cách 1 hay Cách 2):
- Mở trình duyệt truy cập thẳng: **`http://localhost:8000/`** *(Backend đã tự mount toàn bộ giao diện Frontend, hoàn toàn không bị lỗi CORS)*.

### Danh sách tài khoản đăng nhập mẫu (đã được tạo sẵn qua `seed_full.py`):

| Vai trò | Tên đăng nhập (Username) | Mật khẩu (Password) | Quyền hạn / Dữ liệu demo có sẵn |
|---|---|---|---|
| **Admin** | `admin` | `admin1` | Toàn quyền quản trị tài khoản, danh mục, cấu hình hệ thống & xem Audit Log |
| **Thủ thư** | `librarian` | `librarian1` | Quản lý kho sách, duyệt mượn/trả, gia hạn sách, thu điểm phạt quá hạn |
| **Độc giả 1** | `docgia1` | `docgia1` | Đã liên kết hồ sơ DG001 (có sẵn lịch sử mượn sách & phiếu phạt để test) |
| **Độc giả 2** | `docgia2` | `docgia2` | Đã liên kết hồ sơ DG002 |
| **Độc giả vãng lai** | `reader` | `reader1` | Độc giả mới |

---

## 5. Tự kiểm tra & Chạy Test tự động (Verification)

Để xác nhận toàn bộ hệ thống hoạt động chính xác theo tiêu chí chấm điểm:

1. **Kiểm tra nghiệp vụ Backend (111 unit tests tại Backend/tests/ & 118 tests tại qa/backend/):**
   ```powershell
   pytest tests/ -v
   ```
2. **Kiểm tra luồng RAG của Chatbot AI:**
   ```powershell
   python ..\chatbotAI\test_rag_full.py
   ```
3. **Kiểm tra lớp bảo vệ chống câu hỏi lạc đề / ngoài phạm vi thư viện:**
   ```powershell
   python ..\chatbotAI\test_chan_lac_de.py
   ```
