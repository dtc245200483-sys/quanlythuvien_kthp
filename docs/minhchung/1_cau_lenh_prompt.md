# Minh chứng 2.9 (Phần 1): Các câu lệnh (Prompt) gửi cho AI

Trong suốt quá trình phát triển dự án từ ngày 09/08 đến 31/08, tôi không sử dụng AI như một công cụ sinh mã ngẫu nhiên. Thay vào đó, tôi đóng vai trò là **Kiến trúc sư phần mềm**, sử dụng các Prompt (Câu lệnh) có tính kỹ thuật cao để định hướng, ép buộc AI tuân thủ nghiêm ngặt các quy tắc nghiệp vụ, bảo mật và trải nghiệm người dùng của dự án.

Dưới đây là 18 Prompt tiêu biểu (được sắp xếp theo đúng trình tự thời gian) thể hiện rõ năng lực điều khiển AI của tôi:

## GIAI ĐOẠN 1: KHỞI TẠO NỀN TẢNG & PHÂN QUYỀN (09/08/2026)

### 1. Prompt khởi tạo Backend Agent (09/08)
> *"BẮT BUỘC: 1. Không cho mượn khi sách còn = 0, số lượng không âm. 2. Tự động tính phạt trễ hạn. 3. Đặt trước chỉ áp dụng khi sách hết. 4. Phân quyền chặt: độc giả không gọi được API quản trị. 5. API cấp cho AI Engine PHẢI lọc bỏ dữ liệu cá nhân. 6. Có unit test. 7. Mọi thay đổi schema phải có migration."*

### 2. Prompt khởi tạo Frontend Agent (09/08)
> *"PHẠM VI: Chỉ code trong thư mục Frontend. Công nghệ: HTML‑CSS‑JS thuần, không dùng framework nặng. BẮT BUỘC: 1. Khi Backend chưa có API, dùng dữ liệu mock tạm và ghi rõ chỗ sẽ nối API. 2. Phân quyền ở màn hình: độc giả không nhìn thấy chức năng quản trị. 3. Hiển thị rõ lỗi API: sách hết, thẻ khóa, quá hạn."*

### 3. Prompt phân quyền Admin vs Librarian (09/08)
> *"Tuyệt đối không gộp chung quyền Admin và Librarian. Hệ thống phải có ranh giới rõ ràng: 4 nhóm quyền admin-only (quản lý tài khoản thủ thư, cấu hình tham số, cấu hình AI, audit log). Sinh ngay bảng AuditLog để giám sát Admin."*

### 4. Prompt thiết kế nghiệp vụ Mượn/Trả (09/08)
> *"Khi viết API POST /api/borrows, phải rào đủ các điều kiện: 1. Độc giả đang hoạt động. 2. Sách còn > 0. 3. Không vượt `max_books_at_once`. 4. `han_tra` = `ngay_muon` + `max_borrow_days`."*

### 5. Prompt xử lý chống Spam Request (09/08)
> *"Hệ thống bị lỗi HTTP 409 Conflict do độc giả bấm gửi yêu cầu 2 lần liên tiếp. Viết hàm JS tự động sinh mã UUID giả lập gắn vào payload để chống trùng lặp request."*

### 6. Prompt thiết kế hệ thống Đặt trước sách (09/08)
> *"Chức năng đặt trước sách: chỉ được đặt khi sách ĐÃ HẾT. Nếu sách còn → trả 400. Khi trả sách, nếu có ai đặt trước → tự động chuyển trạng thái sang SAN_SANG. Chặn gia hạn nếu sách có đặt trước."*

### 7. Prompt chuyển phạt tiền sang điểm SVNET (09/08)
> *"Đổi toàn bộ hệ thống phạt từ TIỀN sang TRỪ ĐIỂM SVNET. Công thức: 1 ngày quá hạn = 2 điểm. Mỗi độc giả khởi tạo 100 điểm. Migration phải chuyển đổi dữ liệu cũ chính xác."*

---

## GIAI ĐOẠN 2: HOÀN THIỆN UX/UI & VALIDATION (10/08 - 27/08/2026)

### 8. Prompt xác thực dữ liệu nghiêm ngặt (10/08)
> *"Yêu cầu validation: Họ tên ≥ 2 từ. Email bắt buộc đuôi @ictu.edu.vn. SĐT phải theo chuẩn định dạng Việt Nam. Trùng email trả về lỗi 409. Bổ sung Regex chặn từ Frontend đến Backend."*

### 9. Prompt thiết kế Dropzone kéo thả ảnh bìa (27/08)
> *"Bỏ thẻ input file mặc định. Tạo khu vực Dropzone hỗ trợ kéo thả (dragover, dragleave, drop). Dùng FileReader để Preview ảnh bìa ngay lập tức khi người dùng thả ảnh vào."*

### 10. Prompt chuẩn hóa định dạng mã sinh viên DTC (27/08)
> *"Mã sinh viên phải bắt đầu bằng 'DTC' + 9 chữ số. Giảng viên: 'GV' + 4 chữ số. Bổ sung Regex bắt lỗi (Inline Validation) hiển thị chữ đỏ dưới ô nhập."*

### 11. Prompt điều khiển AI Engine (Trợ lý ảo) (27/08)
> *"PROMPT TEMPLATE BẮT BUỘC DÙNG LÀM GỐC: System: 'Bạn là trợ lý tra cứu thư viện. Chỉ gợi ý sách có trong dữ liệu được cung cấp. Không bịa mã sách.' BẮT BUỘC: Không gửi dữ liệu cá nhân độc giả cho AI. Có test case cho câu hỏi mơ hồ."*

---

## GIAI ĐOẠN 3: XÂY DỰNG DỮ LIỆU LỚN & PHÂN TRANG (28/08/2026)

### 12. Prompt chuẩn hóa và thay máu CSDL Sách thật (28/08)
> *"Quy tắc import 64 sách: Kiểm tra bảng Thể loại, chưa có thì tạo mới. Kiểm tra sách trùng tên trước khi thêm, không tự động ghi đè. Số lượng mặc định 5 nếu chưa có. KHÔNG bịa thêm sách ngoài danh sách cung cấp."*

### 13. Prompt thuật toán sinh ID tự động theo tiền tố (28/08)
> *"Viết hàm Python trích xuất chữ cái đầu của mỗi từ trong `ten_sach` để làm tiền tố (Acronym), sau đó cộng với bộ đếm tăng dần 4 chữ số (VD: Bóng Ma Trên Mạng -> BMTM0005). Bộ đếm global, không reset theo thể loại."*

### 14. Prompt viết lại kiến trúc Phân trang (28/08)
> *"Tải 64 sách 1 lần sẽ sập trình duyệt. Viết lại API /api/books ở Backend hỗ trợ `skip` và `limit`. Ở Frontend, vẽ thanh Pagination và đồng bộ trạng thái `currentPage` vào URL."*

---

## GIAI ĐOẠN 4: KTR2 - KIẾN TRÚC MULTI-COPY & SỬA LỖI (30/08 - 31/08/2026)

### 15. Prompt đập đi xây lại CSDL sang bản vật lý (30/08)
> *"Độc giả có thể mượn 3 tài liệu giống nhau, nhưng mỗi quyển phải có 1 ID riêng (Multi-copy) để kiểm soát hư hỏng. Đập đi xây lại bảng BorrowDetails, gỡ khóa chính cũ và lập khóa chính mới `(ma_phieu, copy_id)`. Dùng row-level locking chống xung đột."*

### 16. Prompt sửa xung đột Khóa ngoại SQL Server (30/08)
> *"SQL Server chặn Drop PK khi còn dính FK. Bỏ dùng SQL chay đi. Viết script Python dùng `pyodbc` kết hợp Raw SQL thực hiện quy trình: 1. Drop Constraint FK -> 2. Drop PK cũ -> 3. Add cột copy_id -> 4. Make New PK -> 5. Re-add Constraint FK."*

### 17. Prompt rào lỗi IntegrityError khi xóa sách (30/08)
> *"Cấm can thiệp DB schema `ON DELETE CASCADE`. Phải kiểm soát bằng Application Layer. Sửa hàm DELETE, đếm và xóa thủ công tất cả `BookCopies` của sách đó trước, sau đó mới xóa `Book`."*

### 18. Prompt sửa vị trí hàng đợi Đặt trước (31/08)
> *"Cột Vị trí đặt trước đang hiện dấu `-` dù sách đã sẵn sàng. Kiểm tra và sửa cả Backend (hàm đếm `queue_pos` bỏ quên trạng thái SAN_SANG) và Frontend (lọc mất dữ liệu API). Sửa cả 2 đầu ngay lập tức."*

---

## GIAI ĐOẠN 5: KT3 - HOÀN THIỆN RAG CHATBOT & QUẢN TRỊ NỘI DUNG AI (15/09 - 16/09/2026)

### 19. Prompt bổ sung ô nhập Tóm tắt nội dung sách cho Thủ thư (16/09)
> *"Ở tài khoản thủ thư chưa có phần nhập nội dung tóm tắt sách trong modal Thêm/Sửa sách (`books.html`). Bổ sung ngay ô `<textarea id="book-tomtat" name="tomTat">` chiếm full-width (2 cột) trong modal, cập nhật hàm `openForm` trong `books.js` để tự động điền tóm tắt cũ khi sửa, đảm bảo gửi lên API `POST/PUT /api/books` và kích hoạt hàm `_dong_bo_sach_len_vs` cập nhật tự động vào ChromaDB Vector Store."*

### 20. Prompt sửa lỗi gợi ý thể loại / Quick Pills của Chatbot AI (26/09)
> *"Khi bấm vào các nút gợi ý nhanh như '📚 Sách Kinh tế & Quản trị', '💻 Sách Lập trình & CNTT', '🤖 Sách Trí tuệ nhân tạo & AI', '🔒 Sách An ninh mạng & Bảo mật', '🗣️ Sách Kỹ năng & Giao tiếp', '⭐ Sách hay & Đáng đọc nhất' thì Chatbot lại báo không tìm thấy sách. Kiểm tra lại toàn bộ luồng RAG: mở rộng từ khóa thể loại trong `rag_retriever.py`, loại bỏ các icon emoji/từ đệm trước khi tính fuzzy match, và rào bộ lọc tên sách ở `chatbot_service.py` để không xóa nhầm sách khi người dùng tìm kiếm theo danh mục."*

### 21. Prompt truy vết và sửa lỗi liên kết tài khoản độc giả & thông báo (26/09)
> *"Tại sao khi đăng nhập tài khoản độc giả lại bị lỗi 'Tài khoản chưa liên kết với độc giả' và 'Không thể tải thông báo'? Kiểm tra bảng Users và Readers trong CSDL, sửa lỗi liên kết cho tài khoản reader với độc giả có sẵn, đồng thời cập nhật script seed_full.py và kiểm tra luồng đăng ký tài khoản mới để đảm bảo không còn ai bị lỗi mồ côi reader_id nữa."*

### 22. Prompt điều tra tận gốc và chuẩn hóa 5 cuốn/đầu sách toàn thư viện (27/09)
> *"Xem vì sao không có ai mượn sách mà trong dữ liệu cuốn '50 Cuốn Sách Kinh Điển Về Kinh Doanh' lại chỉ còn 1 quyển. Xem lại tất cả, nếu có lỗi sai thì sửa chứ không được tự tiện thêm lại 4 quyển thành 5 quyển. Kiểm tra cả các sách khác nữa. Có phải do di chứng kiểm thử từ trước để lại không? Sau khi làm rõ, chuẩn hóa lại toàn bộ danh mục để mỗi sách đều có đủ 5 cuốn."*

### 23. Prompt tái cấu trúc thư mục Docker và khắc phục lỗi tắt phụt cửa sổ (27/09)
> *"Tại sao sau khi dừng docker xong tôi nhấn vào file 1_chay_docker.bat thì nó tự bị tắt phụt đi? Sửa lại script sao cho khi nhấn vào là tự bật web lên. Đồng thời gom toàn bộ các file Docker (Dockerfile, docker-compose.yml, .dockerignore) vào thư mục docker/ sao cho gọn gàng thư mục gốc và web vẫn hoạt động bình thường 100% không bị lỗi dữ liệu."*


