import secrets
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..audit import write_audit_log
from ..database import get_db
from ..deps import require_roles
from ..models import Book, BorrowDetail, BorrowSlip, DatTruoc, LibraryConfig, Reader
from ..schemas import ReservationCreate, ReservationOut

router = APIRouter(prefix="/api/reservations", tags=["reservations"])

RESERVATION_STATUSES = ("CHO_XU_LY", "SAN_SANG", "DA_MUON", "HUY")


def _available_count(db: Session, book: Book) -> int:
    from ..models import BookCopy
    return (
        db.query(BookCopy)
        .filter(BookCopy.book_id == book.ma, BookCopy.status == "Có sẵn")
        .count()
    )


def _out(db: Session, res: DatTruoc) -> ReservationOut:
    book = db.get(Book, res.ma_sach)
    
    queue_pos = None
    if res.trang_thai in ["CHO_XU_LY", "CHO_XEP_HANG", "SAN_SANG"]:
        active_reservations = (
            db.query(DatTruoc.ma_dat)
            .filter(
                DatTruoc.ma_sach == res.ma_sach,
                DatTruoc.trang_thai.in_(["CHO_XU_LY", "CHO_XEP_HANG", "SAN_SANG"]),
            )
            .order_by(DatTruoc.ngay_dat.asc(), DatTruoc.ma_dat.asc())
            .all()
        )
        queue_pos = next(
            (idx + 1 for idx, (ma,) in enumerate(active_reservations) if ma == res.ma_dat),
            None,
        )
        
    return ReservationOut(
        ma_dat=res.ma_dat,
        ma_sach=res.ma_sach,
        ten_sach=book.ten if book is not None else "",
        ma_doc_gia=res.ma_doc_gia,
        ngay_dat=res.ngay_dat,
        trang_thai=res.trang_thai,
        queue_position=queue_pos,
    )


def _generate_ma_dat(db: Session) -> str:
    for _ in range(5):
        candidate = (
            "RV"
            + datetime.now().strftime("%Y%m%d%H%M%S")
            + f"{secrets.randbelow(1000):03d}"
        )
        if db.get(DatTruoc, candidate) is None:
            return candidate
    raise HTTPException(status_code=500, detail="Không tạo được mã đặt trước, thử lại.")


@router.get("", response_model=list[ReservationOut])
def list_reservations(
    trangThai: str | None = Query(None, max_length=20),
    db: Session = Depends(get_db),
    user=Depends(require_roles("reader", "librarian")),
) -> list[ReservationOut]:
    query = db.query(DatTruoc)
    if user.role == "reader":
        if not user.reader_id:
            raise HTTPException(
                status_code=403,
                detail="Tài khoản chưa liên kết với độc giả.",
            )
        query = query.filter(DatTruoc.ma_doc_gia == user.reader_id)
    if trangThai:
        if trangThai not in RESERVATION_STATUSES:
            raise HTTPException(status_code=422, detail="trangThai không hợp lệ.")
        query = query.filter(DatTruoc.trang_thai == trangThai)
    rows = query.order_by(DatTruoc.ngay_dat.asc(), DatTruoc.ma_dat.asc()).all()
    return [_out(db, row) for row in rows]


@router.post("", response_model=ReservationOut)
def create_reservation(
    body: ReservationCreate,
    db: Session = Depends(get_db),
    user=Depends(require_roles("reader")),
) -> ReservationOut:
    if user.role == "reader" and not user.reader_id:
        raise HTTPException(
            status_code=403,
            detail="Tài khoản chưa liên kết với độc giả.",
        )
    reader = db.get(Reader, user.reader_id)
    if reader is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy độc giả.")
    if reader.trangThaiThe != "hoat_dong":
        raise HTTPException(status_code=400, detail="Thẻ độc giả đang bị khoá.")

    book = db.get(Book, body.ma_sach)
    if book is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy sách.")
    if _available_count(db, book) > 0:
        raise HTTPException(status_code=400, detail="Sách còn, không cần đặt trước")

    active = (
        db.query(DatTruoc)
        .filter(
            DatTruoc.ma_sach == body.ma_sach,
            DatTruoc.ma_doc_gia == user.reader_id,
            DatTruoc.trang_thai.in_(["CHO_XU_LY", "SAN_SANG"]),
        )
        .first()
    )
    if active is not None:
        raise HTTPException(status_code=409, detail="Bạn đã đặt trước sách này.")

    ma_dat = _generate_ma_dat(db)
    res = DatTruoc(
        ma_dat=ma_dat,
        ma_sach=body.ma_sach,
        ma_doc_gia=user.reader_id,
        ngay_dat=datetime.now(),
        trang_thai="CHO_XU_LY",
        ngay_xu_ly=None,
    )
    db.add(res)
    write_audit_log(
        db,
        user,
        "CREATE_RESERVATION",
        "RESERVATION",
        entity_id=ma_dat,
        details=f"ma_sach={body.ma_sach}",
    )
    db.commit()
    db.refresh(res)
    return _out(db, res)


@router.put("/{ma_dat}/cancel", response_model=ReservationOut)
def cancel_reservation(
    ma_dat: str,
    db: Session = Depends(get_db),
    user=Depends(require_roles("reader", "librarian")),
) -> ReservationOut:
    res = db.get(DatTruoc, ma_dat)
    if res is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy đặt trước.")
    if user.role == "reader" and res.ma_doc_gia != user.reader_id:
        raise HTTPException(status_code=404, detail="Không tìm thấy đặt trước.")
    if user.role == "reader" and res.trang_thai != "CHO_XU_LY":
        raise HTTPException(
            status_code=400,
            detail="Chỉ huỷ được đặt trước đang chờ xử lý.",
        )
    if res.trang_thai not in ("CHO_XU_LY", "SAN_SANG"):
        raise HTTPException(
            status_code=400,
            detail="Chỉ huỷ được đặt trước đang chờ hoặc sẵn sàng.",
        )
    res.trang_thai = "HUY"
    res.ngay_xu_ly = datetime.now()
    write_audit_log(
        db,
        user,
        "CANCEL_RESERVATION",
        "RESERVATION",
        entity_id=ma_dat,
    )
    db.commit()
    db.refresh(res)
    return _out(db, res)


@router.delete("/me/{ma_dat}")
def delete_my_reservation_history(
    ma_dat: str,
    db: Session = Depends(get_db),
    user=Depends(require_roles("reader", "librarian")),
):
    if user.role == "reader" and not user.reader_id:
        raise HTTPException(
            status_code=403,
            detail="Tài khoản chưa liên kết với độc giả.",
        )
    res = db.get(DatTruoc, ma_dat)
    if res is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy đặt trước.")
    if user.role == "reader" and res.ma_doc_gia != user.reader_id:
        raise HTTPException(status_code=404, detail="Không tìm thấy đặt trước.")
    if res.trang_thai in ("CHO_XU_LY", "SAN_SANG"):
        raise HTTPException(
            status_code=400,
            detail="Chỉ xoá được đặt trước đã xử lý (HUY/DA_MUON).",
        )
    write_audit_log(
        db,
        user,
        "DELETE_RESERVATION_HISTORY",
        "RESERVATION",
        entity_id=ma_dat,
        details=f"trang_thai={res.trang_thai}",
    )
    db.delete(res)
    db.commit()
    return {"message": "Đã xoá lịch sử đặt trước.", "so_phieu_da_xoa": 1}


@router.delete("/me")
def delete_all_my_reservation_history(
    db: Session = Depends(get_db),
    user=Depends(require_roles("reader", "librarian")),
):
    if user.role == "reader" and not user.reader_id:
        raise HTTPException(
            status_code=403,
            detail="Tài khoản chưa liên kết với độc giả.",
        )
    query = db.query(DatTruoc).filter(DatTruoc.trang_thai.in_(["HUY", "DA_MUON"]))
    if user.role == "reader":
        query = query.filter(DatTruoc.ma_doc_gia == user.reader_id)
    targets = query.all()
    count = len(targets)
    for res in targets:
        db.delete(res)
    write_audit_log(
        db,
        user,
        "DELETE_RESERVATION_HISTORY_ALL",
        "RESERVATION",
        entity_id="ALL",
        details=f"so_phieu_da_xoa={count}",
    )
    db.commit()
    return {
        "message": "Đã xoá lịch sử các đặt trước đã xử lý.",
        "so_phieu_da_xoa": count,
    }


@router.put("/{ma_dat}/borrow", response_model=ReservationOut)
def borrow_from_reservation(
    ma_dat: str,
    db: Session = Depends(get_db),
    user=Depends(require_roles("librarian")),
) -> ReservationOut:
    res = db.get(DatTruoc, ma_dat, with_for_update=True)
    if res is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy đặt trước.")
    if res.trang_thai != "SAN_SANG":
        raise HTTPException(
            status_code=400,
            detail="Chỉ lập phiếu mượn khi đặt trước ở trạng thái sẵn sàng.",
        )
    reader = db.get(Reader, res.ma_doc_gia, with_for_update=True)
    if reader is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy độc giả.")
    if reader.trangThaiThe != "hoat_dong":
        raise HTTPException(status_code=400, detail="Thẻ độc giả đang bị khoá.")
    book = db.get(Book, res.ma_sach, with_for_update=True)
    if book is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy sách.")
    if book.soLuong <= 0:
        raise HTTPException(status_code=400, detail="Sách không còn bản để mượn.")
    cfg = db.get(LibraryConfig, 1)
    if cfg is None:
        raise HTTPException(status_code=500, detail="Chưa có cấu hình thư viện.")

    from ..models import BookCopy
    copy = None
    if res.copy_id:
        copy = db.query(BookCopy).with_for_update().get(res.copy_id)
        if copy is None or copy.status != "Đang giữ chỗ":
            raise HTTPException(status_code=400, detail="Bản vật lý không sẵn sàng hoặc đã bị lỗi trạng thái.")
    else:
        raise HTTPException(status_code=400, detail="Phiếu đặt trước không có bản sao vật lý hợp lệ.")

    now = datetime.now()
    ma_phieu = "PM" + res.ma_dat[2:]
    suffix = 0
    while db.get(BorrowSlip, ma_phieu) is not None:
        suffix += 1
        ma_phieu = "PM" + res.ma_dat[2:] + str(suffix)

    slip = BorrowSlip(
        ma_phieu=ma_phieu,
        ma_doc_gia=res.ma_doc_gia,
        ngay_muon=now,
        han_tra=now + timedelta(days=cfg.max_borrow_days),
        trang_thai="dang_muon",
        so_lan_gia_han=0,
    )
    db.add(slip)
    db.add(
        BorrowDetail(
            ma_phieu=ma_phieu,
            ma_sach=res.ma_sach,
            so_luong=1,
            ngay_tra_chi_tiet=None,
            copy_id=copy.copy_id,
        )
    )
    copy.status = "Đang mượn"
    book.soLuong -= 1
    res.trang_thai = "DA_MUON"
    res.ngay_xu_ly = now
    write_audit_log(
        db,
        user,
        "BORROW_FROM_RESERVATION",
        "RESERVATION",
        entity_id=res.ma_dat,
        details=f"ma_phieu={ma_phieu}",
    )
    db.commit()
    db.refresh(res)
    return _out(db, res)


@router.put("/{ma_dat}/fulfill", response_model=ReservationOut)
def fulfill_reservation(
    ma_dat: str,
    db: Session = Depends(get_db),
    user=Depends(require_roles("librarian")),
) -> ReservationOut:
    res = db.get(DatTruoc, ma_dat, with_for_update=True)
    if res is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy đặt trước.")
    if res.trang_thai != "CHO_XU_LY":
        raise HTTPException(
            status_code=400,
            detail="Chỉ chuyển SAN_SANG từ trạng thái chờ xử lý.",
        )
    book = db.get(Book, res.ma_sach, with_for_update=True)
    if book is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy sách.")

    first_pending = (
        db.query(DatTruoc)
        .filter(
            DatTruoc.ma_sach == res.ma_sach,
            DatTruoc.trang_thai == "CHO_XU_LY",
        )
        .order_by(DatTruoc.ngay_dat.asc(), DatTruoc.ma_dat.asc())
        .first()
    )
    if first_pending and first_pending.ma_dat != res.ma_dat:
        raise HTTPException(
            status_code=400,
            detail=f"Phải xử lý theo thứ tự hàng đợi (FIFO). Phiếu {first_pending.ma_dat} đang ở vị trí 1.",
        )
    
    from ..models import BookCopy
    copy = (
        db.query(BookCopy)
        .with_for_update()
        .filter(BookCopy.book_id == book.ma, BookCopy.status == "Có sẵn")
        .first()
    )
    if not copy:
        raise HTTPException(
            status_code=400,
            detail="Chưa có sách để sẵn sàng — chờ độc giả trả sách về.",
        )
    
    res.copy_id = copy.copy_id
    copy.status = "Đang giữ chỗ"
    res.trang_thai = "SAN_SANG"
    now = datetime.now()
    res.ngay_xu_ly = now
    res.han_nhan = now + timedelta(hours=48)
    write_audit_log(
        db,
        user,
        "FULFILL_RESERVATION",
        "RESERVATION",
        entity_id=ma_dat,
        details=f"ma_sach={res.ma_sach}",
    )
    db.commit()
    db.refresh(res)
    return _out(db, res)


@router.post("/cleanup-expired")
def cleanup_expired(db: Session = Depends(get_db)):
    """
    Cron job endpoint: Scan and cancel reservations that have expired (passed han_nhan)
    """
    now = datetime.now()
    expired = (
        db.query(DatTruoc)
        .filter(DatTruoc.trang_thai == "SAN_SANG", DatTruoc.han_nhan < now)
        .with_for_update(skip_locked=True)
        .all()
    )
    
    count = 0
    from ..models import BookCopy
    for res in expired:
        res.trang_thai = "HUY"
        if res.copy_id:
            copy = db.get(BookCopy, res.copy_id, with_for_update=True)
            if copy and copy.status == "Đang giữ chỗ":
                pending = (
                    db.query(DatTruoc)
                    .filter(DatTruoc.ma_sach == res.ma_sach, DatTruoc.trang_thai == "CHO_XU_LY")
                    .order_by(DatTruoc.ngay_dat.asc(), DatTruoc.ma_dat.asc())
                    .with_for_update(skip_locked=True)
                    .first()
                )
                if pending:
                    pending.trang_thai = "SAN_SANG"
                    pending.copy_id = copy.copy_id
                    pending.ngay_xu_ly = now
                    pending.han_nhan = now + timedelta(hours=48)
                else:
                    copy.status = "Có sẵn"
        count += 1
    
    db.commit()
    return {"message": "Success", "cleaned": count}
