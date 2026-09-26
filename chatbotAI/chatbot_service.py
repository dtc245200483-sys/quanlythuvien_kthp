"""
chatbot_service.py — Hàm tổng hợp toàn bộ luồng RAG tra cứu sách.

Luồng chính:
  1. truy_xuat_context()   → Retrieval (embedding + fuzzy)
  2. xay_dung_user_prompt()→ Ghép prompt
  3. Đọc system_prompt.txt
  4. call_llm()            → Gọi LLM sinh câu trả lời
  5. Parse + Validate JSON → Kiểm soát bịa dữ liệu
  6. Trả về kết quả sạch

Lớp bảo vệ chống hallucination:
  Dù system prompt đã ràng buộc LLM, bước 7 vẫn đối chiếu tên sách
  trong kết quả LLM với context ban đầu — loại bỏ mọi sách LLM tự bịa.
"""

import json
import logging
import sys
import time
from pathlib import Path
from typing import Optional

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

from chatbotAI.rag_retriever import truy_xuat_context    # noqa: E402
from chatbotAI.prompt_builder import xay_dung_user_prompt # noqa: E402
from chatbotAI.llm_client import call_llm                 # noqa: E402
from chatbotAI.config import doc_system_prompt, PROMPT_VERSION # noqa: E402

_logger = logging.getLogger("ai_calls")

SYSTEM_PROMPT_FILE = Path(__file__).resolve().parent / "prompts" / "system_prompt.txt"


# ─────────────────────────────────────────────────────────────────────────────
# Hàm đọc system prompt (fallback tương thích ngược)
# ─────────────────────────────────────────────────────────────────────────────

def _doc_system_prompt(version: Optional[str] = None) -> str:
    return doc_system_prompt(version=version)


# ─────────────────────────────────────────────────────────────────────────────
# Hàm parse + validate JSON từ LLM
# ─────────────────────────────────────────────────────────────────────────────

def _parse_json_llm(phan_hoi: str) -> Optional[dict]:
    """Trích xuất JSON hợp lệ từ phản hồi LLM (phòng khi LLM thêm text thừa)."""
    noi_dung = phan_hoi.strip()
    # Tìm khối {} đầu tiên và cuối cùng
    bat_dau = noi_dung.find("{")
    ket_thuc = noi_dung.rfind("}") + 1
    if bat_dau != -1 and ket_thuc > bat_dau:
        noi_dung = noi_dung[bat_dau:ket_thuc]
    try:
        data = json.loads(noi_dung)
        # Validate schema tối thiểu
        if "ket_qua" not in data:
            return None
        if not isinstance(data["ket_qua"], list):
            return None
        return data
    except (json.JSONDecodeError, ValueError):
        return None


# ─────────────────────────────────────────────────────────────────────────────
# Lớp kiểm soát chống bịa — Phần 4 Mục 7
# ─────────────────────────────────────────────────────────────────────────────

def _loc_ket_qua_bija(ket_qua_llm: list[dict], context: list[dict]) -> list[dict]:
    """
    Đối chiếu tên sách LLM trả về với context ban đầu.
    Loại bỏ mọi sách mà LLM tự bịa (không có trong context).
    Đồng thời làm giàu metadata từ context: ma_sach, the_loai, tom_tat, con_hang.
    """
    context_map = {}
    for s in context:
        if isinstance(s, dict) and s.get("ten_sach"):
            key = s["ten_sach"].lower().strip()
            context_map[key] = s

    ket_qua_sach = []
    for item in ket_qua_llm:
        if not isinstance(item, dict):
            continue
        ten = (item.get("ten_sach") or "").lower().strip()
        if ten and ten in context_map:
            ctx_item = context_map[ten]
            item_enriched = dict(item)
            item_enriched["ma_sach"] = ctx_item.get("ma_sach", "")
            item_enriched["the_loai"] = ctx_item.get("the_loai", "")
            item_enriched["tom_tat"] = ctx_item.get("tom_tat", "")
            # Đảm bảo con_hang chuẩn theo context
            item_enriched["con_hang"] = ctx_item.get("con_hang", item.get("con_hang", True))
            # Điểm fuzzy match tên sách (từ retriever) — dùng để kiểm tra chế độ tìm tên riêng
            item_enriched["diem_khop_ten"] = ctx_item.get("diem_khop_ten", 0)
            if "khop_voi_tu_khoa" not in item_enriched or not isinstance(item_enriched["khop_voi_tu_khoa"], list):
                item_enriched["khop_voi_tu_khoa"] = []
            ket_qua_sach.append(item_enriched)
        else:
            _logger.warning(
                f"[CHATBOT_SERVICE] ⚠️ AI có dấu hiệu bịa dữ liệu: "
                f"Sách '{item.get('ten_sach', '?')}' không có trong context — đã loại bỏ."
            )

    return ket_qua_sach


# ─────────────────────────────────────────────────────────────────────────────
# Hàm chính: tra_cuu_sach()
# ─────────────────────────────────────────────────────────────────────────────

def tra_cuu_sach(cau_hoi: str, prompt_version: Optional[str] = None) -> dict:
    """
    Luồng RAG tra cứu sách hoàn chỉnh hỗ trợ đa phiên bản prompt (v1, v2, v3).

    Tham số:
        cau_hoi (str): Câu hỏi của độc giả.
        prompt_version (str, optional): "v1", "v2", "v3". Mặc định dùng PROMPT_VERSION từ config.

    Trả về:
        dict: {
          "ket_qua": [...],        # danh sách sách gợi ý
          "tong_so_ket_qua": int,
          "thong_bao": str,        # thông báo kết quả hoặc lý do
          "raw_text": str,         # phản hồi văn bản thô từ LLM
          "context_so_bo": int,    # số sách retriever tìm được
          "context_list": list,    # danh sách context chi tiết
          "thoi_gian_ms": int,     # thời gian xử lý (ms)
          "prompt_version": str,   # phiên bản prompt sử dụng
          "canh_bao_bia": bool,    # cảnh báo có sách ngoài context
        }
    """
    start_time = time.time()
    version = prompt_version or PROMPT_VERSION

    # ── Bước 1: Retrieval ─────────────────────────────────────────────────────
    # Với v1 và v2: lấy context sơ bộ (nguong=0.0) mô phỏng vòng thử nghiệm 1 & 2
    # Với v3: áp dụng lớp lọc ngưỡng liên quan (nguong=0.35)
    nguong = 0.35 if version == "v3" else 0.0
    try:
        context = truy_xuat_context(cau_hoi, nguong_lien_quan=nguong)
    except Exception as e:
        _logger.error(f"[CHATBOT_SERVICE] Retrieval thất bại: {e}")
        return {"loi": f"Lỗi tìm kiếm: {e}"}

    # ── Bước 2: Chặn tầng retrieval (Chỉ áp dụng với v3 bản chính thức) ─────────
    if version == "v3" and not context:
        diem_cao_nhat = getattr(context, "diem_cao_nhat_truoc_loc", None)
        if diem_cao_nhat is None:
            diem_cao_nhat = getattr(truy_xuat_context, "diem_cao_nhat_truoc_loc", 0.0)

        if diem_cao_nhat < 0.15:
            thong_bao = (
                "Tôi chỉ hỗ trợ tra cứu sách trong thư viện. "
                "Bạn vui lòng đặt câu hỏi liên quan đến sách nhé!"
            )
            ly_do_chan = (
                f"câu hỏi hoàn toàn lạc đề (điểm cao nhất {diem_cao_nhat:.4f} < 0.15)"
            )
        else:
            thong_bao = "Không tìm thấy sách phù hợp trong thư viện."
            ly_do_chan = (
                f"không có sách phù hợp trong thư viện "
                f"(điểm cao nhất {diem_cao_nhat:.4f} nằm trong [0.15, 0.35])"
            )

        log_msg = (
            f"[CHATBOT_SERVICE] '{cau_hoi}' → đã chặn ở tầng retrieval, "
            f"không tốn API call ({ly_do_chan})"
        )
        _logger.info(log_msg)
        print(log_msg)

        elapsed_ms = int((time.time() - start_time) * 1000)
        return {
            "ket_qua": [],
            "tong_so_ket_qua": 0,
            "thong_bao": thong_bao,
            "raw_text": thong_bao,
            "context_so_bo": 0,
            "context_list": [],
            "diem_cao_nhat": diem_cao_nhat,
            "thoi_gian_ms": elapsed_ms,
            "prompt_version": version,
            "canh_bao_bia": False,
        }

    # Nếu không có context (ngay cả khi nguong=0.0)
    if not context:
        elapsed_ms = int((time.time() - start_time) * 1000)
        return {
            "ket_qua": [],
            "tong_so_ket_qua": 0,
            "thong_bao": "Không tìm thấy sách phù hợp trong thư viện.",
            "raw_text": "Không tìm thấy sách phù hợp trong thư viện.",
            "context_so_bo": 0,
            "context_list": [],
            "thoi_gian_ms": elapsed_ms,
            "prompt_version": version,
            "canh_bao_bia": False,
        }

    # ── Bước 3: Xây dựng user prompt ─────────────────────────────────────────
    try:
        user_prompt = xay_dung_user_prompt(cau_hoi, context)
    except Exception as e:
        return {"loi": f"Lỗi xây dựng prompt: {e}"}

    # ── Bước 4: Đọc system prompt theo version ────────────────────────────────
    try:
        system_prompt = _doc_system_prompt(version=version)
    except FileNotFoundError as e:
        return {"loi": f"Lỗi cấu hình: {e}"}

    # ── Bước 5: Gọi LLM ──────────────────────────────────────────────────────
    try:
        phan_hoi_llm = call_llm(system_prompt=system_prompt, user_prompt=user_prompt)
    except Exception as e:
        _logger.error(f"[CHATBOT_SERVICE] Gọi LLM thất bại: {e}")
        return {"loi": f"LLM không phản hồi: {e}"}

    if isinstance(phan_hoi_llm, str) and phan_hoi_llm.startswith("[Lỗi"):
        return {"loi": phan_hoi_llm}

    elapsed_ms = int((time.time() - start_time) * 1000)

    # ── Bước 6 & 7: Xử lý phản hồi theo từng phiên bản prompt ────────────────
    if version in ("v1", "v2"):
        ket_qua_dict = _parse_json_llm(phan_hoi_llm)
        if ket_qua_dict and "ket_qua" in ket_qua_dict:
            ket_qua_goc = ket_qua_dict.get("ket_qua", [])
            ket_qua_sach = _loc_ket_qua_bija(ket_qua_goc, context)
            canh_bao_bia = len(ket_qua_goc) > len(ket_qua_sach)
            thong_bao = ket_qua_dict.get("thong_bao", phan_hoi_llm)
        else:
            ket_qua_sach = []
            for s in context:
                if s.get("ten_sach") and s["ten_sach"].lower() in phan_hoi_llm.lower():
                    ket_qua_sach.append({
                        "ten_sach": s["ten_sach"],
                        "tac_gia": s["tac_gia"],
                        "ly_do_goi_y": "Được đề cập trong phản hồi",
                        "con_hang": s["con_hang"],
                    })
            canh_bao_bia = False
            thong_bao = phan_hoi_llm

        return {
            "ket_qua": ket_qua_sach,
            "tong_so_ket_qua": len(ket_qua_sach),
            "thong_bao": thong_bao,
            "raw_text": phan_hoi_llm,
            "context_so_bo": len(context),
            "context_list": list(context),
            "thoi_gian_ms": elapsed_ms,
            "prompt_version": version,
            "canh_bao_bia": canh_bao_bia,
        }

    # ── Phiên bản v3 (JSON chuẩn bắt buộc) ──────────────────────────────────
    ket_qua_dict = _parse_json_llm(phan_hoi_llm)
    if ket_qua_dict is None:
        _logger.warning(
            "[CHATBOT_SERVICE] Parse JSON lần 1 thất bại — thử lại với yêu cầu bổ sung."
        )
        retry_prompt = (
            f"{user_prompt}\n\n"
            "[QUAN TRỌNG: Phản hồi trước của bạn không phải JSON hợp lệ. "
            "Hãy trả lời LẠI DUY NHẤT một đối tượng JSON theo đúng schema đã quy định, "
            "không kèm bất kỳ văn bản nào khác.]"
        )
        try:
            phan_hoi_llm_2 = call_llm(
                system_prompt=system_prompt,
                user_prompt=retry_prompt,
            )
            ket_qua_dict = _parse_json_llm(phan_hoi_llm_2)
            if ket_qua_dict:
                phan_hoi_llm = phan_hoi_llm_2
        except Exception:
            ket_qua_dict = None

        if ket_qua_dict is None:
            _logger.error("[CHATBOT_SERVICE] Parse JSON lần 2 vẫn thất bại.")
            return {
                "ket_qua": [],
                "tong_so_ket_qua": 0,
                "thong_bao": phan_hoi_llm,
                "raw_text": phan_hoi_llm,
                "context_so_bo": len(context),
                "context_list": list(context),
                "thoi_gian_ms": elapsed_ms,
                "prompt_version": version,
                "canh_bao_bia": True,
            }

    ket_qua_goc = ket_qua_dict.get("ket_qua", [])
    ket_qua_sach = _loc_ket_qua_bija(ket_qua_goc, context)
    so_bi_loai = len(ket_qua_goc) - len(ket_qua_sach)
    if so_bi_loai > 0:
        _logger.warning(
            f"[CHATBOT_SERVICE] Đã loại bỏ {so_bi_loai} sách LLM bịa khỏi kết quả cuối cùng."
        )

    thong_bao = ket_qua_dict.get("thong_bao", "")

    # Hậu xử lý đặc biệt khi câu hỏi có khả năng là tên riêng một cuốn sách cụ thể
    # (cờ co_the_la_ten_sach được đặt bởi _phat_hien_tra_cuu_ten_sach() trong rag_retriever.py)
    co_the_la_ten_sach = getattr(context, "co_the_la_ten_sach", False)
    
    # Kiểm tra an toàn: nếu câu hỏi thực chất là tìm kiếm chủ đề / thể loại thì không lọc tên
    cau_hoi_lower = cau_hoi.lower()
    la_tim_the_loai = any(tk in cau_hoi_lower for tk in [
        "sách", "gợi ý", "tìm", "kinh tế", "quản trị", "lập trình", "cntt",
        "công nghệ", "trí tuệ nhân tạo", "ai", "bảo mật", "an ninh mạng",
        "kỹ năng", "giao tiếp", "đáng đọc", "sách hay", "thể loại", "chủ đề"
    ])
    if la_tim_the_loai:
        co_the_la_ten_sach = False

    if co_the_la_ten_sach and ket_qua_sach:
        # Trong chế độ "tìm tên sách": loại bỏ sách chỉ khớp ngẫu nhiên vài từ trong tên
        # Yêu cầu diem_khop_ten >= 75% (cao hơn FUZZY_THRESHOLD=60 để loại false positive)
        # Ví dụ: "Vũ Khí Hoàn Hảo - Chiến Tranh..." khớp "chiến tranh" ≈ 60-65% → bị loại
        ket_qua_loc_ten = [s for s in ket_qua_sach if s.get("diem_khop_ten", 0) >= 75]
        if not ket_qua_loc_ten:
            # Sách trả về không khớp đủ tên → thư viện không có sách này
            ket_qua_sach = []
            cau_hoi_hien_thi = cau_hoi.strip().rstrip("?").strip()
            thong_bao = (
                f"Thư viện hiện chưa có sách '{cau_hoi_hien_thi}'. "
                "Bạn có thể tham khảo các sách cùng chủ đề khác nếu muốn."
            )
            _logger.info(
                f"[CHATBOT_SERVICE] '{cau_hoi[:50]}' → chế độ tên sách, "
                f"loại bỏ {len(ket_qua_sach)} sách khớp yếu (diem_khop_ten < 75%), "
                f"dùng thông báo cụ thể về sách chưa có trong kho."
            )
        else:
            ket_qua_sach = ket_qua_loc_ten

    if not ket_qua_sach and not thong_bao:
        if co_the_la_ten_sach:
            cau_hoi_hien_thi = cau_hoi.strip().rstrip("?").strip()
            thong_bao = (
                f"Thư viện hiện chưa có sách '{cau_hoi_hien_thi}'. "
                "Bạn có thể tham khảo các sách cùng chủ đề khác nếu muốn."
            )
        else:
            thong_bao = "Không có sách nào thực sự phù hợp với yêu cầu của bạn."

    tu_khoa_nhan_manh = ket_qua_dict.get("tu_khoa_nhan_manh", [])
    if not isinstance(tu_khoa_nhan_manh, list):
        tu_khoa_nhan_manh = []
    phan_tich_yeu_cau = ket_qua_dict.get("phan_tich_yeu_cau", "")

    return {
        "ket_qua": ket_qua_sach,
        "tong_so_ket_qua": len(ket_qua_sach),
        "thong_bao": thong_bao,
        "tu_khoa_nhan_manh": tu_khoa_nhan_manh,
        "phan_tich_yeu_cau": phan_tich_yeu_cau,
        "raw_text": phan_hoi_llm,
        "context_so_bo": len(context),
        "context_list": list(context),
        "thoi_gian_ms": elapsed_ms,
        "prompt_version": version,
        "canh_bao_bia": so_bi_loai > 0,
    }
