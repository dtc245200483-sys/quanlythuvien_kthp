# 5. Toàn bộ nhật ký và timeline minh chứng

## Mục tiêu

Cung cấp một **bản tổng hợp đầy đủ** các nhật ký (log), prompt, phản hồi AI và các lần chỉnh sửa do sinh viên thực hiện, từ **khi khởi tạo dự án** đến **phiên bản hiện tại**. Các tài liệu này sẽ được dùng làm minh chứng cho việc sử dụng AI trong quá trình phát triển phần mềm, đáp ứng yêu cầu **KT2** và **KT9**.

## Nguồn dữ liệu

- **Thư ký (thuky)**: `D:\ung dung tri tue nhan ao\app\thuky\changelog_tong.md` – chứa toàn bộ log thời gian thực (hơn 700 dòng), bao gồm log tự phát hiện (PHÁT HIỆN TỪ QUÉT) và log tự báo cáo (FRONTEND / BACKEND).  
- **Prompt**: các file trong `Backend/AGENTS.md`, `Frontend/AGENTS.md`, `AI_Engine/AI.txt` – được trích xuất trong **Phần 1**.
- **Mã nguồn AI sinh ra**: các đoạn code được trích xuất trong **Phần 2** và **Phần 3**.
- **Các chỉnh sửa do sinh viên thực hiện**: được mô tả chi tiết trong **Phần 4**.

## Cách đọc

1. Mở `changelog_tong.md` → duyệt theo thứ tự thời gian (mốc `2026-08-09` → `2026-08-31`).
2. Các mục được đánh dấu `PHÁT HIỆN TỪ QUÉT` là **phát hiện tự động** của Thư ký, chưa có log chính thức.
3. Các mục `LOG` (ví dụ `[BACKEND] 2026-08-09 08:06:16`) là **log do Agent tự báo cáo** – đây là bằng chứng chính.
4. Các mục `GHI CHÚ THƯ KÝ` và `TRỢ LÝ GHI` mô tả các **hành động người dùng** (sửa lỗi, tạo file, đồng bộ prompt, v.v.).

## Tổng quan timeline (đánh dấu các mốc quan trọng)

| Ngày | Thành phần | Mô tả ngắn | Vai trò của Tôi |
|------|------------|-------------|-----------------|
| 09/08 06:28 | Khởi tạo Prompt & Agent | Tạo `Backend/AGENTS.md`, `Frontend/AGENTS.md`, `AI_Engine/AI.txt` | Viết 3 bộ Prompt điều khiển |
| 09/08 06:46–07:02 | Frontend + Backend v0.1 | Tạo giao diện Đăng nhập + CRUD Sách, API đầu tiên | Kiểm duyệt API docs |
| 09/08 08:06 | Phân quyền Admin vs Librarian | 4 nhóm quyền admin-only, bảng AuditLog | Ra lệnh bóc tách quyền |
| 09/08 09:49–10:43 | Chức năng 3-5 hoàn thiện | Quản lý Độc giả, Mượn/Trả, Tra cứu | Review & bắt lỗi logic |
| 09/08 17:35–19:34 | Chức năng 6-8 | Đặt trước, Thống kê, Xuất CSV | Chỉ đạo nghiệp vụ FIFO |
| 09/08 19:50–20:15 | Demo data + Thu phạt + Xóa lịch sử | Seed data, UC19, Xóa yêu cầu đã xử lý | Yêu cầu seed idempotent |
| 09/08 21:52–23:16 | Phạt điểm SVNET + Sắp xếp sách | Chuyển phạt tiền → điểm, sort/order | Đặt quy tắc phạt 2đ/ngày |
| 10/08 02:15–02:56 | Hồ sơ cá nhân + Validation + Email DTC | Profile, avatar, Regex chuẩn Việt Nam | Ép email @ictu.edu.vn |
| 10/08 03:07–03:59 | Phân quyền quản lý độc giả | Librarian chỉ khoá thẻ, Admin toàn quyền | Bóc tách quyền lần 2 |
| 10/08 04:52–05:22 | DAT_TRUOC + Export reservations | Loại yêu cầu mới, CSV đặt trước | Thiết kế luồng yêu cầu |
| 10/08 05:48–06:45 | Bỏ CSV thống kê + Bỏ hậu tố UC | Dọn rác UI, disable nút gửi khi chưa chọn sách | Ra lệnh xóa tính năng thừa |
| 27/08 | UI/UX nâng cao | Inline Validation, Dropzone ảnh bìa, mã DTC | Chê AI, bắt sửa UX |
| 28/08 | Chuẩn hóa CSDL Sách | Nhập 64 sách thật, phân trang, sửa ID trùng | Bắt lỗi thuật toán AI |
| 29/08 | Dọn dẹp & Tối ưu mã nguồn | Xóa script rác, rà soát toàn bộ | Đóng vai QA |
| 30/08 | Kiến trúc Multi-copy (BookCopy) | Đập đi làm lại quản lý bản vật lý | Điều hướng kiến trúc CSDL |
| 30/08 | Xung đột FK + IntegrityError | Giải quyết khóa ngoại SQL Server | Viết quy trình migration |
| 30/08 | 111 Unit Tests + QA toàn diện | Test 3 quyền, push GitHub master | Nghiệm thu & duyệt push |
| 31/08 | Sửa Queue Position + Khôi phục tồn kho | Vị trí hàng đợi + bản copy bị test phá | Debug & lệnh khôi phục DB |
| 15/09–16/09 | Tích hợp RAG AI & Lưu lịch sử liên trang | DeepSeek LLM, ChromaDB, sessionStorage, modal Tiếng Việt | Kiến trúc sư AI & kiểm toán 10 tiêu chí KT3 |
| 16/09 | Bổ sung nhập Tóm tắt sách (tomTat) | Thêm textarea trong modal Quản lý sách, nạp/lưu tự động và đồng bộ ChromaDB | Phát hiện thiếu sót & chỉ đạo AI bổ sung |
| 26/09 | Kiểm toán toàn diện 20 tiêu chí KT3 & Căn chỉnh Docker Compose | Dockerfile, docker-compose đa dịch vụ (SQL Server + FastAPI + ChromaDB), scripts chạy 1-click | Tổ chức kiểm thử & nghiệm thu 20/20 tiêu chí |
| 26/09 | Fix liên kết Độc giả & Lỗi API Thông báo 500 | Users.reader_id = 'DG003', seed_full.py, /api/auth/register, /api/notifications/my | Bắt lỗi phân quyền & tài khoản mồ côi |
| 26/09–27/09 | Fix Chatbot Quick Category Pills (False Negative) | rag_retriever.py exact category match, hybrid boost, chatbot.html data.ket_qua | Debug RAG retrieval & xử lý lỗi logic UI |
| 27/09 | Chuẩn hóa kho sách vật lý 5 cuốn/đầu sách (315 cuốn) | BookCopies, Books.soLuong = 5, books_catalog.json, books_data.txt, ChromaDB sync | Audit dữ liệu kho sách & chỉ đạo chuẩn hóa |
| 27/09 | Quy hoạch thư mục Docker & nâng cấp 1-click startup | Di chuyển Docker vào docker/, name: app bảo toàn volume, run_docker.ps1 chờ SQL & auto mở web | Tối ưu đóng gói triển khai & UX khởi chạy |
| 28/10 | Chuẩn hóa Thể loại & NXB 63 cuốn sách thực tế | Xóa 9 thể loại & 6 NXB rác, thêm 5 thể loại chuẩn UTF-8, gán theLoaiId cho 39 sách bị NULL | Rà soát toàn vẹn CSDL trước bảo vệ đồ án |
| 28/10 | Thanh lọc 85 sách giả lập (TEST...) trong ChromaDB | Xóa sạch 85 vector rác sinh ra từ Unit Test, đồng bộ chuẩn 63 vector sách thật | Audit Vector Store & chất lượng phản hồi AI |
| 28/10 | Sửa lỗi Microsecond hàng đợi Đặt trước | Thuật toán index-based ranking, tie-breaker ma_dat trong reservations.py | Bắt lỗi precision mismatch SQL Server vs Python |
| 28/10 | Bổ sung cột Vị trí & Chặn chen hàng cho Thủ thư | Thêm cột Vị trí trên reservations.html/js, nút Chờ lượt, chốt chặn FIFO trong fulfill_reservation | Thiết kế trải nghiệm công bằng & bảo vệ luồng FIFO |

## Thống kê tổng quan

| Chỉ số | Giá trị |
|--------|---------|
| Tổng số log trong changelog | ~700 dòng |
| Tổng số migration (schema versioning) | 14 file |
| Tổng số Unit Test | 111 unit tests (Backend/tests/) + 118 tests (qa/backend/) (PASS 100%) |
| Số lần AI sinh code sai phải sửa | 32 lần (xem Phần 4) |
| Số Prompt phức tạp được ghi nhận | 27 lệnh (xem Phần 1 & Phần 2) |
| Số đoạn code AI sinh được lưu vết | 20 đoạn (xem Phần 2) |
| Số đoạn code giữ nguyên | 11 đoạn (xem Phần 3) |
| Số commit Git | Đã push lên master (qlsachkn3) |

## Liên kết tới các phần chi tiết

- **Phần 1 – Prompt**: `1_cau_lenh_prompt.md`
- **Phần 2 – Phản hồi AI & source code**: `2_phan_hoi_ai_code.md`
- **Phần 3 – Code gốc (không chỉnh)**: `3_code_dung_nguyen.md`
- **Phần 4 – Code tự chỉnh sửa**: `4_code_chinh_sua.md`
- **Phần 5 – Toàn bộ timeline**: *(tệp hiện tại)*

---

*File này được cập nhật bổ sung ngày 2026-10-28 để phản ánh đầy đủ các đợt chuẩn hóa dữ liệu CSDL SQL Server, thanh lọc ChromaDB Vector Store và hoàn thiện cơ chế hàng đợi FIFO đặt trước phục vụ bảo vệ đồ án.*
