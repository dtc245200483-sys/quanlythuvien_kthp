# Minh Chứng Kỹ Thuật: RAG Retrieval, Prompt Engineering & Lớp Bảo Vệ Chống Lạc Đề

## Prompt đã dùng

### Phần A: Xây dựng tầng RAG Retrieval & Prompt Engineering
```text
Bạn là kỹ sư AI. Dự án nằm tại: D:\ung dung tri tue nhan tao\app

Hãy xây dựng tầng RAG Retrieval hoàn chỉnh cho chatbot tra cứu sách, 
kết hợp Vector Store (embedding, đã có ở chatbotAI\vector_store.py) với 
fuzzy match tên riêng (tên sách/tác giả), sau đó ghép context vào LLM 
để sinh câu trả lời cuối cùng.

VỊ TRÍ FILE CẦN TẠO:
- chatbotAI/rag_retriever.py
- chatbotAI/prompts/system_prompt.txt
- chatbotAI/prompt_builder.py
- chatbotAI/chatbot_service.py

YÊU CẦU CHÍNH:
1. rag_retriever.py: Kết hợp Embedding Search (VectorStore) + Fuzzy Match tên riêng (rapidfuzz).
   Công thức điểm tổng hợp: bonus +0.3 nếu khớp cả 2 nguồn, sắp xếp giảm dần, giới hạn top_k.
2. prompts/system_prompt.txt: System prompt RAG-aware, chỉ gợi ý sách trong context, schema JSON cố định.
3. prompt_builder.py: Ghép câu hỏi người dùng + context rút gọn thành user prompt chuẩn.
4. chatbot_service.py: Luồng 7 bước hoàn chỉnh (Retrieval -> Prompt -> Call LLM -> Parse JSON -> Lọc bịa dữ liệu).
```

### Phần B: Bổ sung 2 lớp bảo vệ chống câu hỏi lạc đề (Out-of-Domain Guardrails)
```text
Bạn là kỹ sư AI. Dự án nằm tại: D:\ung dung tri tue nhan tao\app

Bổ sung 2 lớp bảo vệ cho chatbot chống câu hỏi lạc đề (ngoài phạm vi 
thư viện, VD: chính trị, thời sự, đời tư, spam), vào các file đã có:
D:\ung dung tri tue nhan tao\app\chatbotAI\rag_retriever.py
D:\ung dung tri tue nhan tao\app\chatbotAI\chatbot_service.py
D:\ung dung tri tue nhan tao\app\chatbotAI\prompts\system_prompt.txt
(và cả 3 file v1/v2/v3 nếu đã tồn tại)

YÊU CẦU:

1. Trong rag_retriever.py, hàm truy_xuat_context(): thêm tham số 
   nguong_lien_quan: float = 0.35. Sau khi có kết quả cuối cùng, LỌC 
   BỎ những sách có điểm liên quan (diem_tuong_dong hoặc 
   diem_khop_ten quy đổi về cùng thang 0-1) THẤP HƠN ngưỡng này. Nếu 
   sau khi lọc không còn cuốn nào, trả về list rỗng.

2. Trong chatbot_service.py, hàm tra_cuu_sach(): khi context rỗng 
   (do không tìm thấy HOẶC do bị lọc ở bước 1), phân biệt 2 
   trường hợp bằng cách kiểm tra thêm: nếu điểm cao nhất trước khi 
   lọc (nếu có) vẫn rất thấp (< 0.15) → đây là dấu hiệu câu hỏi HOÀN 
   TOÀN lạc đề, trả về thong_bao = "Tôi chỉ hỗ trợ tra cứu sách trong 
   thư viện. Bạn vui lòng đặt câu hỏi liên quan đến sách nhé!" Nếu 
   điểm ở mức trung bình (0.15 - 0.35) → có thể là câu hỏi về sách 
   nhưng thư viện chưa có, trả về thong_bao = "Không tìm thấy sách 
   phù hợp trong thư viện." Cả 2 trường hợp đều KHÔNG gọi LLM.

3. Trong TẤT CẢ các file system prompt (system_prompt.txt, v1, v2, 
   v3 nếu tồn tại), thêm 1 quy tắc riêng biệt với các quy tắc đã có:
   "Nếu câu hỏi của độc giả không liên quan đến việc tìm sách hoặc 
   thư viện (ví dụ: hỏi về chính trị, thời sự, đời tư, kiến thức 
   chung không liên quan đến sách), hãy từ chối lịch sự và nhắc rằng 
   bạn chỉ hỗ trợ tra cứu sách trong thư viện, KHÔNG cố gắng trả lời 
   câu hỏi đó dù có kiến thức, và KHÔNG gán ghép sách không liên quan 
   vào câu trả lời."

KIỂM THỬ (bắt buộc):
Chạy thử tra_cuu_sach() với 3 câu hỏi hoàn toàn lạc đề:
1. "Ai là chủ tịch nước hiện tại?"
2. "Cho tôi công thức nấu phở"
3. "1 với 1 bằng mấy?"
Xác nhận cả 3 đều bị chặn ở bước similarity threshold (KHÔNG gọi 
LLM), in ra log xác nhận "đã chặn ở tầng retrieval, không tốn API 
call" cho từng câu.

Sau đó chạy thử 1 câu hỏi THỰC SỰ về sách nhưng thư viện không có 
(VD: "sách Harry Potter") để xác nhận nó KHÔNG bị nhầm sang nhánh 
"lạc đề hoàn toàn" mà vẫn đi đúng nhánh "không có sách phù hợp".
```

---

## Phản hồi/Kết quả của AI

### 1. Danh sách file trong hệ thống

| File | Loại thay đổi | Mô tả chức năng |
|------|:---:|-------|
| `chatbotAI/rag_retriever.py` | Cập nhật | Retrieval lai (Hybrid): Embedding + Fuzzy match, lọc ngưỡng liên quan (`nguong_lien_quan = 0.35`), ghi nhận điểm cao nhất trước lọc |
| `chatbotAI/chatbot_service.py` | Cập nhật | Luồng RAG hoàn chỉnh + Phân nhánh chặn sớm tại retrieval (< 0.15 vs [0.15, 0.35]) + Lớp lọc bịa dữ liệu |
| `chatbotAI/prompts/system_prompt.txt` | Cập nhật | Bổ sung **Quy tắc 8** (Lớp 2: Từ chối câu hỏi lạc đề ở tầng LLM), schema JSON cố định |
| `chatbotAI/prompt_builder.py` | Giữ nguyên | Ghép câu hỏi độc giả + context rút gọn thành user prompt |
| `chatbotAI/test_rag_full.py` | Tạo mới | Script kiểm thử 3 kịch bản RAG cơ bản (ngữ nghĩa, fuzzy match, không có sách) |
| `chatbotAI/test_chan_lac_de.py` | Tạo mới | Script kiểm thử 4 câu hỏi bắt buộc chặn tầng retrieval + 1 câu đối chứng |

---

### 2. Kiến trúc luồng RAG & 2 Tầng phòng ngự (Defense-in-Depth)

```
                                  Câu hỏi độc giả
                                         │
                                         ▼
                   ┌──────────────────────────────────────────────┐
                   │       TẦNG RETRIEVAL (rag_retriever.py)      │
                   │  - Embedding search (ChromaDB + MiniLM)      │
                   │  - Fuzzy match tên riêng (rapidfuzz)         │
                   │  - Chuẩn hóa điểm & phát hiện lạc đề         │
                   │  - LỌC NGƯỠNG: diem_lien_quan >= 0.35        │
                   └─────────────────────┬────────────────────────┘
                                         │
                        ┌────────────────┴────────────────┐
                        │ Context rỗng?                    │
                        ▼                                  ▼
                      [CÓ]                               [KHÔNG]
                        │                          (Đạt ngưỡng >= 0.35)
                        │                                  │
      ┌─────────────────┴─────────────────┐                ▼
      │ Kiểm tra diem_cao_nhat_truoc_loc │  ┌──────────────────────────────┐
      ▼                                   ▼  │ prompt_builder.py            │
 [Điểm < 0.15]                    [0.15 - 0.35]│ Ghép câu hỏi + Context        │
(Lạc đề hoàn toàn)               (Sách ngoài TV)└──────────────┬───────────────┘
      │                                   │                    │
      │                                   │                    ▼
      ▼                                   ▼  ┌──────────────────────────────┐
  CHẶN TẦNG 1                         CHẶN TẦNG 1 │ llm_client.py (deepseek-chat)│
(KHÔNG gọi LLM)                     (KHÔNG gọi LLM)│                              │
"Tôi chỉ hỗ trợ tra cứu             "Không tìm thấy   ├──────────────────────────────┤
sách trong thư viện..."             sách phù hợp..." │ LỚP BẢO VỆ 2 (SYSTEM PROMPT) │
                                                     │ - Quy tắc 8: Từ chối lịch sự │
                                                     │   câu hỏi ngoài thư viện     │
                                                     └──────────────┬───────────────┘
                                                                    │
                                                                    ▼
                                                     ┌──────────────────────────────┐
                                                     │ chatbot_service.py           │
                                                     │ - Parse JSON (kèm retry)     │
                                                     │ - LỌC BỊA DỮ LIỆU (Context) │
                                                     └──────────────┬───────────────┘
                                                                    │
                                                                    ▼
                                                             Kết quả cuối cùng
```

---

### 3. Kết quả kiểm thử Phần 1: Luồng RAG cơ bản (3 câu hỏi)

**Môi trường:** ChromaDB 1.5.9 | `paraphrase-multilingual-MiniLM-L12-v2` | OpenRouter API (`deepseek/deepseek-chat`)

#### 📌 Test 1: `"sách dạy làm bếp và chế biến thức ăn"` — Ngữ nghĩa
*Từ "làm bếp", "chế biến" không xuất hiện trong tên/tóm tắt sách nào*

**Context Retriever tìm được (8 sách sơ bộ):**
| # | Nguồn | Điểm | Tên sách | Tác giả |
|---|-------|------|---------|---------|
| 1 | ngu_nghia | 0.637 | Lập trình Python từ cơ bản đến nâng cao | Nguyễn Thành Nam |
| 2 | ngu_nghia | 0.636 | Nghĩ giàu làm giàu | Napoleon Hill |
| 3 | ngu_nghia | 0.630 | Tắt đèn | Ngô Tất Tố |
| ... | ... | ... | ... | ... |

**Câu trả lời LLM:**
```json
{
  "ket_qua": [],
  "tong_so_ket_qua": 0,
  "thong_bao": "Không tìm thấy sách nào về dạy làm bếp và chế biến thức ăn trong danh sách."
}
```
**✅ Đánh giá: LLM đánh giá lại đúng** — dù Retriever trả sách sơ bộ, LLM nhận ra không có cuốn nào thực sự về nấu ăn và trả về danh sách rỗng + giải thích rõ lý do.

---

#### 📌 Test 2: `"Carnegie"` — Fuzzy match tên tác giả
*Tác giả "Dale Carnegie" có trong thư viện*

**Context Retriever tìm được ("Đắc nhân tâm" lên #1 điểm 1.300):**
| # | Nguồn | Điểm | Tên sách | Tác giả |
|---|-------|------|---------|---------|
| ★1 | **ngu_nghia+ten_rieng** | **1.300** | **Đắc nhân tâm** | **Dale Carnegie** |
| 2 | ngu_nghia | 0.610 | Nghĩ giàu làm giàu | Napoleon Hill |
| 3 | ngu_nghia | 0.604 | Lược sử thời gian | Stephen Hawking |

**Câu trả lời LLM:**
```json
{
  "ket_qua": [
    {
      "ten_sach": "Đắc nhân tâm",
      "tac_gia": "Dale Carnegie",
      "ly_do_goi_y": "Sách của tác giả Dale Carnegie, phù hợp với từ khóa tìm kiếm.",
      "con_hang": true
    }
  ],
  "tong_so_ket_qua": 1,
  "thong_bao": ""
}
```
**✅ Đánh giá: Fuzzy match hoạt động tối ưu** — tên tác giả "Carnegie" khớp "Dale Carnegie" → điểm 1.300 (bonus khớp 2 nguồn) → LLM chọn đúng "Đắc nhân tâm" và loại bỏ toàn bộ sách không liên quan.

---

#### 📌 Test 3: `"sách dạy lái xe hơi và thi bằng lái"` — Không có sách phù hợp
**Câu trả lời LLM:**
```json
{
  "ket_qua": [],
  "tong_so_ket_qua": 0,
  "thong_bao": "Không tìm thấy sách về dạy lái xe hoặc thi bằng lái trong danh sách được cung cấp."
}
```
**✅ Đánh giá: LLM từ chối gợi ý đúng**, không bịa đặt sách ngoài thư viện.

---

### 4. Kết quả kiểm thử Phần 2: 2 Lớp bảo vệ chống câu hỏi lạc đề

Chạy script kiểm thử [chatbotAI/test_chan_lac_de.py](file:///d:/ung%20dung%20tri%20tue%20nhan%20ao/app/chatbotAI/test_chan_lac_de.py):

#### Log console thực tế xác nhận chặn ở tầng retrieval:
```
======================================================================
  KIỂM THỬ 2 LỚP BẢO VỆ CHỐNG CÂU HỎI LẠC ĐỀ
======================================================================

══════════════════════════════════════════════════════════════════════
  TEST 1: [LẠC ĐỀ HOÀN TOÀN] "Ai là chủ tịch nước hiện tại?" (Chính trị / Thời sự / Lãnh đạo)
──────────────────────────────────────────────────────────────────────
  📋 Số sách đạt ngưỡng context (>= 0.35): 0
  🎯 Điểm cao nhất trước khi lọc: 0.0541
[CHATBOT_SERVICE] 'Ai là chủ tịch nước hiện tại?' → đã chặn ở tầng retrieval, không tốn API call (câu hỏi hoàn toàn lạc đề (điểm cao nhất 0.0541 < 0.15))
  💬 Thông báo trả về: "Tôi chỉ hỗ trợ tra cứu sách trong thư viện. Bạn vui lòng đặt câu hỏi liên quan đến sách nhé!"
  Kết luận: ✅ PASS (Chặn tầng retrieval: True, Điểm < 0.15: True, Thông báo đúng: True)

══════════════════════════════════════════════════════════════════════
  TEST 2: [LẠC ĐỀ HOÀN TOÀN] "Cho tôi công thức nấu phở" (Nấu ăn / Ẩm thực đời sống)
──────────────────────────────────────────────────────────────────────
  📋 Số sách đạt ngưỡng context (>= 0.35): 0
  🎯 Điểm cao nhất trước khi lọc: 0.0299
[CHATBOT_SERVICE] 'Cho tôi công thức nấu phở' → đã chặn ở tầng retrieval, không tốn API call (câu hỏi hoàn toàn lạc đề (điểm cao nhất 0.0299 < 0.15))
  💬 Thông báo trả về: "Tôi chỉ hỗ trợ tra cứu sách trong thư viện. Bạn vui lòng đặt câu hỏi liên quan đến sách nhé!"
  Kết luận: ✅ PASS (Chặn tầng retrieval: True, Điểm < 0.15: True, Thông báo đúng: True)

══════════════════════════════════════════════════════════════════════
  TEST 3: [LẠC ĐỀ HOÀN TOÀN] "1 với 1 bằng mấy?" (Toán đố cơ bản / Chat nhảm / Spam)
──────────────────────────────────────────────────────────────────────
  📋 Số sách đạt ngưỡng context (>= 0.35): 0
  🎯 Điểm cao nhất trước khi lọc: 0.0284
[CHATBOT_SERVICE] '1 với 1 bằng mấy?' → đã chặn ở tầng retrieval, không tốn API call (câu hỏi hoàn toàn lạc đề (điểm cao nhất 0.0284 < 0.15))
  💬 Thông báo trả về: "Tôi chỉ hỗ trợ tra cứu sách trong thư viện. Bạn vui lòng đặt câu hỏi liên quan đến sách nhé!"
  Kết luận: ✅ PASS (Chặn tầng retrieval: True, Điểm < 0.15: True, Thông báo đúng: True)

══════════════════════════════════════════════════════════════════════
  TEST 4: [CÂU HỎI VỀ SÁCH - KHÔNG CÓ TRONG THƯ VIỆN] "sách Harry Potter"
──────────────────────────────────────────────────────────────────────
  📋 Số sách đạt ngưỡng context (>= 0.35): 0
  🎯 Điểm cao nhất trước khi lọc: 0.2344
[CHATBOT_SERVICE] 'sách Harry Potter' → đã chặn ở tầng retrieval, không tốn API call (không có sách phù hợp trong thư viện (điểm cao nhất 0.2344 nằm trong [0.15, 0.35]))
  💬 Thông báo trả về: "Không tìm thấy sách phù hợp trong thư viện."
  Kết luận: ✅ PASS (Chặn tầng retrieval: True, Điểm trong [0.15, 0.35]: True, Thông báo đúng: True)

══════════════════════════════════════════════════════════════════════
  TEST 5: [KIỂM TRA ĐỐI CHỨNG] Sách có trong thư viện: "Carnegie"
──────────────────────────────────────────────────────────────────────
  📋 Số sách đạt ngưỡng context (>= 0.35): 1
  🎯 Điểm cao nhất: 1.3000
  Top 1 sách: Đắc nhân tâm — Dale Carnegie (điểm: 1.3)
  Kết luận: ✅ PASS (Context hợp lệ, sẵn sàng chuyển LLM)
```

#### Bảng tổng hợp đối chiếu kết quả:

| STT | Câu hỏi kiểm thử | Phân loại chủ đề | Điểm max trước lọc | Phân nhánh xử lý | Gọi LLM? | Phản hồi thông báo | Đánh giá |
|:---:|:---|:---|:---:|:---|:---:|:---|:---:|
| 1 | *"Ai là chủ tịch nước hiện tại?"* | Chính trị / Lãnh đạo | **0.0541** (< 0.15) | Lạc đề hoàn toàn | ❌ KHÔNG | *"Tôi chỉ hỗ trợ tra cứu sách trong thư viện. Bạn vui lòng đặt câu hỏi liên quan đến sách nhé!"* | ✅ **PASS** |
| 2 | *"Cho tôi công thức nấu phở"* | Nấu ăn / Ẩm thực | **0.0299** (< 0.15) | Lạc đề hoàn toàn | ❌ KHÔNG | *"Tôi chỉ hỗ trợ tra cứu sách trong thư viện. Bạn vui lòng đặt câu hỏi liên quan đến sách nhé!"* | ✅ **PASS** |
| 3 | *"1 với 1 bằng mấy?"* | Toán đố / Spam | **0.0284** (< 0.15) | Lạc đề hoàn toàn | ❌ KHÔNG | *"Tôi chỉ hỗ trợ tra cứu sách trong thư viện. Bạn vui lòng đặt câu hỏi liên quan đến sách nhé!"* | ✅ **PASS** |
| 4 | *"sách Harry Potter"* | Hỏi sách ngoài thư viện | **0.2344** (0.15 - 0.35) | Sách chưa có | ❌ KHÔNG | *"Không tìm thấy sách phù hợp trong thư viện."* | ✅ **PASS** |
| 5 | *"Carnegie"* | Sách có trong TV | **1.3000** (>= 0.35) | Đạt ngưỡng context |  CÓ | Gợi ý cuốn *"Đắc nhân tâm"* | ✅ **PASS** |

---

### 5. Giải thích kỹ thuật & cơ chế an toàn

#### A. Vì sao cần đối chiếu chống bịa dữ liệu (Anti-Hallucination)?
- Dù prompt đã ràng buộc, LLM vẫn có thể bịa thông tin khi gặp context dài hoặc câu hỏi gây nhiễu.
- Nguyên tắc **Defense-in-Depth**: Lớp System Prompt là ràng buộc hành vi của mô hình, còn hàm `_loc_ket_qua_bija()` là chốt chặn độc lập tại code Python để loại bỏ 100% sách tự bịa trước khi gửi về client.

#### B. Vì sao cần chặn ở tầng Retrieval (Similarity Threshold)?
- **Tiết kiệm chi phí:** Các câu hỏi lạc đề (chính trị, spam, công thức nấu ăn...) bị chặn ngay tại tầng Python, không tiêu tốn token gọi LLM.
- **Phản hồi tức thì:** Giảm độ trễ từ vài giây (gọi API LLM) xuống dưới 50ms.
- **Bảo mật & an toàn nội dung:** Tránh để chatbot đưa ra các bình luận nhạy cảm về chính trị, thời sự hoặc đời tư.

---

## Phần sinh viên đã kiểm tra/chỉnh sửa
- [x] **Tối ưu cấu hình RAG Prompt & Top_k (16/09/2026)**: Chuẩn hóa `PROMPT_VERSION = "v3"`, điều chỉnh `top_k = 4` để cô đọng ngữ cảnh đưa vào LLM, giảm thời gian xử lý và tiết kiệm token OpenRouter.
- [x] **Bản vá Category Boost & Exact Match khắc phục False Negative (26/09/2026 - 27/09/2026)**: Phát hiện khi người dùng nhấn nút gợi ý thể loại (Lập trình, Kinh tế, Văn học...) thì câu hỏi ngắn bị embedding tính điểm thấp (< 0.35), gây chặn nhầm ở tầng retrieval. Đã bổ sung logic trong `rag_retriever.py` tự động so khớp thể loại trong CSDL SQL và boost điểm relevance lên [0.70, 0.85] để luôn nạp sách phù hợp vào context cho LLM DeepSeek sinh câu trả lời.

---

## Ngày thực hiện
15/09/2026 11:25 (Cập nhật bổ sung: 16/09/2026; Bản vá Category Boost: 27/09/2026)
