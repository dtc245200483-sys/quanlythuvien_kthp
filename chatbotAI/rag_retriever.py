"""
rag_retriever.py — Tầng Retrieval cho hệ thống RAG tra cứu sách.

Kết hợp 2 chiến lược tìm kiếm bù trừ nhau:
  - Embedding (Vector Store): tìm theo Ý NGHĨA / chủ đề / nội dung
  - Fuzzy match (rapidfuzz):  tìm theo TÊN RIÊNG (tên sách, tác giả)

Lý do cần cả 2:
  * Embedding rất mạnh khi hỏi theo nhu cầu ("sách dạy nấu ăn"),
    nhưng yếu với tên riêng vì tên riêng ít mang "nghĩa" ngữ nghĩa.
  * Fuzzy match bù đắp đúng lúc người dùng gõ tên sách/tác giả —
    kể cả khi gõ sai chính tả hoặc chỉ gõ một phần.

Hàm chính: truy_xuat_context(cau_hoi, top_k=8) -> list[dict]
"""

import logging
import sys
from pathlib import Path
from typing import Optional

# Đảm bảo hiển thị tiếng Việt trên Windows console
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Thêm thư mục app gốc vào sys.path
APP_ROOT = Path(__file__).resolve().parent.parent
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

from chatbotAI.vector_store import VectorStore  # noqa: E402

_logger = logging.getLogger("ai_calls")

# Ngưỡng fuzzy match — partial_ratio >= 60 mới tính là khớp
FUZZY_THRESHOLD = 60

# Mẫu phát hiện câu hỏi hoàn toàn lạc đề (chính trị, thời sự, đời tư, nấu ăn, toán đố, spam)
PATTERNS_LAC_DE = [
    # Chính trị, thời sự, chức danh lãnh đạo, bộ máy nhà nước
    r"\b(chủ tịch nước|thủ tướng|tổng bí thư|chủ tịch quốc hội|bộ trưởng|chính phủ|quốc hội|đảng cộng sản|tổng thống|bầu cử|chiến tranh|thời sự|tin tức|biển đông)\b",
    # Công thức món ăn, nấu nướng (không phải tìm sách)
    r"\b(công thức nấu|cách nấu|nấu phở|nấu bún|nấu lẩu|món ăn|cách làm bánh|pha chế|cách luộc|hôm nay ăn gì|món ngon)\b",
    # Toán đố, phép tính, spam số học
    r"\b(\d+\s*[\+\-\*\/x]\s*\d+|\d+\s+với\s+\d+\s+bằng|bằng mấy|giải phương trình|tính đạo hàm|tích phân)\b",
    # Đời tư, chitchat cá nhân, trêu chọc bot
    r"\b(bạn tên gì|bạn là ai|bao nhiêu tuổi|người yêu|đời tư|kể chuyện cười|hát đi|thời tiết hôm nay)\b",
]


class ContextList(list):
    """
    Subclass của list chuẩn, bổ sung các thuộc tính metadata cho retrieval.
    Tương thích 100% với list thông thường (len, for, json serialize...).
    """
    diem_cao_nhat_truoc_loc: float = 0.0
    co_the_la_ten_sach: bool = False  # True khi câu hỏi có khả năng là tên riêng 1 cuốn sách cụ thể


def _kiem_tra_cau_hoi_lac_de(cau_hoi: str) -> bool:
    """
    Kiểm tra câu hỏi có thuộc các chủ đề hoàn toàn lạc đề (ngoài phạm vi thư viện) hay không.
    Nếu câu hỏi chứa từ khóa thể hiện rõ nhu cầu tìm sách thì không coi là lạc đề.
    """
    if not cau_hoi or not isinstance(cau_hoi, str):
        return False
    cau_hoi_lower = cau_hoi.lower().strip()

    # Từ khóa rõ ràng về nhu cầu tra cứu sách/thư viện
    tu_khoa_sach = ["sách", "truyện", "tiểu thuyết", "tác phẩm", "giáo trình", "tác giả", "cuốn", "mượn sách", "đọc sách"]
    if any(tk in cau_hoi_lower for tk in tu_khoa_sach):
        return False

    import re
    for pattern in PATTERNS_LAC_DE:
        if re.search(pattern, cau_hoi_lower):
            return True
    return False


# ─────────────────────────────────────────────────────────────────────────────
# Hàm lấy toàn bộ metadata sách từ Vector Store (dùng cho fuzzy match)
# ─────────────────────────────────────────────────────────────────────────────

def _lay_tat_ca_sach_tu_vs(vs: VectorStore) -> list[dict]:
    """
    Lấy toàn bộ sách đang có trong Vector Store để fuzzy match.
    Dùng collection.get() — lấy tất cả documents và metadata.

    Trả về list[dict] với: ma_sach, ten_sach, tac_gia, the_loai, con_hang, tom_tat
    """
    try:
        ket_qua_raw = vs._collection.get(
            include=["documents", "metadatas"],
        )
        ids = ket_qua_raw.get("ids", [])
        documents = ket_qua_raw.get("documents", [])
        metadatas = ket_qua_raw.get("metadatas", [])

        danh_sach = []
        for ma_sach, doc, meta in zip(ids, documents, metadatas):
            con_hang_val = str(meta.get("con_hang", "True")).lower() == "true"
            danh_sach.append({
                "ma_sach": ma_sach,
                "ten_sach": meta.get("ten_sach", ""),
                "tac_gia": meta.get("tac_gia", ""),
                "the_loai": meta.get("the_loai", ""),
                "con_hang": con_hang_val,
                "tom_tat": doc or "",
            })
        return danh_sach
    except Exception as e:
        _logger.warning(f"[RAG_RETRIEVER] Không lấy được danh sách sách từ VS: {e}")
        return []


# ─────────────────────────────────────────────────────────────────────────────
# Hàm fuzzy match tên riêng
# ─────────────────────────────────────────────────────────────────────────────

def _fuzzy_match_ten(cau_hoi: str, tat_ca_sach: list[dict]) -> list[dict]:
    """
    Dùng rapidfuzz.fuzz.partial_ratio so khớp câu hỏi với ten_sach và tac_gia.
    Ngưỡng: partial_ratio >= FUZZY_THRESHOLD (60).

    Trả về list[dict] với thêm trường diem_khop_ten (0–100).
    """
    try:
        from rapidfuzz import fuzz
    except ImportError:
        _logger.error(
            "[RAG_RETRIEVER] 'rapidfuzz' chưa cài. Chạy: pip install rapidfuzz"
        )
        return []

    ket_qua = []
    cau_hoi_lower = cau_hoi.lower().strip()

    for sach in tat_ca_sach:
        diem_ten = fuzz.partial_ratio(cau_hoi_lower, sach["ten_sach"].lower())
        diem_tac_gia = fuzz.partial_ratio(cau_hoi_lower, sach["tac_gia"].lower())
        diem_cao_nhat = max(diem_ten, diem_tac_gia)

        if diem_cao_nhat >= FUZZY_THRESHOLD:
            entry = dict(sach)
            entry["diem_khop_ten"] = diem_cao_nhat
            entry["ly_do_fuzzy"] = (
                f"Tên sách khớp {diem_ten}%" if diem_ten >= diem_tac_gia
                else f"Tác giả khớp {diem_tac_gia}%"
            )
            ket_qua.append(entry)

    # Sắp xếp theo điểm giảm dần
    ket_qua.sort(key=lambda x: x["diem_khop_ten"], reverse=True)
    return ket_qua


# ─────────────────────────────────────────────────────────────────────────────
# Hàm phát hiện tra cứu tên riêng (Exact-ish title lookup detection)
# ─────────────────────────────────────────────────────────────────────────────

# Từ khóa chỉ rõ đây là tìm theo CHỦ ĐỀ / THỂ LOẠI, không phải tra cứu tên sách cụ thể
_TU_KHOA_TIM_KIEM_CHU_DE = [
    "sách về", "sách gì", "sách nào", "có sách", "gợi ý", "tìm kiếm",
    "muốn tìm", "liên quan", "đọc gì", "cho tôi", "hình như", "cuốn gì",
    "tôi cần", "tôi muốn", "giới thiệu", "tìm sách", "sách hay",
    "sách của", "gì đó", "của tác giả", "thể loại", "chủ đề",
    "kinh tế", "quản trị", "kinh doanh", "làm giàu", "tài chính",
    "lập trình", "cntt", "công nghệ thông tin", "phần mềm", "tin học",
    "trí tuệ nhân tạo", "ai", "chatgpt", "khoa học máy tính", "machine learning",
    "an ninh mạng", "bảo mật", "an toàn thông tin", "hacker", "mạng máy tính",
    "kỹ năng", "giao tiếp", "phát triển bản thân", "tâm lý", "ứng xử",
    "đáng đọc", "sách mới", "sách nổi bật", "hay nhất", "kinh điển",
    "tư vấn", "danh sách", "top sách", "nên đọc", "học lập trình"
]


def _phat_hien_tra_cuu_ten_sach(
    cau_hoi: str,
    tat_ca_sach: list[dict],
) -> tuple[bool, bool, list[dict]]:
    """
    Phát hiện câu hỏi có phải là tra cứu tên riêng một cuốn sách cụ thể hay không.

    Nguyên lý: Khi câu hỏi giống gần như toàn bộ tên 1 cuốn sách cụ thể
    (fuzz.ratio() >= 80), ưu tiên coi đây là tra cứu tên riêng (exact-ish
    lookup), không phải tìm kiếm theo chủ đề — tránh trường hợp trùng từ
    khóa ngẫu nhiên với sách không liên quan.

    Ví dụ: "Chiến tranh và Hòa bình" → câu ngắn, không có từ khóa tìm chủ đề
    → đây là tra cứu tên sách. Nếu thư viện không có sách này, thông báo rõ
    ràng thay vì trả về sách chỉ trùng vài từ như "Vũ Khí Hoàn Hảo - Chiến Tranh...".

    Returns:
        Tuple (la_ten_sach_chinh_xac, co_the_la_ten_sach, sach_khop_chinh_xac)
        - la_ten_sach_chinh_xac (bool):  True nếu sách trong kho khớp >= 80%
          → trả trực tiếp, bỏ qua embedding
        - co_the_la_ten_sach (bool):     True nếu câu hỏi CÓ THỂ là tên sách
          (ratio 50-79%, hoặc câu ngắn ≤ 7 từ không có từ khóa chủ đề)
          → dùng thông báo cụ thể hơn khi không tìm thấy sách
        - sach_khop_chinh_xac (list):    Danh sách sách khớp chính xác
          (chỉ có dữ liệu khi la_ten_sach_chinh_xac = True)
    """
    try:
        from rapidfuzz import fuzz as _fuzz
    except ImportError:
        return False, False, []

    import re
    cau_hoi_norm = cau_hoi.strip().lower()
    cau_hoi_clean = re.sub(r"^[📚💻🤖🔒🗣️⭐\s\-\:\.\,]+", "", cau_hoi_norm).strip()

    # Nếu câu hỏi bắt đầu bằng từ "sách" hoặc chứa emoji/từ khóa chủ đề → 100% tìm chủ đề
    if cau_hoi_norm.startswith("sách ") or cau_hoi_clean.startswith("sách "):
        return False, False, []

    # Nếu câu hỏi chứa từ khóa tìm theo chủ đề/thể loại → không phải tra cứu tên sách
    for tu_khoa in _TU_KHOA_TIM_KIEM_CHU_DE:
        if tu_khoa in cau_hoi_norm or tu_khoa in cau_hoi_clean:
            return False, False, []

    # So khớp TOÀN BỘ chuỗi (fuzz.ratio) — khác partial_ratio chỉ tìm chuỗi con
    # Ưu điểm: fuzz.ratio thấp khi 2 chuỗi chênh lệch độ dài nhiều →
    # "Chiến tranh và Hòa bình" sẽ KHÔNG khớp cao với "Vũ Khí Hoàn Hảo - Chiến Tranh..."
    diem_ratio_cao_nhat = 0
    sach_khop_chinh_xac = []

    for sach in tat_ca_sach:
        ratio = _fuzz.ratio(cau_hoi_norm, sach["ten_sach"].lower())
        if ratio >= 80:
            entry = dict(sach)
            entry["diem_khop_ten"] = ratio
            entry["nguon_khop"] = ["ten_rieng"]
            entry["diem_tuong_dong"] = 0.0
            entry["diem_lien_quan"] = ratio / 100.0
            entry["ly_do_fuzzy"] = f"Tên sách khớp toàn chuỗi {ratio}%"
            sach_khop_chinh_xac.append(entry)
        diem_ratio_cao_nhat = max(diem_ratio_cao_nhat, ratio)

    # Sách khớp chính xác tên (>= 80%) → tìm đích danh, bỏ qua embedding
    if sach_khop_chinh_xac:
        sach_khop_chinh_xac.sort(key=lambda x: x["diem_khop_ten"], reverse=True)
        return True, False, sach_khop_chinh_xac

    # Câu hỏi ngắn (≤ 7 từ) mà không có từ khóa chủ đề → có thể là tên sách
    # chưa có trong kho (VD: "Chiến tranh và Hòa bình", "Harry Potter"...)
    so_tu = len(cau_hoi.strip().split())
    co_the_la_ten_sach = (50 <= diem_ratio_cao_nhat < 80) or (so_tu <= 7)

    return False, co_the_la_ten_sach, []


# ─────────────────────────────────────────────────────────────────────────────
# Hàm tổng hợp — Retrieval chính
# ─────────────────────────────────────────────────────────────────────────────

def truy_xuat_context(
    cau_hoi: str,
    top_k: int = 8,
    nguong_lien_quan: float = 0.35,
) -> list[dict]:
    """
    Tầng Retrieval RAG: kết hợp Embedding + Fuzzy match → lọc theo ngưỡng liên quan.

    Luồng xử lý:
    1. Embedding search → list A (tìm theo ngữ nghĩa/chủ đề)
    2. Fuzzy match tên riêng → list B (khớp tên sách/tác giả)
    3. Gộp A + B, loại trùng theo ma_sach, cộng gộp thông tin
    4. Chuẩn hóa điểm liên quan về thang 0-1, ghi nhận diem_cao_nhat_truoc_loc
    5. LỌC BỎ các sách có điểm liên quan < nguong_lien_quan (0.35)
    6. Nếu sau khi lọc không còn cuốn nào, trả về list rỗng

    Tham số:
        cau_hoi (str): Câu hỏi tra cứu của độc giả.
        top_k (int):   Số kết quả tối đa trả về (mặc định 8).
        nguong_lien_quan (float): Ngưỡng điểm tối thiểu để đưa vào context (mặc định 0.35).

    Trả về:
        ContextList[dict]: Danh sách sách đã lọc đạt ngưỡng, mỗi phần tử gồm:
            ma_sach, ten_sach, tac_gia, the_loai, con_hang, tom_tat,
            diem_tuong_dong (float, 0–1, đã chuẩn hóa),
            diem_khop_ten (int, 0–100, chỉ có nếu khớp fuzzy),
            diem_lien_quan (float, điểm tổng hợp để xếp hạng),
            nguon_khop (list[str]: ["ngu_nghia"] | ["ten_rieng"] | cả 2)
        Kèm thuộc tính diem_cao_nhat_truoc_loc trên list kết quả.
    """
    if not cau_hoi or not isinstance(cau_hoi, str) or not cau_hoi.strip():
        truy_xuat_context.diem_cao_nhat_truoc_loc = 0.0
        res = ContextList([])
        res.diem_cao_nhat_truoc_loc = 0.0
        res.co_the_la_ten_sach = False
        return res

    vs = VectorStore()

    # ── Bước 1: Embedding search ──────────────────────────────────────────────
    list_a_raw = vs.tim_kiem_ngu_nghia(cau_hoi.strip(), top_k=10)

    # Chuyển thành dict dễ gộp: key = ma_sach
    map_ket_qua: dict[str, dict] = {}

    for item in list_a_raw:
        ma = item["ma_sach"]
        map_ket_qua[ma] = {
            "ma_sach": ma,
            "ten_sach": item["ten_sach"],
            "tac_gia": item["tac_gia"],
            "the_loai": item["the_loai"],
            "con_hang": item["con_hang"],
            "tom_tat": item["tom_tat"],
            "diem_tuong_dong": item["diem_tuong_dong"],
            "diem_khop_ten": 0,
            "nguon_khop": ["ngu_nghia"],
        }

    # ── Bước 2: Phát hiện "tìm đích danh tên sách" + Fuzzy match tên riêng ────
    tat_ca_sach = _lay_tat_ca_sach_tu_vs(vs)

    # Bước 2a: Phát hiện câu hỏi là tên sách cụ thể (fuzz.ratio >= 80 hoặc heuristic)
    la_ten_sach_chinh_xac, co_the_la_ten_sach, sach_khop_chinh_xac = \
        _phat_hien_tra_cuu_ten_sach(cau_hoi.strip(), tat_ca_sach)

    if la_ten_sach_chinh_xac:
        # Sách được tìm thấy trong kho qua đối chiếu tên chính xác → bỏ qua embedding
        sach_khop_chinh_xac.sort(key=lambda x: x["diem_khop_ten"], reverse=True)
        res = ContextList(sach_khop_chinh_xac[:top_k])
        res.diem_cao_nhat_truoc_loc = sach_khop_chinh_xac[0]["diem_lien_quan"]
        res.co_the_la_ten_sach = False  # Tìm thấy chính xác → không cần cờ cảnh báo
        _logger.info(
            f"[RAG_RETRIEVER] '{cau_hoi[:50]}' → Tìm đích danh tên sách "
            f"(fuzz.ratio={sach_khop_chinh_xac[0]['diem_khop_ten']}%), "
            f"bỏ qua embedding, trả {len(sach_khop_chinh_xac)} kết quả."
        )
        return res

    # Bước 2b: Fuzzy match tên riêng thông thường (partial_ratio >= 60)
    list_b_raw = _fuzzy_match_ten(cau_hoi.strip(), tat_ca_sach)

    for item in list_b_raw:
        ma = item["ma_sach"]
        if ma in map_ket_qua:
            # ── Sách xuất hiện ở CẢ 2 nguồn → gộp thông tin ──────────────
            map_ket_qua[ma]["diem_khop_ten"] = item["diem_khop_ten"]
            if "ten_rieng" not in map_ket_qua[ma]["nguon_khop"]:
                map_ket_qua[ma]["nguon_khop"].append("ten_rieng")
        else:
            # ── Sách chỉ khớp fuzzy, không có trong embedding results ────
            map_ket_qua[ma] = {
                "ma_sach": ma,
                "ten_sach": item["ten_sach"],
                "tac_gia": item["tac_gia"],
                "the_loai": item["the_loai"],
                "con_hang": item["con_hang"],
                "tom_tat": item["tom_tat"],
                "diem_tuong_dong": 0.0,
                "diem_khop_ten": item["diem_khop_ten"],
                "nguon_khop": ["ten_rieng"],
            }

    # ── Bước 3: Không có kết quả sơ bộ → trả về rỗng ──────────────────────────
    if not map_ket_qua:
        _logger.info(f"[RAG_RETRIEVER] '{cau_hoi[:50]}' → 0 kết quả sơ bộ")
        truy_xuat_context.diem_cao_nhat_truoc_loc = 0.0
        res = ContextList([])
        res.diem_cao_nhat_truoc_loc = 0.0
        res.co_the_la_ten_sach = co_the_la_ten_sach
        return res

    # ── Bước 4: Tính diem_lien_quan và chuẩn hóa thang 0 - 1 ──────────────────
    danh_sach = list(map_ket_qua.values())
    la_lac_de = _kiem_tra_cau_hoi_lac_de(cau_hoi)

    for item in danh_sach:
        co_ca_hai = len(item["nguon_khop"]) == 2
        bonus = 0.3 if co_ca_hai else 0.0
        diem_fuzzy_chuan = item["diem_khop_ten"] / 100.0

        # Chuẩn hóa diem_tuong_dong từ vector_store (1 - dist/2) về cosine similarity chuẩn
        diem_raw = item.get("diem_tuong_dong", 0.0)
        diem_sim = round(max(0.0, 2.0 * diem_raw - 1.0), 4)

        # Nếu câu hỏi hoàn toàn lạc đề (chính trị, thời sự, công thức nấu ăn, toán đố...),
        # hạ thấp điểm liên quan để đảm bảo < 0.15 và kích hoạt lớp chặn tầng retrieval
        if la_lac_de:
            diem_sim = round(min(diem_sim * 0.15, 0.08), 4)

        item["diem_tuong_dong"] = diem_sim
        item["diem_lien_quan"] = round(
            max(diem_sim, diem_fuzzy_chuan) + bonus, 4
        )

    # Sắp xếp: khớp cả 2 nguồn lên đầu, rồi theo điểm giảm dần
    danh_sach.sort(
        key=lambda x: (len(x["nguon_khop"]) == 2, x["diem_lien_quan"]),
        reverse=True,
    )

    # Ghi nhận điểm cao nhất trước khi lọc
    diem_cao_nhat_truoc_loc = max([x["diem_lien_quan"] for x in danh_sach], default=0.0)
    truy_xuat_context.diem_cao_nhat_truoc_loc = diem_cao_nhat_truoc_loc

    # ── Bước 5: LỌC BỎ những sách có điểm liên quan < nguong_lien_quan (0.35) ──
    ket_qua_sau_loc = [
        item for item in danh_sach
        if item["diem_lien_quan"] >= nguong_lien_quan
    ]

    # Giới hạn top_k kết quả cuối cùng
    ket_qua_cuoi = ket_qua_sau_loc[:top_k]

    _logger.info(
        f"[RAG_RETRIEVER] '{cau_hoi[:50]}' → "
        f"{len(ket_qua_cuoi)}/{len(danh_sach)} sách đạt ngưỡng {nguong_lien_quan} "
        f"(max_score_truoc_loc={diem_cao_nhat_truoc_loc:.4f}, la_lac_de={la_lac_de})"
    )

    res = ContextList(ket_qua_cuoi)
    res.diem_cao_nhat_truoc_loc = diem_cao_nhat_truoc_loc
    res.co_the_la_ten_sach = co_the_la_ten_sach
    return res
