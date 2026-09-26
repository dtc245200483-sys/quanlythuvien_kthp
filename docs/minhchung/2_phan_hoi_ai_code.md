# Minh chứng 2.9 (Phần 2): Nghệ thuật viết Prompt & Phản hồi mã nguồn của AI

Mục đích của phần minh chứng này là khẳng định: **"Chất lượng code do AI sinh ra tỷ lệ thuận với chất lượng của Prompt (Câu lệnh) do con người thiết kế"**. 

Tôi không sử dụng các Prompt chung chung ngây ngô kiểu *"Viết cho tôi trang quản lý sách"*. Thay vào đó, tôi sử dụng các kỹ thuật Prompt kỹ sư (Prompt Engineering) nâng cao như **Zero-shot, Few-shot, Chain-of-Thought** để cung cấp rõ ngữ cảnh, ràng buộc dữ liệu và thuật toán, từ đó ép AI sinh ra mã nguồn chất lượng cao.

Dưới đây là tiến trình thời gian thực (Chronological Timeline) ghi nhận các Prompt phức tạp của tôi và cách AI phản hồi:

## GIAI ĐOẠN 1: THIẾT KẾ KIẾN TRÚC & PHÂN QUYỀN (09/08/2026)

### 1. Prompt khởi tạo kiến trúc Backend Agent
**Prompt (Lệnh) của tôi:**
> *"BẮT BUỘC: 1. Không cho mượn khi sách còn = 0, số lượng không âm. 2. Tự động tính phạt trễ hạn. 3. Đặt trước chỉ áp dụng khi sách hết. 4. Phân quyền chặt: độc giả không gọi được API quản trị. 5. API cấp cho AI Engine PHẢI lọc bỏ dữ liệu cá nhân. 6. Có unit test. 7. Mọi thay đổi schema phải có migration."*

**Phản hồi của AI (07:02):** AI tạo ra `api_docs.md v0.1.0` với endpoints `login`, `books CRUD`, kèm migration 0001. Nhờ Prompt rõ ràng, AI không tự ý thêm logic lạ mà tuân thủ đúng 7 điều luật.

### 2. Prompt ép ranh giới quyền lực (Admin vs Librarian)
**Prompt (Lệnh) của tôi (08:06):**
> *"Tuyệt đối không gộp chung quyền Admin và Librarian. Hệ thống phải có ranh giới rõ ràng: 4 nhóm quyền admin-only (quản lý tài khoản thủ thư, cấu hình tham số, cấu hình AI, audit log). Sinh ngay cho tôi bảng AuditLog để giám sát Admin."*

**Phản hồi của AI (`Backend/app/models.py`):**
AI hiểu rõ ràng buộc bảo mật và tự động sinh ra cấu trúc theo dõi vết:
```python
# AI tự động sinh bảng AuditLog để giám sát Admin theo lệnh
class AuditLog(Base):
    __tablename__ = "audit_log"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True)
    action = Column(NVARCHAR(255), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
```

### 3. Prompt nghiệp vụ Mượn/Trả phức tạp (10:27)
**Prompt (Lệnh) của tôi:**
> *"Khi viết API POST /api/borrows, phải rào đủ các điều kiện: 1. Độc giả phải đang hoạt động. 2. Sách phải còn > 0. 3. Không vượt quá `max_books_at_once`. 4. `han_tra` = `ngay_muon` + `max_borrow_days`. Bắt đầu code."*

**Phản hồi của AI (`Backend/app/routers/borrows.py`):**
AI dịch hoàn hảo 4 điều kiện nghiệp vụ sang code Python:
```python
if current_borrows_count + len(borrow_in.book_ids) > config.max_books_at_once:
    raise HTTPException(status_code=400, detail="Vượt quá số lượng sách được mượn tối đa")

for book in books:
    if book.soLuongKhaDung <= 0:
        raise HTTPException(status_code=400, detail=f"Sách {book.ten_sach} đã hết")
    book.soLuongKhaDung -= 1
```

### 4. Prompt chống Spam Request (18:07)
**Prompt (Lệnh) của tôi:**
> *"Hệ thống bị lỗi HTTP 409 Conflict do độc giả bấm gửi yêu cầu 2 lần liên tiếp. Viết một hàm JS tự động sinh mã UUID giả lập gắn vào payload để chống trùng lặp."*

**Phản hồi của AI (`frontend/js/requests.js`):**
```javascript
function generateRequestCode() {
    const randomNum = Math.floor(1000 + Math.random() * 9000);
    const timestamp = Date.now().toString().slice(-4);
    return `REQ-${timestamp}-${randomNum}`;
}
```

### 5. Prompt thiết kế hệ thống Đặt trước sách (19:02)
**Prompt (Lệnh) của tôi:**
> *"Chức năng đặt trước sách: chỉ được đặt khi sách ĐÃ HẾT. Nếu sách còn → trả 400. Khi trả sách, nếu có ai đặt trước → tự động chuyển trạng thái sang SAN_SANG. Chặn gia hạn nếu sách có đặt trước. Viết đúng quy trình."*

**Phản hồi của AI:** AI tạo migration 0007, bảng `DatTruoc` với filtered unique index chống đặt trùng. Tích hợp logic: trả sách → tự động đổi `CHO_XU_LY` → `SAN_SANG` cho người đặt kế tiếp. Test 50/50 PASS.

### 6. Prompt đổi phạt tiền sang Trừ điểm SVNET (21:52)
**Prompt (Lệnh) của tôi:**
> *"Đổi toàn bộ hệ thống phạt từ TIỀN sang TRỪ ĐIỂM SVNET. Công thức: 1 ngày quá hạn = 2 điểm. Mỗi độc giả khởi tạo 100 điểm. Migration phải chuyển dữ liệu cũ đúng."*

**Phản hồi của AI:** AI tạo migration 0011, đổi cột `so_tien` → `so_diem`, quy đổi dữ liệu cũ (`so_diem = so_ngay_qua_han × 2`), thêm `Readers.diem_svnet` mặc định 100. Test 86/86 PASS.

---

## GIAI ĐOẠN 2: HOÀN THIỆN UX/UI (10/08 - 27/08/2026)

### 7. Prompt xác thực nghiêm ngặt (10/08, 02:42)
**Prompt (Lệnh) của tôi:**
> *"Yêu cầu validation: Họ tên ≥ 2 từ. Email bắt buộc đuôi @ictu.edu.vn. SĐT phải theo chuẩn Việt Nam. Trùng email → 409."*

**Phản hồi của AI:** AI tạo module `validation.py` với Regex chuẩn Việt Nam (`^(0|\+84)(3|5|7|8|9)\d{8}$`), áp dụng cho cả register, profile, admin accounts. Test 86/86 PASS.

### 8. Prompt giao diện kéo thả ảnh bìa (27/08)
**Prompt (Lệnh) của tôi:**
> *"Bỏ thẻ input file mặc định. Tạo khu vực Dropzone hỗ trợ kéo thả (dragover, dragleave, drop). Dùng FileReader để Preview ảnh bìa ngay lập tức khi thả ảnh vào."*

**Phản hồi của AI:** AI tạo Dropzone UI với sự kiện drag-and-drop hoàn chỉnh, kết hợp API `POST /api/books/upload-cover` giới hạn 5MB.

### 9. Prompt chuẩn hóa mã sinh viên DTC (27/08)
**Prompt (Lệnh) của tôi:**
> *"Mã sinh viên phải bắt đầu bằng 'DTC' + 9 chữ số. Giảng viên: 'GV' + 4 chữ số. Bổ sung Regex vào cả Frontend và Backend."*

**Phản hồi của AI:** AI viết Regex validation ở cả 2 tầng, đảm bảo mã không bị nhập sai định dạng.

---

## GIAI ĐOẠN 3: XÂY DỰNG DỮ LIỆU LỚN (28/08/2026)

### 10. Prompt chuẩn hóa CSDL Sách (28/08)
**Prompt (Lệnh) của tôi:**
> *"Quy tắc: Kiểm tra bảng Thể loại đã có mã chưa, chưa có thì tạo mới. Kiểm tra sách trùng tên trước khi thêm. Mỗi sách sinh book_id theo quy tắc mã hiện có. Số lượng mặc định 5 nếu chưa có. KHÔNG bịa thêm sách ngoài danh sách."*

**Phản hồi của AI:** AI tạo 64 cuốn sách với mã viết tắt tự động từ tên, sinh BookCopy cho từng cuốn, đúng quy trình kiểm tra trùng lặp.

### 11. Prompt thuật toán sinh ID sách
**Prompt (Lệnh) của tôi:**
> *"Viết hàm Python trích xuất chữ cái đầu của mỗi từ trong `ten_sach` để làm tiền tố (Acronym), sau đó cộng với bộ đếm tăng dần 4 chữ số."*

**Phản hồi của AI (Script `update_book_ids.py`):**
```python
import re
def generate_acronym(title: str) -> str:
    words = re.sub(r'[^a-zA-ZÀ-ỹ\s]', '', title).split()
    acronym = ''.join(w[0].upper() for w in words if w)
    return acronym if acronym else 'BK'
```

---

## GIAI ĐOẠN 4: KIẾN TRÚC MULTI-COPY & HÀNG ĐỢI FIFO (30/08/2026)

### 12. Prompt cấu trúc lại toàn bộ CSDL sang Bản vật lý (30/08)
**Prompt (Lệnh) của tôi:**
> *"Độc giả có thể mượn 3 tài liệu giống nhau, nhưng mỗi quyển phải có 1 ID riêng (Multi-copy) để kiểm soát hư hỏng. Đập đi xây lại bảng BorrowDetails, gỡ khóa chính cũ `(ma_phieu, ma_sach)` và lập khóa chính mới `(ma_phieu, copy_id)`."*

**Phản hồi của AI:**
AI hiểu sự thay đổi mang tính cách mạng này (KTR2) và sinh ra:
1. Bảng `BookCopies` quản lý từng mã vạch (VD: `CNTT-A8F9B2-1`).
2. API dùng `row-level locking` (Khóa dòng) trong SQLAlchemy:
```python
# AI dùng with_for_update() để chống Race Condition theo lệnh của tôi
available_copies = db.query(BookCopy).filter(
    BookCopy.book_id == book.ma,
    BookCopy.status == "Có sẵn"
).with_for_update().limit(count).all()
```

### 13. Prompt sửa vị trí xếp hàng đặt trước (31/08)
**Prompt (Lệnh) của tôi:**
> *"Cột Vị trí đặt trước đang hiện dấu `-` dù sách đã sẵn sàng. Kiểm tra và sửa cả Backend (hàm đếm `queue_pos` phải bao gồm trạng thái SAN_SANG) và Frontend (`fieldMap` phải map trường `queue_position`)."*

**Phản hồi của AI:** AI sửa đúng cả 2 đầu: Backend bổ sung `SAN_SANG` vào điều kiện tính `queue_pos`, Frontend thêm trường `queue_position` vào `fieldMap`.

---

## GIAI ĐOẠN 5: KT3 - HOÀN THIỆN RAG CHATBOT & QUẢN TRỊ DỮ LIỆU (16/09/2026)

### 14. Prompt bổ sung trường Tóm tắt sách trong Modal Quản lý sách
**Prompt (Lệnh) của tôi:**
> *"Ở tài khoản thủ thư chưa có phần nhập nội dung tóm tắt sách trong modal Thêm/Sửa sách. Bổ sung ngay ô textarea trong modal Thêm/Sửa sách của `books.html`, kết nối hàm `openForm` trong `books.js` để tự nạp dữ liệu khi sửa, và đảm bảo lưu vào DB cũng như đồng bộ lên Vector Store."*

**Phản hồi của AI:**
AI đã thực hiện đúng trọn vẹn yêu cầu:
1. Thêm `<textarea id="book-tomtat" name="tomTat">` trong `Frontend/books.html` với định dạng `grid-column: 1 / -1`.
2. Cập nhật `Frontend/js/books.js`:
```javascript
// Đưa tomTat vào danh sách các trường được nạp tự động khi bấm Sửa sách
["ma", "ten", "tacGia", "theLoai", "nxb", "namXb", "soLuong", "anhBia", "tomTat"].forEach(
  function (key) {
    var input = form.elements[key];
    if (input) {
      input.value = (book[key] === null || book[key] === undefined) ? "" : book[key];
    }
  }
);
```
3. Backend tiếp nhận trường `tomTat` qua `BookBase` và tự động kích hoạt hàm đồng bộ Vector Store thời gian thực:
```python
_dong_bo_sach_len_vs(book, action="upsert")
```

### 15. Prompt mở rộng nhận diện Thể loại / Quick Pills cho Chatbot AI (26/09)
**Prompt (Lệnh) của tôi:**
> *"Khi người dùng click vào các nút gợi ý nhanh như '📚 Sách Kinh tế & Quản trị', '💻 Sách Lập trình & CNTT'... Chatbot bị lỗi False Negative trả về 0 sách. Mở rộng từ khóa thể loại trong `rag_retriever.py`, loại bỏ emoji và rào bộ lọc tên sách ở `chatbot_service.py`."*

**Phản hồi của AI:**
AI đã cập nhật thuật toán phát hiện thể loại và bypass bộ lọc tên sách khi câu hỏi là danh mục:
```python
# chatbotAI/chatbot_service.py: Bỏ qua lọc tên sách khắt khe nếu câu hỏi là tìm kiếm thể loại
cau_hoi_lower = cau_hoi.lower()
la_tim_the_loai = any(tk in cau_hoi_lower for tk in [
    "sách", "gợi ý", "tìm", "kinh tế", "quản trị", "lập trình", "cntt",
    "công nghệ", "trí tuệ nhân tạo", "ai", "bảo mật", "an ninh mạng",
    "kỹ năng", "giao tiếp", "đáng đọc", "sách hay", "thể loại", "chủ đề"
])
if la_tim_the_loai:
    co_the_la_ten_sach = False
```

### 16. Prompt sửa lỗi mồ côi tài khoản độc giả và thông báo (26/09)
**Prompt (Lệnh) của tôi:**
> *"Tại sao đăng nhập độc giả lại bị lỗi 'Tài khoản chưa liên kết với độc giả' và 'Không thể tải thông báo'? Kiểm tra và sửa lỗi liên kết trong CSDL, cập nhật seed_full.py và bảo đảm luồng đăng ký tự liên kết."*

**Phản hồi của AI:**
AI phát hiện trường `reader_id` của user `reader` bị `NULL`, tiến hành liên kết trực tiếp trong SQL Server và cập nhật seed:
```python
# Backend/scripts/seed_full.py: Gán sẵn reader_id = "DG003" cho tài khoản reader
("reader", "reader1", "Lê Minh Cường", "DTC245200503@ictu.edu.vn", "0900000003", "reader", "DG003"),
```

### 17. Prompt điều tra và chuẩn hóa 5 cuốn/mỗi đầu sách (27/09)
**Prompt (Lệnh) của tôi:**
> *"Kiểm tra vì sao sách '50 Cuốn Sách Kinh Điển Về Kinh Doanh' chỉ còn 1 cuốn và Combo Sửa chữa Ô tô còn 4 cuốn. Không được tự tiện thêm bừa khi chưa rõ nguyên nhân. Sau khi điều tra ra di chứng Unit Test, chuẩn hóa lại toàn bộ 63 cuốn sách đều có đủ 5 cuốn."*

**Phản hồi của AI:**
AI truy vết git log phát hiện lỗi đóng băng dữ liệu dở dang vào file seed. Sau đó tiến hành cập nhật:
```json
// Backend/scripts/books_catalog.json
{"ma": "5CSKDVKD0002", "ten": "50 Cuốn Sách Kinh Điển Về Kinh Doanh", ..., "soLuong": 5}
{"ma": "CSSCOTTCBDNC0011", "ten": "Combo Sách Sửa Chữa Ô Tô...", ..., "soLuong": 5}
```
Và bổ sung 5 bản sao vật lý còn thiếu vào SQL Server:
```sql
UPDATE Books SET soLuong = 5 WHERE ma IN ('5CSKDVKD0002', 'CSSCOTTCBDNC0011');
INSERT INTO BookCopies (copy_id, book_id, status) VALUES ('5CSKDVKD0002-C02', '5CSKDVKD0002', N'Có sẵn');
-- (+ C03, C04, C05 cho 5CSKDVKD0002 và C05 cho CSSCOTTCBDNC0011)
```

### 18. Prompt tái cấu trúc thư mục Docker và khắc phục lỗi tắt phụt cửa sổ (27/09)
**Prompt (Lệnh) của tôi:**
> *"Sửa lỗi 1_chay_docker.bat bị tắt phụt khi click đúp chuột, tự mở web http://localhost:8000/, và chuyển toàn bộ file Docker vào thư mục docker/ mà không bị lỗi dữ liệu hay mất volume."*

**Phản hồi của AI:**
AI tạo thư mục `docker/`, di chuyển `Dockerfile`, `docker-compose.yml`, `.dockerignore` với cấu hình bảo toàn volume:
```yaml
# docker/docker-compose.yml
name: app  # Đảm bảo giữ nguyên các volume app_mssql_data và app_chroma_data
services:
  backend:
    build:
      context: ..
      dockerfile: docker/Dockerfile
```
Và tạo kịch bản `run/run_docker.ps1` có Smart Wait Loop kiểm tra SQL Server và tự động mở trình duyệt web:
```powershell
# Chờ SQL Server sẵn sàng rồi mới nạp dữ liệu và mở web
Start-Process "http://localhost:8000/"
Read-Host "Nhấn phím Enter để đóng cửa sổ này (Hệ thống vẫn tiếp tục chạy ngầm)..."
```

---
**TỔNG KẾT PHẦN 2:**
Thông qua 18 minh chứng trải dài từ 09/08 đến 27/09, có thể thấy AI là một cỗ máy sinh code cực kỳ mạnh mẽ, **NHƯNG** nó chỉ phát huy sức mạnh khi được định hướng bởi các **Prompt có tư duy kỹ thuật cao** của con người. Prompt yếu = Code yếu. Prompt mạnh = Code mạnh.


