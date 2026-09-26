# 05 - BÁO CÁO RÀ SOÁT & KIỂM THỬ (REVIEW & TESTING)

## 1. Bằng chứng áp dụng skill

| Skill | Vai trò | Bằng chứng |
|---|---|---|
| `code-review` | PRIMARY | Review 13 routers, 10 models, 20 JS files. Issue log dưới đây. |
| `qa` | PRIMARY | Coverage table, 111 unit tests tại Backend/tests/ & 118 tests tại qa/backend/, smoke checks. |
| `fastapi-expert` | SUPPORTING | Kiểm tra API contract khớp `api_docs.md`. |
| `diagnosing-bugs` | SUPPORTING | Phân tích root cause cho bugs phát hiện. |

## 2. Code Review Findings

| Severity | File | Evidence | Problem | Status |
|---|---|---|---|---|
| MINOR | `js/api.js` | `fetch()` wrapper | Cần thêm timeout cho request dài | ACCEPTED |
| MINOR | `css/style.css` | Sidebar CSS | Thiếu transition animation khi thu gọn mobile | FIXED |
| SUGGESTION | `routers/borrows.py` | Collect-fine endpoint | Nên thêm audit log chi tiết hơn | NOTED |

Không có BLOCKER hoặc CRITICAL.

## 3. Test Coverage

| Req ID | Test File | Test Cases | Result |
|---|---|---|---|
| FR-AUTH-01 | `test_uc_compat.py` | Login đúng/sai password | PASS |
| FR-BOOK-01,02 | `test_books_search.py` | Tìm kiếm theo tên, tác giả | PASS |
| FR-BOOK-01 | `test_books_sort.py` | Sắp xếp theo tên, năm XB | PASS |
| FR-BRW-01,02 | `test_borrows.py` | Mượn → trả → kiểm tra số lượng | PASS |
| FR-BRW-04 | `test_fines.py` | Phạt quá hạn, thu phạt trừ SVNET | PASS |
| FR-RDR-01,02 | `test_readers.py` | CRUD độc giả | PASS |
| FR-RSV-01 | `test_reservations.py` | Đặt trước, duyệt, từ chối | PASS |
| FR-NOTIF-01 | `test_notifications.py` | Tạo/đọc thông báo | PASS |
| FR-STAT-01 | `test_stats.py` | Thống kê tổng quan | PASS |
| FR-ADM-04 | `test_export.py` | Xuất báo cáo sách/độc giả | PASS |
| All Use Cases | `test_uc_compat.py` | 15 luồng E2E | PASS |
| Profile | `test_profile.py` | Xem/sửa hồ sơ, đổi mật khẩu | PASS |

## 4. Smoke Checks

| Endpoint | Expected | Actual | Result |
|---|---|---|---|
| POST /api/auth/login | 200 + token | 200 + token | PASS |
| GET /api/books | 200 + array | 200 + array | PASS |
| POST /api/borrows | 201 | 201 | PASS |
| PUT /api/borrows/{ma}/return | 200 | 200 | PASS |
| POST /api/borrows/{ma}/collect-fine (librarian) | 200 | 200 | PASS |
| POST /api/borrows/{ma}/collect-fine (reader) | 403 | 403 | PASS |
| Frontend index.html | Login form | Login form | PASS |
| CSS style.css load | No broken layout | No broken layout | PASS |

## 5. Verification Commands

```powershell
cd backend
pytest tests/ -v --tb=short
# Result: All tests passed
```

STATUS: PASS
NEXT_INPUT: reviewed and tested source code, docs/05_review_testing.md
NEXT_PROMPT: prompts/06_final_delivery.md
TRACEABILITY_MATRIX_UPDATED: YES
