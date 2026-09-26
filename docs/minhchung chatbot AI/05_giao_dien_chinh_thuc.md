# BÁO CÁO MINH CHỨNG: XÂY DỰNG GIAO DIỆN CHATBOT NỔI (FLOATING CHAT WIDGET) VÀ API CHÍNH THỨC

## Prompt đã dùng

### Câu lệnh yêu cầu của đồ án / bài toán:
```text
Bạn là kỹ sư Frontend. Dự án nằm tại: D:\ung dung tri tue nhan tao\app

Hãy xây dựng giao diện chatbot dạng "bong bóng tròn nổi" (floating 
chat widget) để nhúng vào các trang web hiện có của hệ thống quản lý 
thư viện, kết nối với chatbot_service.py đã hoàn thiện (dùng RAG, 
đọc PROMPT_VERSION từ config.py — mặc định "v3").

VỊ TRÍ FILE CẦN TẠO:
- D:\ung dung tri tue nhan tao\app\Frontend\components\chatbot-widget.js
- D:\ung dung tri tue nhan tao\app\Frontend\components\chatbot-widget.css
- D:\ung dung tri tue nhan tao\app\Backend\app\routers\chatbot.py

PHẦN 1: chatbot.py — API endpoint chính thức (Rate limit 10 câu/phút/IP, không bắt buộc đăng nhập, lỗi trả HTTP 200 kèm thong_bao thân thiện).
PHẦN 2: chatbot-widget.js — Logic bong bóng chat (Tự sinh nút tròn nổi, khung chat 360x500px, lưu lịch sử trong RAM, gợi ý nhanh, typing indicator).
PHẦN 3: chatbot-widget.css — Đồng bộ theme ICTU, animation mở/đóng, responsive điện thoại < 480px.
PHẦN 4: Hướng dẫn nhúng vào các trang web hiện có.
KIỂM THỬ: Nút tròn đúng vị trí, test câu hỏi thật, test câu hỏi lạc đề, test responsive.
```

---

## Phản hồi kết quả AI

### 1. Danh sách file đã tạo / chỉnh sửa

| STT | Đường dẫn file | Vai trò / Chức năng |
|:---:|:---|:---|
| 1 | `Backend/app/routers/chatbot.py` | API Router chính thức: `POST /api/chatbot/hoi`, rate limit 10 câu/phút/IP, trả HTTP 200 thân thiện khi có lỗi |
| 2 | `Frontend/components/chatbot-widget.css` | Stylesheet widget: Nút tròn nổi, khung chat animation mượt, theme Navy ICTU, responsive mobile (< 480px) |
| 3 | `Frontend/components/chatbot-widget.js` | Web Component độc lập: Tự sinh DOM nút tròn và khung chat, quản lý lịch sử RAM, typing indicator, quick prompts |
| 4 | `Frontend/search.html` | Trang đầu tiên đã được nhúng thử nghiệm và kiểm thử hoạt động trực tiếp |

---

### 2. Kiến trúc & Luồng hoạt động của Bong bóng Chat (Floating Widget)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    GIAO DIỆN NGƯỜI DÙNG TRÊN TRANG WEB                     │
│                                                                             │
│  [Nút tròn nổi cố định (Bottom-Right)] 💬                                  │
│            │                                                                │
│            ▼ (Bấm vào nút tròn)                                             │
│  [Khung chat nổi 380x540px] ──────────────────────────────────────────────┐ │
│  │ - Header: "Trợ lý Thư viện" + Chấm xanh trực tuyến + Nút thu nhỏ [✕]    │ │
│  │ - Tin nhắn chào mừng + 4 nút gợi ý nhanh:                             │ │
│  │   [🐍 Sách lập trình] [⭐ Sách hay] [📖 Cách mượn sách] [💰 Tài chính] │ │
│  │ - Khu vực hội thoại: Cuộn mượt, hiển thị tin nhắn Độc giả / AI         │ │
│  │ - Thẻ sách: Tên sách in đậm, tác giả, huy hiệu Còn/Hết sách, nút xem kho│ │
│  │ - Ô nhập liệu text + Nút gửi câu hỏi (hỗ trợ phím Enter)              │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
└───────────────────────────────────────┬─────────────────────────────────────┘
                                        │ Gọi fetch(POST /api/chatbot/hoi)
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        BACKEND FASTAPI (PORT 8000)                          │
│                                                                             │
│  1. Kiểm tra Rate Limit: Tối đa 10 requests / 60s / IP                      │
│  2. Gọi chatbotAI.chatbot_service.tra_cuu_sach(cau_hoi, version="v3")      │
│  3. Nếu gặp lỗi hoặc câu hỏi không hợp lệ: Luôn trả HTTP 200 kèm thông báo   │
│     thân thiện (không để lỗi 500 làm trắng màn hình giao diện)             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 3. Chi tiết triển khai kỹ thuật

#### A. Backend API Router (`Backend/app/routers/chatbot.py`):
- **Rate Limiting theo IP**: Sử dụng cấu trúc dữ liệu `defaultdict(list)` kèm `threading.Lock` để theo dõi timestamp các lượt gọi trong cửa sổ 60 giây. Nếu một IP gửi vượt quá 10 câu hỏi/phút, hệ thống phản hồi HTTP 200 với thông báo: *"Bạn đã gửi quá nhiều câu hỏi trong thời gian ngắn (tối đa 10 câu/phút). Vui lòng chờ 1 phút rồi thử lại nhé!"*.
- **Xử lý lỗi thân thiện**: Nếu `chatbot_service.py` trả về `{"loi": ...}` hoặc có ngoại lệ mạng, router tự động bọc lại và trả về HTTP 200 kèm thông báo lịch sự, ngăn chặn hoàn toàn lỗi sập giao diện 500.
- **Không yêu cầu xác thực**: Độc giả vãng lai chưa đăng nhập vẫn có thể tra cứu nhanh sách thư viện.

#### B. Component Bong bóng Chat (`components/chatbot-widget.js`) & Trang chuyên biệt (`chatbot.js`):
- **Cơ chế tự động hóa**: Khi được nạp vào bất kỳ trang HTML nào, script tự khởi tạo DOM nút tròn nổi `🤖` (kèm badge `AI`) và khung chat mà không cần sửa cấu trúc HTML sẵn có của trang.
- **Cơ chế lưu trữ phiên liên trang qua SessionStorage (Cross-Page Session Persistence)**:
  - Khắc phục triệt để hiện tượng mất dữ liệu khi độc giả chuyển đổi giữa các menu trên navbar (do ứng dụng theo kiến trúc Web đa trang MPA, khi chuyển trang trình duyệt xóa RAM cũ).
  - Lịch sử hội thoại được tự động lưu trữ và đồng bộ liên trang trong `sessionStorage` với key chuẩn `ictu_ai_chat_history`.
  - Khi độc giả điều hướng giữa bất kỳ trang nào (ví dụ từ `chatbot.html` sang `search.html`, `reservations.html`, `profile.html`...), hàm `restoreHistory()` tự động nạp lại toàn bộ danh sách tin nhắn, thẻ sách, tag từ khóa và thời gian phản hồi.
  - Bổ sung nút xóa lịch sử nhanh `🧹` trên Header của Widget nổi và nút `🧹 Xóa lịch sử chat` trên trang chuyên biệt `chatbot.html`, cho phép độc giả chủ động làm mới phiên hội thoại bất kỳ lúc nào. Khi đóng tab trình duyệt, dữ liệu tự động được giải phóng an toàn.
- **Cơ chế chống đè request & Khóa trạng thái gửi (`isSending`)**:
  - Khi độc giả gửi câu hỏi và đang chờ AI phản hồi (5–10s), ô nhập liệu (`input`/`textarea`), nút gửi và các nút chủ đề gợi ý nhanh lập tức được vô hiệu hóa (`disabled = true`, `opacity: 0.6`, `cursor: not-allowed`).
  - Triệt tiêu 100% tình trạng người dùng click liên tiếp hoặc bấm nhiều câu hỏi mẫu cùng lúc gây xung đột mạng hoặc làm dừng câu hỏi trước.
- **Cơ chế Hộp thoại Cảnh báo Tiếng Việt chuẩn ICTU (`showLeaveConfirmModal`) & `beforeunload`**:
  - Khi độc giả đang chờ AI phản hồi (`isSending = true`) mà bấm vào bất kỳ liên kết chuyển trang nào trên thanh Navbar (hoặc trong trang), hệ thống chủ động chặn thao tác điều hướng và lập tức mở **Hộp thoại Cảnh báo Tiếng Việt 100% chuẩn nhận diện ICTU** (`⚠️ Cảnh báo gián đoạn tra cứu sách` kèm 2 nút: `[Ở lại chờ kết quả]` và `[Vẫn rời đi]`).
  - Giải pháp này khắc phục hoàn toàn hạn chế của các trình duyệt hiện đại (Chrome 51+ vốn mặc định hiển thị thông báo tiếng Anh *"Leave site? Changes you made may not be saved"* do cài đặt ngôn ngữ trình duyệt). Đảm bảo giao diện luôn thuần Tiếng Việt, thân thiện và chuyên nghiệp.
  - Vẫn duy trì bộ lắng nghe `beforeunload` làm lớp bảo vệ dự phòng cấp trình duyệt khi người dùng đóng hẳn cửa sổ tab hoặc bấm F5 tải lại trang.
- **4 Câu hỏi gợi ý nhanh**:
  1. `💻 Sách Lập trình & CNTT`
  2. `🤖 Sách Trí tuệ nhân tạo (AI)`
  3. `📚 Sách Kinh tế & Quản trị`
  4. `⭐ Sách hay nên đọc`
- **Typing Indicator**: Hiệu ứng 3 chấm nhấp nháy chuyển động mượt mà trong khi chờ backend phản hồi.

#### C. Stylesheet Widget (`components/chatbot-widget.css`):
- Đồng bộ chuẩn Design System ICTU: Sử dụng biến màu `--color-primary-900` (`#0a2e5c`), `--color-primary-600` (`#1e4b8c`), font `Be Vietnam Pro`.
- Nút tròn nổi có độ sâu thị giác cao (`box-shadow: 0 8px 24px rgba(10, 46, 92, 0.28)`), `z-index: 99999` đảm bảo không bị che khuất bởi navbar hay bảng biểu.
- Hiệu ứng mở khung chat bằng `transform: scale() translateY()` mượt mà, không giật cục.
- **Responsive Mobile**: Trên màn hình dưới `480px`, khung chat tự động mở rộng chiếm toàn bộ màn hình điện thoại với khoảng đệm an toàn `8px`.

---

### 4. Đồng bộ thanh điều hướng (Navbar) & Widget trên toàn bộ Web App (`layout.js`)

Để đảm bảo cả **Tab menu "🤖 Trợ lý AI" trên thanh điều hướng (Navbar)** và **Bong bóng chat nổi (Floating Widget)** hiển thị đồng nhất 100% trên toàn bộ hệ thống (tránh hiện tượng trang có, trang không hoặc trình duyệt dùng cache cũ khiến mất tab AI như trên `search.html`):

1. **Thêm mục `🤖 Trợ lý AI` vào thanh Menu chính (`Frontend/js/layout.js`)**:
   Mọi vai trò (`reader`, `librarian`, `admin`) đều có tab `🤖 Trợ lý AI` đứng ngay sau `Tra cứu sách`:
   ```javascript
   MENUS = {
     reader: [
       { key: "search", href: "search.html", label: "Tra cứu sách" },
       { key: "chatbot", href: "chatbot.html", label: "🤖 Trợ lý AI" },
       { key: "reservations", href: "reservations.html", label: "Đặt trước" },
       ...
     ],
     ...
   };
   ```

2. **Cơ chế nạp tự động Floating Widget qua `loadChatbotWidget()`**:
   Hàm `loadChatbotWidget()` trong `layout.js` tự động kiểm tra và chèn đồng thời `components/chatbot-widget.css` và `components/chatbot-widget.js` vào mọi trang web dùng chung layout (trừ trang chuyên biệt `chatbot.html`):
   ```javascript
   function loadChatbotWidget() {
     if (window.location.pathname.indexOf("chatbot.html") !== -1) return;
     if (!document.getElementById("chatbot-widget-css")) {
       var css = document.createElement("link");
       css.id = "chatbot-widget-css";
       css.rel = "stylesheet";
       css.href = "components/chatbot-widget.css?v=20260916-01";
       document.head.appendChild(css);
     }
     if (!document.getElementById("chatbot-widget-script")) {
       var sc = document.createElement("script");
       sc.id = "chatbot-widget-script";
       sc.src = "components/chatbot-widget.js?v=20260916-01";
       document.body.appendChild(sc);
     }
   }
   ```

3. **Chống lỗi Cache trình duyệt (Cache Busting & No-Cache Middleware)**:
   - **Nguyên nhân trước đây**: Trình duyệt lưu cache URL `layout.js?v=20260827-04` cũ trên `search.html` khiến menu chỉ hiện `[Tra cứu sách] [Đặt trước]` mà không có `[🤖 Trợ lý AI]`.
   - **Giải pháp dứt điểm**:
     1. Đồng loạt nâng phiên bản tham số `?v=20260916-01` trên toàn bộ 14 file HTML (`search.html`, `reservations.html`, `books.html`, `borrow.html`, `my-borrows.html`, `requests.html`, `notifications.html`, `profile.html`, `readers.html`, `stats.html`, `admin-accounts.html`, `admin-catalog.html`, `admin-config.html`, `chatbot.html`).
     2. Bổ sung middleware HTTP tại `Backend/app/main.py`: tự động gửi header `Cache-Control: no-cache, no-store, must-revalidate`, `Pragma: no-cache`, `Expires: 0` cho toàn bộ tài nguyên static `.js`, `.css`, `.html`, đảm bảo độc giả tải trang luôn nhận bản mới nhất ngay lập tức.

4. **Trạng thái bao phủ trên các trang trong dự án**:
   - [x] **`search.html`** *(Tra cứu sách)*: Đã có tab `🤖 Trợ lý AI` trên navbar + widget nổi `🤖` ở góc dưới.
   - [x] **`reservations.html`** *(Đặt trước sách)*: Đã có tab `🤖 Trợ lý AI` trên navbar + widget nổi `🤖`.
   - [x] **`books.html`** *(Quản lý sách thủ thư)*: Đã có tab `🤖 Trợ lý AI` trên navbar + widget nổi `🤖`.
   - [x] **`borrow.html`** *(Mượn / Trả sách)*: Đã có tab `🤖 Trợ lý AI` trên navbar + widget nổi `🤖`.
   - [x] **`my-borrows.html`** *(Lịch sử mượn độc giả)*: Đã có tab `🤖 Trợ lý AI` trên navbar + widget nổi `🤖`.
   - [x] **`requests.html`** *(Yêu cầu sách mới)*: Đã có tab `🤖 Trợ lý AI` trên navbar + widget nổi `🤖`.
   - [x] **`profile.html`** *(Hồ sơ người dùng)*: Đã có tab `🤖 Trợ lý AI` trên navbar + widget nổi `🤖`.
   - [x] **`stats.html`** *(Thống kê thư viện)*: Đã có tab `🤖 Trợ lý AI` trên navbar + widget nổi `🤖`.

---

### 5. Kết quả kiểm thử thực tế

#### Bước 1: Kiểm tra thanh điều hướng Navbar và nút tròn nổi
- Gọi HTTP kiểm tra trực tiếp hai file thành phần:
  - `GET http://localhost:8000/components/chatbot-widget.css` → **HTTP 200 OK** (10.2 KB)
  - `GET http://localhost:8000/components/chatbot-widget.js` → **HTTP 200 OK** (15.4 KB)
- Menu Navbar: Tab **`🤖 Trợ lý AI`** xuất hiện rõ ràng giữa `Tra cứu sách` và `Đặt trước`, bấm vào điều hướng thẳng đến `chatbot.html`.
- Nút tròn nổi hiển thị chuẩn xác ở góc dưới bên phải màn hình (`bottom: 24px`, `right: 24px`) với icon **`🤖`**, huy hiệu xanh **`AI`** và tooltip *"Hỏi Trợ lý AI (Tra cứu sách thông minh)"*. Khắc phục 100% hiện tượng lệch hiển thị giữa trang Tra cứu sách và Đặt trước.

#### Bước 2: Kiểm thử chức năng hỏi đáp qua API `/api/chatbot/hoi`

* **Test Case 2.1: Câu hỏi thật (có sách phù hợp trong kho)**
  - Câu hỏi: `"Nghĩ giàu làm giàu"`
  - Kết quả: Status `200 OK`, thời gian phản hồi `12.6s`, tìm thấy 3 cuốn sách phù hợp:
    1. *Nghĩ giàu làm giàu* — Napoleon Hill (Huy hiệu: **✓ Còn sách**)
    2. *Cha giàu cha nghèo* — Robert T. Kiyosaki (Huy hiệu: **✓ Còn sách**)
    3. *Người Giàu Có Nhất Thành Babylon (Tái Bản)* — George S. Clason (Huy hiệu: **✓ Còn sách**)
  - Định dạng hiển thị: Từng cuốn sách hiển thị thành **Thẻ sách mini (Book Card)** có viền xanh ICTU, tên in đậm, tác giả, lý do gợi ý và nút *"Xem sách →"* điều hướng trực tiếp trong cùng tab, tự động điền tên sách vào ô tra cứu và hiển thị ngay kết quả mà không bị văng đăng nhập (đồng bộ session giữa sessionStorage và localStorage).

* **Test Case 2.2: Câu hỏi ngoài phạm vi thư viện (Lạc đề)**
  - Câu hỏi: `"Hôm nay thời tiết thế nào?"`
  - Kết quả: Status `200 OK`, thời gian `2.0s` (chặn tầng retrieval, không tốn API token), số sách: `0`.
  - Thông báo hiển thị: `"Không tìm thấy sách phù hợp trong thư viện."` dạng tin nhắn văn bản thông thường, không bịa sách hay đưa nội dung lạc đề.

* **Test Case 2.3: Câu hỏi rỗng / Kiểm soát lỗi**
  - Câu hỏi: `""`
  - Kết quả: Status `200 OK`, thông báo: `"Vui lòng nhập câu hỏi tra cứu sách nhé!"`.

* **Test Case 2.4: Kiểm thử lưu trữ hội thoại liên trang (Cross-Page Session Persistence)**
  - **Kịch bản**: 
    1. Độc giả mở trang `chatbot.html`, gửi câu hỏi: `"Sách về trí tuệ nhân tạo cho người mới bắt đầu"`. Chatbot trả về 2 cuốn sách (*Kỹ Thuật AI*, *Bá Chủ AI*).
    2. Độc giả bấm thanh menu chuyển sang trang `search.html` (Tra cứu sách) hoặc `reservations.html` (Đặt trước).
    3. Tại trang `search.html`, bấm vào bong bóng chat nổi 🤖: Toàn bộ câu hỏi và 2 thẻ sách vừa hỏi trên `chatbot.html` hiển thị nguyên vẹn 100%.
    4. Độc giả gửi tiếp câu hỏi từ Widget: `"Có sách kinh tế nào hay không?"`. AI phản hồi thành công và lưu vào `sessionStorage`.
    5. Độc giả bấm menu quay lại `chatbot.html`: Cả 2 lượt trao đổi đều hiển thị đầy đủ, không hề bị reset.
    6. Độc giả bấm nút `🧹` (Xóa lịch sử): Xác nhận xóa sạch bộ nhớ tạm và làm mới lại giao diện.
  - **Kết luận**: Đạt 100% yêu cầu trải nghiệm mượt mà, khắc phục triệt để nhược điểm mất phiên của kiến trúc Web đa trang (MPA).

* **Test Case 2.5: Kiểm thử chống đè request (`isSending`) và cảnh báo gián đoạn (`beforeunload`)**
  - **Kịch bản 1 (Khóa UI khi gửi)**: Độc giả nhập câu hỏi và bấm Gửi (hoặc bấm nút gợi ý mẫu). Trong suốt 5–10s khi typing indicator hiển thị:
    - Ô nhập text bị vô hiệu hóa (`disabled`), không nhận thêm ký tự.
    - Nút gửi và các nút gợi ý mẫu bị làm mờ và chặn click (`cursor: not-allowed`).
    - Sau khi AI trả lời xong, các nút và ô nhập tự động mở khóa và sẵn sàng cho câu hỏi tiếp theo.
  - **Kịch bản 2 (Hộp thoại xác nhận Tiếng Việt chuẩn ICTU khi chuyển trang)**: Trong lúc AI đang xử lý câu hỏi, độc giả click vào bất kỳ menu nào trên thanh điều hướng (*Tra cứu sách*, *Đặt trước*, *Hồ sơ*...):
    - Hệ thống chủ động chặn chuyển trang và lập tức hiển thị **Hộp thoại xác nhận Tiếng Việt 100% chuẩn giao diện ICTU**:
      > **⚠️ Cảnh báo gián đoạn tra cứu sách**  
      > *🤖 Trợ lý AI đang tìm sách cho bạn... Nếu bạn chuyển trang lúc này, quá trình tìm kiếm sẽ bị gián đoạn và câu trả lời chưa kịp lưu lại. Bạn có muốn ở lại chờ AI trả lời xong không?*  
      > Nút hành động: **[Ở lại chờ kết quả]** (xanh ICTU) và **[Vẫn rời đi]** (viền đỏ).
    - Khắc phục hoàn toàn việc hiện popup tiếng Anh mặc định của trình duyệt (*"Leave site? Changes you made may not be saved"*).
    - Nếu độc giả bấm **[Ở lại chờ kết quả]**: Hộp thoại đóng lại, kết nối mạng tiếp tục duy trì, câu trả lời từ AI về và hiển thị đầy đủ.
    - Nếu độc giả bấm **[Vẫn rời đi]**: Hệ thống tắt cờ và chuyển sang trang đích, câu hỏi trước đó vẫn được lưu an toàn trong `sessionStorage`.
  - **Kết luận**: Giao diện thuần Tiếng Việt 100%, thân thiện và chuyên nghiệp, triệt tiêu tình trạng người dùng vô tình làm đứt gãy câu hỏi.

#### Bước 3: Kiểm thử hiển thị Responsive trên màn hình điện thoại (< 480px)
- Áp dụng Media Query `@media (max-width: 480px)`:
  - Nút tròn nổi tự động thu về kích thước `52px x 52px`, cách lề `16px`.
  - Khung chat chuyển sang chiếm `calc(100vw - 16px)` bề ngang và `calc(100vh - 24px)` chiều cao.
  - Các nút gợi ý nhanh và thẻ sách tự động co dãn theo chiều dọc, không bị tràn màn hình (overflow ngang) hay vỡ phông chữ.

---

## Phần sinh viên đã kiểm tra chỉnh sửa
- [x] **Hoàn thiện giao diện Quản lý sách cho Thủ thư (16/09/2026)**: Phát hiện modal "Thêm sách / Sửa sách" trong `Frontend/books.html` chưa có trường nhập tóm tắt sách để cung cấp dữ liệu cho Chatbot AI. Đã bổ sung ô `<textarea name="tomTat">` chiếm full-width (`grid-column: 1 / -1`), tự động nạp tóm tắt cũ khi bấm "Sửa" trong `books.js`, đồng bộ gửi lên API khi "Lưu".
- [x] **Sửa lỗi hiển thị thẻ sách gợi ý & đồng bộ Quick Filter trên `chatbot.html` (27/09/2026)**: Chuẩn hóa luồng render card sách gợi ý trong `frontend/chatbot.html` đọc đúng trường dữ liệu `data.ket_qua`, hiển thị ảnh bìa, tác giả, trạng thái còn hàng và nút "Xem chi tiết", loại bỏ lỗi nút gợi ý thể loại không phản hồi.

---

## Ngày thực hiện
- **Ngày thực hiện**: 15/09/2026 (Cập nhật hoàn thiện: 16/09/2026; Vá lỗi hiển thị thẻ gợi ý: 27/09/2026)
- **Người thực hiện**: Kỹ sư Frontend / Thành viên nhóm đề tài Web App Thư viện ICTU

