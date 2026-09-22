import os
import pyodbc
import re
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from ..audit import write_audit_log
from ..config import BACKUP_DIR, DB_NAME, DB_SERVER, ODBC_DRIVER
from ..database import engine, get_db
from ..deps import require_roles
from ..models import AIConfig, AuditLog, LibraryConfig
from ..schemas import (
    AIConfigOut,
    AIConfigUpdate,
    AuditLogOut,
    BackupOut,
    LibraryConfigOut,
    LibraryConfigUpdate,
    RestoreRequest,
)
router = APIRouter(prefix="/api/admin", tags=["admin"])


def _mask_api_key(key: str) -> str:
    if not key:
        return ""
    if len(key) <= 8:
        return "*" * len(key)
    return key[:4] + "*" * (len(key) - 8) + key[-4:]


def _ai_config_out(cfg: AIConfig) -> AIConfigOut:
    return AIConfigOut(
        provider=cfg.provider,
        model=cfg.model,
        api_key_masked=_mask_api_key(cfg.api_key),
        has_api_key=bool(cfg.api_key),
        prompt_template=cfg.prompt_template,
    )


@router.get("/config/library", response_model=LibraryConfigOut)
def get_library_config(
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin", "librarian")),
) -> LibraryConfigOut:
    cfg = db.get(LibraryConfig, 1)
    if cfg is None:
        raise HTTPException(status_code=404, detail="Chưa có cấu hình thư viện.")
    return cfg


@router.put("/config/library", response_model=LibraryConfigOut)
def update_library_config(
    body: LibraryConfigUpdate,
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin")),
) -> LibraryConfigOut:
    cfg = db.get(LibraryConfig, 1)
    if cfg is None:
        raise HTTPException(status_code=404, detail="Chưa có cấu hình thư viện.")
    cfg.max_borrow_days = body.max_borrow_days
    cfg.overdue_fine_points_per_day = body.overdue_fine_points_per_day
    cfg.overdue_fine_vnd_per_day_lecturer = body.overdue_fine_vnd_per_day_lecturer
    cfg.max_books_at_once = body.max_books_at_once
    write_audit_log(
        db,
        user,
        "UPDATE_LIBRARY_CONFIG",
        "CONFIG",
        entity_id="1",
        details=body.model_dump_json(),
    )
    db.commit()
    db.refresh(cfg)
    return cfg


@router.get("/config/ai", response_model=AIConfigOut)
def get_ai_config(
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin")),
) -> AIConfigOut:
    cfg = db.get(AIConfig, 1)
    if cfg is None:
        raise HTTPException(status_code=404, detail="Chưa có cấu hình AI.")
    return _ai_config_out(cfg)


@router.put("/config/ai", response_model=AIConfigOut)
def update_ai_config(
    body: AIConfigUpdate,
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin")),
) -> AIConfigOut:
    cfg = db.get(AIConfig, 1)
    if cfg is None:
        raise HTTPException(status_code=404, detail="Chưa có cấu hình AI.")
    data = body.model_dump(exclude_unset=True)
    if "api_key" in data:
        cfg.api_key = data["api_key"]
    for field in ("provider", "model", "prompt_template"):
        if field in data:
            setattr(cfg, field, data[field])
    write_audit_log(
        db,
        user,
        "UPDATE_AI_CONFIG",
        "CONFIG",
        entity_id="1",
        details=",".join(data.keys()),
    )
    db.commit()
    db.refresh(cfg)
    return _ai_config_out(cfg)


@router.get("/audit-logs", response_model=list[AuditLogOut])
def list_audit_logs(
    limit: int = Query(100, ge=1, le=500),
    action: str | None = Query(None, max_length=50),
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin")),
) -> list[AuditLogOut]:
    query = db.query(AuditLog)
    if action:
        query = query.filter(AuditLog.action == action)
    return query.order_by(AuditLog.id.desc()).limit(limit).all()


@router.post("/backup", response_model=BackupOut)
def backup_database(
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin")),
) -> BackupOut:
    if not re.fullmatch(r"[A-Za-z0-9_]+", DB_NAME):
        raise HTTPException(status_code=500, detail="Tên database cấu hình không hợp lệ.")
    backup_dir = BACKUP_DIR
    if not backup_dir:
        with engine.connect() as conn:
            backup_dir = conn.execute(
                text("SELECT CAST(SERVERPROPERTY('InstanceDefaultBackupPath') AS NVARCHAR(500))")
            ).scalar()
    if not backup_dir:
        raise HTTPException(status_code=500, detail="Không xác định được thư mục backup.")
    os.makedirs(backup_dir, exist_ok=True)
    filename = f"{DB_NAME}_{datetime.now():%Y%m%d_%H%M%S}.bak"
    path = os.path.join(backup_dir, filename)
    path_sql = path.replace("'", "''")
    conn = None
    try:
        conn = pyodbc.connect(
            f"DRIVER={{{ODBC_DRIVER}}};SERVER={DB_SERVER};DATABASE={DB_NAME};"
            "Trusted_Connection=Yes;TrustServerCertificate=Yes",
            autocommit=True,
        )
        cursor = conn.cursor()
        cursor.execute(f"BACKUP DATABASE [{DB_NAME}] TO DISK = N'{path_sql}'")
        while cursor.nextset():
            pass
        cursor.close()
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Sao lưu CSDL thất bại: {exc}",
        )
    finally:
        if conn is not None:
            conn.close()
    write_audit_log(
        db,
        user,
        "BACKUP_DATABASE",
        "DATABASE",
        entity_id=filename,
        details=path,
    )
    db.commit()
    return BackupOut(message="Đã sao lưu cơ sở dữ liệu.", path=path)


@router.post("/restore")
def restore_database(
    body: RestoreRequest,
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin")),
):
    path = body.file_path
    if not os.path.isfile(path) or not path.lower().endswith(".bak"):
        raise HTTPException(
            status_code=404,
            detail="File backup không tồn tại hoặc không phải .bak.",
        )
    if not re.fullmatch(r"[A-Za-z0-9_]+", DB_NAME):
        raise HTTPException(status_code=500, detail="Tên database cấu hình không hợp lệ.")

    path_sql = path.replace("'", "''")
    write_audit_log(
        db,
        user,
        "RESTORE_DATABASE",
        "DATABASE",
        entity_id=os.path.basename(path),
        details=path,
    )
    db.commit()

    conn = None
    try:
        conn = pyodbc.connect(
            f"DRIVER={{{ODBC_DRIVER}}};SERVER={DB_SERVER};DATABASE=master;"
            "Trusted_Connection=Yes;TrustServerCertificate=Yes",
            autocommit=True,
        )
        cursor = conn.cursor()
        cursor.execute(f"ALTER DATABASE [{DB_NAME}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE")
        while cursor.nextset():
            pass
        cursor.execute(f"RESTORE DATABASE [{DB_NAME}] FROM DISK = N'{path_sql}' WITH REPLACE")
        while cursor.nextset():
            pass
        cursor.execute(f"ALTER DATABASE [{DB_NAME}] SET MULTI_USER")
        while cursor.nextset():
            pass
        cursor.close()
    except Exception as exc:
        try:
            if conn is not None:
                cursor = conn.cursor()
                cursor.execute(f"ALTER DATABASE [{DB_NAME}] SET MULTI_USER")
                while cursor.nextset():
                    pass
                cursor.close()
        except Exception:
            pass
        raise HTTPException(
            status_code=500,
            detail=f"Phục hồi CSDL thất bại: {exc}",
        )
    finally:
        if conn is not None:
            conn.close()
    return {"message": "Đã phục hồi CSDL từ file backup.", "path": path}


# ─────────────────────────────────────────────────────────────────────────────
# Endpoint đồng bộ toàn bộ sách sang Vector Store (Admin only)
# ─────────────────────────────────────────────────────────────────────────────

@router.post("/dong-bo-vector-store")
def dong_bo_vector_store(
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin")),
):
    """
    Đồng bộ lại TOÀN BỘ sách từ CSDL chính sang Vector Store.

    Dùng cho trường hợp:
    - Import hàng loạt sách mới mà chưa tự động sync
    - Vector Store bị lỗi cần build lại từ đầu
    - Kiểm tra tính nhất quán giữa CSDL và VS

    Chỉ Admin được gọi endpoint này.
    """
    import sys
    from pathlib import Path

    # Thêm root vào sys.path để import chatbotAI
    _app_root = Path(__file__).resolve().parent.parent.parent.parent
    if str(_app_root) not in sys.path:
        sys.path.insert(0, str(_app_root))

    try:
        from chatbotAI.index_sach import dong_bo_toan_bo
        from chatbotAI.vector_store import VectorStore
        from ..models import Book

        # Lấy toàn bộ sách từ CSDL chính
        tat_ca_sach = db.query(Book).all()

        danh_sach = [
            {
                "ma_sach": s.ma,
                "ten_sach": s.ten,
                "tac_gia": s.tacGia,
                "tom_tat": s.tomTat or "",
                "the_loai": s.theLoai or "",
                "con_hang": s.soLuong > 0,
            }
            for s in tat_ca_sach
        ]

        dong_bo_toan_bo(danh_sach)

        vs = VectorStore()
        so_luong_vs = vs.dem_so_luong()

        write_audit_log(
            db,
            user,
            "SYNC_VECTOR_STORE",
            "SYSTEM",
            details=f"Đồng bộ {len(danh_sach)} sách → VS có {so_luong_vs} entries",
        )
        db.commit()

        return {
            "message": "Đồng bộ Vector Store hoàn tất.",
            "so_sach_tu_csdl": len(danh_sach),
            "so_sach_trong_vs": so_luong_vs,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Đồng bộ Vector Store thất bại: {e}",
        )


@router.post("/repair-book-copies")
def repair_book_copies(
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin")),
):
    """
    Quét và sửa các BookCopy bị kẹt ở trạng thái 'Đang mượn'
    mà không có BorrowDetail active tương ứng.
    Đồng thời đồng bộ lại soLuong trong bảng Books.
    """
    from ..models import Book, BookCopy, BorrowDetail, BorrowSlip, DatTruoc

    dang_muon_copies = (
        db.query(BookCopy).filter(BookCopy.status == "Đang mượn").all()
    )

    fixed_copies = 0
    for copy in dang_muon_copies:
        active_borrow = (
            db.query(BorrowDetail)
            .join(BorrowSlip, BorrowSlip.ma_phieu == BorrowDetail.ma_phieu)
            .filter(
                BorrowDetail.copy_id == copy.copy_id,
                BorrowDetail.ngay_tra_chi_tiet.is_(None),
                BorrowSlip.trang_thai == "dang_muon",
            )
            .first()
        )
        reserved = (
            db.query(DatTruoc)
            .filter(
                DatTruoc.copy_id == copy.copy_id,
                DatTruoc.trang_thai.in_(["CHO_XU_LY", "SAN_SANG"]),
            )
            .first()
        )
        if active_borrow is None and reserved is None:
            copy.status = "Có sẵn"
            fixed_copies += 1

    # Đồng bộ soLuong = số copy "Có sẵn"
    synced_books = 0
    all_books = db.query(Book).all()
    for book in all_books:
        co_san = (
            db.query(BookCopy)
            .filter(BookCopy.book_id == book.ma, BookCopy.status == "Có sẵn")
            .count()
        )
        if book.soLuong != co_san:
            book.soLuong = co_san
            synced_books += 1

    write_audit_log(
        db,
        user,
        "REPAIR_BOOK_COPIES",
        "SYSTEM",
        details=f"fixed_copies={fixed_copies}; synced_books={synced_books}",
    )
    db.commit()

    return {
        "message": "Sửa dữ liệu BookCopies hoàn tất.",
        "fixed_copies": fixed_copies,
        "synced_books": synced_books,
    }
