# Minh Chứng Kỹ Thuật: Vector Store, Embedding & Đồng Bộ Realtime (RAG)

---

## PHẦN A — XÂY DỰNG VECTOR STORE & EMBEDDING

### Prompt đã dùng
```text
Bạn là kỹ sư AI. Dự án nằm tại: D:\ung dung tri tue nhan tao\app

Hãy xây dựng lớp Vector Store cho hệ thống RAG tra cứu sách, dùng 
ChromaDB để lưu trữ và tìm kiếm embedding, kết hợp với module 
embedding_client.py đã có tại 
D:\ung dung tri tue nhan tao\app\chatbotAI\embedding_client.py

VỊ TRÍ FILE CẦN TẠO:
- D:\ung dung tri tue nhan tao\app\chatbotAI\vector_store.py
- D:\ung dung tri tue nhan tao\app\chatbotAI\index_sach.py
- D:\ung dung tri tue nhan tao\app\chatbotAI\vector_db\

[... phần còn lại xem nguyên văn prompt đã gửi cho AI ...]
```

### Phản hồi/Kết quả của AI

#### 1. Danh sách file đã tạo

| File | Mô tả |
|------|-------|
| `chatbotAI/vector_store.py` | Lớp `VectorStore` — ChromaDB PersistentClient, cosine distance |
| `chatbotAI/index_sach.py` | Script đồng bộ batch + demo dữ liệu giả lập 10 sách |
| `chatbotAI/vector_db/` | Thư mục lưu dữ liệu ChromaDB persistent (tự tạo khi chạy) |

#### 2. Cấu trúc lớp VectorStore

```python
class VectorStore:
    def __init__(self):
        """PersistentClient → lưu vào chatbotAI/vector_db/ (không mất khi restart)"""
        # Collection: "sach_thu_vien", metadata={"hnsw:space": "cosine"}

    def them_sach(ma_sach, ten_sach, tac_gia, tom_tat, the_loai, con_hang) -> None:
        """Upsert (thêm mới hoặc cập nhật) 1 sách. Embed tom_tat, fallback ten_sach."""

    def tim_kiem_ngu_nghia(cau_hoi, top_k=10) -> list[dict]:
        """Query cosine similarity. Trả về diem_tuong_dong = 1 - dist/2 ∈ [0,1]"""

    def xoa_sach(ma_sach) -> None:
        """Xóa 1 sách khi bị xóa khỏi CSDL chính."""

    def dem_so_luong() -> int:
        """Kiểm tra nhanh tổng số sách đã index."""
```

**ChromaDB metadata:** Lưu `ten_sach`, `tac_gia`, `the_loai`, `con_hang` (dưới dạng string vì ChromaDB không nhận bool). Trường `con_hang` được chuyển đổi lại khi đọc.

#### 3. Kết quả kiểm thử RAG Semantic Search thực tế

> [!NOTE]
> *Dữ liệu 10 cuốn sách giả lập dưới đây được ghi lại ở giai đoạn kiểm thử sơ khai của module. Ở phiên bản chính thức, toàn bộ dữ liệu đã được quét dọn sạch sẽ và thay thế hoàn toàn bằng 63 cuốn sách thực tế từ SQL Server (xem chi tiết ở file 06 và file 07).*

**Môi trường:** 10 sách giả lập đã index | ChromaDB 1.5.9 | paraphrase-multilingual-MiniLM-L12-v2

> **Lưu ý:** Tất cả câu hỏi test dùng từ KHÔNG TRÙNG chữ với tên sách hay tóm tắt, chứng minh hệ thống tìm theo nghĩa chứ không phải khớp ký tự.

##### 📌 Test 1: `"muốn học cách viết code cho người chưa biết gì"`
*Dùng "viết code" thay vì "lập trình", "chưa biết gì" thay vì "cơ bản"*

| # | Điểm tương đồng | Tên sách | Tình trạng |
|---|----------------|----------|-----------|
| 1 | **0.7790** | Lập trình Python từ cơ bản đến nâng cao | Còn hàng ✅ |
| 2 | 0.6594 | Trí tuệ nhân tạo: Tiếp cận hiện đại | Còn hàng |
| 3 | 0.6297 | Đắc nhân tâm | Còn hàng |

##### 📌 Test 2: `"sách giúp tôi kiếm tiền và quản lý túi tiền tốt hơn"`
*Dùng "túi tiền" thay vì "tài chính", "kiếm tiền" thay vì "làm giàu"*

| # | Điểm tương đồng | Tên sách | Tình trạng |
|---|----------------|----------|-----------|
| 1 | **0.7761** | Nghĩ giàu làm giàu | Còn hàng ✅ |
| 2 | 0.7172 | Cha giàu cha nghèo | Còn hàng ✅ |
| 3 | 0.6427 | Tắt đèn | Còn hàng |

##### 📌 Test 3: `"làm sao để chinh phục lòng người và được mọi người yêu quý"`
*Dùng "chinh phục lòng người" thay vì "giao tiếp", "đắc nhân tâm"*

| # | Điểm tương đồng | Tên sách | Tình trạng |
|---|----------------|----------|-----------|
| 1 | **0.7446** | Đắc nhân tâm | Còn hàng ✅ |
| 2 | 0.6815 | 7 Thói quen của người hiệu quả | **Hết hàng** |
| 3 | 0.6518 | Nghĩ giàu làm giàu | Còn hàng |

##### 📌 Test 4: `"khám phá vũ trụ và bí ẩn không gian bao la"`
*Dùng "bí ẩn không gian" thay vì "vũ trụ học", "thời gian"*

| # | Điểm tương đồng | Tên sách | Tình trạng |
|---|----------------|----------|-----------|
| 1 | **0.7946** | Lược sử thời gian | Còn hàng ✅ |
| 2 | 0.6114 | Số đỏ | Còn hàng |
| 3 | 0.6083 | Kiến trúc hệ thống phân tán | Hết hàng |

#### 4. Log đầu ra thực tế

```
  KẾT QUẢ ĐỒNG BỘ
  ✅ Thành công: 10/10 sách
  📚 Tổng trong DB: 10 sách
  ⏱  Tổng thời gian: 25268ms (batch embedding: 23419ms)
  Kiểm thử hoàn thành. RAG Semantic Search hoạt động đúng!
```

---

---

## PHẦN B — ĐỒNG BỘ VECTOR STORE REALTIME VỚI API

### Prompt đã dùng
```text
Bạn là kỹ sư backend Python. Dự án nằm tại: 
D:\ung dung tri tue nhan tao\app

Hệ thống quản lý sách (CRUD sách) đã có sẵn trong project — hãy TÌM 
ĐÚNG các endpoint API xử lý thêm/sửa/xóa sách hiện có, KHÔNG viết lại 
từ đầu, chỉ CHÈN THÊM logic đồng bộ Vector Store vào các hàm đã tồn tại.

[... nội dung đầy đủ như yêu cầu gốc ...]
```

### Phản hồi/Kết quả của AI

#### 1. Tên trường thực tế trong model `Book` (bảng `Books`)

| Trường model | Ý nghĩa | Ánh xạ sang VectorStore |
|---|---|---|
| `ma` | Mã sách (PK) | `ma_sach` |
| `ten` | Tên sách | `ten_sach` |
| `tacGia` | Tác giả | `tac_gia` |
| `tomTat` | Tóm tắt (nullable) | `tom_tat` |
| `theLoai` | Thể loại (text) | `the_loai` |
| `soLuong` | Số lượng → `soLuong > 0` | `con_hang` (bool) |

#### 2. Các file đã chỉnh sửa (KHÔNG tạo mới)

##### [MODIFY] [books.py](file:///D:/ung%20dung%20tri%20tue%20nhan%20ao/app/Backend/app/routers/books.py)

Hàm helper chèn thêm ở đầu file:
```python
def _dong_bo_sach_len_vs(book: Book, action: str = "upsert") -> None:
    """LUÔN trong try-except — lỗi VS không bao giờ ảnh hưởng CSDL chính."""
    try:
        from chatbotAI.vector_store import VectorStore
        vs = VectorStore()
        if action == "delete":
            vs.xoa_sach(book.ma)
        else:
            vs.them_sach(
                ma_sach=book.ma, ten_sach=book.ten, tac_gia=book.tacGia,
                tom_tat=book.tomTat or "", the_loai=book.theLoai or "",
                con_hang=book.soLuong > 0,
            )
    except Exception as vs_err:
        _vs_logger.warning(f"[VS_SYNC] ⚠️ {action.upper()} thất bại: {vs_err}")
```

Vị trí gọi:
- `create_book()` → sau `db.commit()`: `_dong_bo_sach_len_vs(book, "upsert")`
- `update_book()` → sau `db.commit()`: `_dong_bo_sach_len_vs(book, "upsert")`
- `delete_book()` → sau `db.commit()`: `_dong_bo_sach_len_vs(sach_da_xoa, "delete")`

##### [MODIFY] [borrows.py](file:///D:/ung%20dung%20tri%20tue%20nhan%20ao/app/Backend/app/routers/borrows.py)

```python
def _dong_bo_con_hang(book: Book) -> None:
    """Cập nhật con_hang trong VS khi soLuong thay đổi do mượn/trả."""
    try:
        from chatbotAI.vector_store import VectorStore
        vs = VectorStore()
        vs.them_sach(ma_sach=book.ma, ..., con_hang=book.soLuong > 0)
    except Exception as vs_err:
        _vs_logger.warning(f"[VS_SYNC] ⚠️ CON_HANG UPDATE thất bại: {vs_err}")
```

Vị trí gọi:
- `_perform_create_borrow()` → sau `db.commit()`: loop sách vừa mượn
- `_perform_return_borrow()` → sau `db.commit()`: loop sách vừa trả

##### [MODIFY] [admin.py](file:///D:/ung%20dung%20tri%20tue%20nhan%20ao/app/Backend/app/routers/admin.py)

Endpoint mới thêm vào cuối file:
```
POST /api/admin/dong-bo-vector-store   (Admin only)
→ Gọi dong_bo_toan_bo() với toàn bộ sách từ DB
→ Trả về {message, so_sach_tu_csdl, so_sach_trong_vs}
```

#### 3. Kết quả kiểm thử 4 bước realtime

**Sách test:** `[TEST_RT_001] Bí Quyết Nấu Phở Ngon`  
**Câu hỏi:** `"cách làm món ăn truyền thống Việt Nam"`

| Bước | Thao tác | Kết quả |
|:----:|:---------|:--------|
| 1 | `vs.them_sach('TEST_RT_001', ...)` | ✅ OK — 84ms |
| 2 | Tìm *"cách làm món ăn truyền thống Việt Nam"* | ✅ PASS — **#1 điểm 0.7616** (28ms) |
| 3 | `vs.xoa_sach('TEST_RT_001')` | ✅ OK — 11ms |
| 4 | Tìm lại câu hỏi trên | ✅ PASS — sách biến mất hoàn toàn (26ms) |

**Chi tiết Bước 2** — Top 5 sau khi thêm:

| # | Điểm | Mã | Tên sách |
|---|------|----|---------|
| ★1 | **0.7616** | TEST_RT_001 | **Bí Quyết Nấu Phở Ngon** ← đây rồi! |
| 2 | 0.7490 | VH002 | Tắt đèn |
| 3 | 0.7381 | VH001 | Số đỏ |
| 4 | 0.5705 | KN001 | Đắc nhân tâm |
| 5 | 0.5693 | KT001 | Nghĩ giàu làm giàu |

**Chi tiết Bước 4** — Top 5 sau khi xóa:

| # | Điểm | Mã | Tên sách |
|---|------|----|---------|
| 1 | 0.7490 | VH002 | Tắt đèn |
| 2 | 0.7381 | VH001 | Số đỏ |
| 3 | 0.5705 | KN001 | Đắc nhân tâm |
| 4 | 0.5693 | KT001 | Nghĩ giàu làm giàu |
| 5 | 0.5581 | KN002 | 7 Thói quen của người hiệu quả |

```
🎉 TẤT CẢ PASS — Đồng bộ realtime hoạt động đúng!
```

---

## Phần sinh viên đã kiểm tra/chỉnh sửa
- [x] **Kiểm tra luồng nhập liệu của Thủ thư (16/09/2026)**: Phát hiện trên màn hình Quản lý sách (`books.html`), modal "Thêm sách / Sửa sách" bị thiếu trường nhập `Tóm tắt nội dung sách` (`tomTat`), khiến sách mới thêm vào SQL Server không có nội dung ngữ cảnh để đồng bộ sang ChromaDB. Đã chỉ đạo bổ sung trường `<textarea name="tomTat">` trong `books.html`, nạp dữ liệu tự động trong `books.js` và xác nhận hàm `_dong_bo_sach_len_vs` cập nhật tức thì sang Vector Store.
- [x] **Chuẩn hóa kho sách vật lý & đồng bộ vector store (27/09/2026)**: Rà soát và chuẩn hóa toàn bộ 63 đầu sách về đúng 5 bản vật lý/đầu sách (`Books.soLuong = 5`, `BookCopies` đạt 315 bản sao ở trạng thái "Có sẵn"), đồng thời đồng bộ hóa metadata `con_hang: True` và ngữ cảnh tóm tắt sang ChromaDB vector collection `sach_thu_vien`.

---

## Ngày thực hiện
15/09/2026 10:44 (Cập nhật bổ sung: 16/09/2026; Chuẩn hóa kho sách: 27/09/2026)

