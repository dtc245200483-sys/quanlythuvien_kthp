from datetime import datetime, timezone

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Index, Integer, Numeric, Unicode, UnicodeText, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class User(Base):
    __tablename__ = "Users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(Unicode(50), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(Unicode(255), nullable=False)
    ho_ten: Mapped[str] = mapped_column(Unicode(255), nullable=False)
    email: Mapped[str | None] = mapped_column(Unicode(255), nullable=True)
    so_dien_thoai: Mapped[str | None] = mapped_column(Unicode(20), nullable=True)
    role: Mapped[str] = mapped_column(Unicode(20), nullable=False)
    reader_id: Mapped[str | None] = mapped_column(
        Unicode(20),
        ForeignKey("Readers.ma"),
        nullable=True,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    __table_args__ = (
        CheckConstraint("role IN ('admin', 'librarian', 'reader')", name="ck_users_role"),
        Index(
            "uq_users_email",
            "email",
            unique=True,
            mssql_where=text("email IS NOT NULL"),
        ),
    )

    @property
    def role_display(self) -> str:
        return {
            "admin": "Quản trị viên",
            "librarian": "Thủ thư",
            "reader": "Độc giả",
        }.get(self.role, self.role)


class Book(Base):
    __tablename__ = "Books"

    ma: Mapped[str] = mapped_column(Unicode(20), primary_key=True)
    ten: Mapped[str] = mapped_column(Unicode(255), nullable=False)
    tacGia: Mapped[str] = mapped_column(Unicode(255), nullable=False)
    theLoai: Mapped[str] = mapped_column(Unicode(100), nullable=False)
    nxb: Mapped[str] = mapped_column(Unicode(255), nullable=False)
    namXb: Mapped[int] = mapped_column(Integer, nullable=False)
    soLuong: Mapped[int] = mapped_column(Integer, nullable=False)
    anhBia: Mapped[str] = mapped_column(Unicode(2048), nullable=False)
    tomTat: Mapped[str | None] = mapped_column(UnicodeText, nullable=True)
    theLoaiId: Mapped[str | None] = mapped_column(
        Unicode(20),
        ForeignKey("TheLoai.ma"),
        nullable=True,
    )
    nxbId: Mapped[str | None] = mapped_column(
        Unicode(20),
        ForeignKey("Nxb.ma"),
        nullable=True,
    )

    __table_args__ = (
        CheckConstraint("soLuong >= 0", name="ck_books_soluong"),
    )


class BookCopy(Base):
    __tablename__ = "BookCopies"

    copy_id: Mapped[str] = mapped_column(Unicode(50), primary_key=True)
    book_id: Mapped[str] = mapped_column(
        Unicode(20),
        ForeignKey("Books.ma"),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(Unicode(50), nullable=False, default="Có sẵn")

    __table_args__ = (
        CheckConstraint(
            "status IN ('Có sẵn', 'Đang mượn', 'Đang giữ chỗ', 'Hỏng', 'Mất')",
            name="ck_book_copies_status",
        ),
        Index("ix_book_copies_book_id", "book_id"),
        Index("ix_book_copies_book_id_status", "book_id", "status"),
    )


class LibraryConfig(Base):
    __tablename__ = "LibraryConfig"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    max_borrow_days: Mapped[int] = mapped_column(Integer, nullable=False)
    overdue_fine_points_per_day: Mapped[int] = mapped_column(Integer, nullable=False, default=2)
    overdue_fine_vnd_per_day_lecturer: Mapped[int] = mapped_column(
        Integer, nullable=False, default=5000
    )
    max_books_at_once: Mapped[int] = mapped_column(Integer, nullable=False)

    __table_args__ = (
        CheckConstraint("id = 1", name="ck_library_config_singleton"),
        CheckConstraint("max_borrow_days > 0", name="ck_library_config_max_borrow_days"),
        CheckConstraint(
            "overdue_fine_points_per_day >= 0",
            name="ck_library_config_points",
        ),
        CheckConstraint(
            "overdue_fine_vnd_per_day_lecturer >= 0",
            name="ck_library_config_fine_lecturer",
        ),
        CheckConstraint("max_books_at_once > 0", name="ck_library_config_max_books"),
    )


class AIConfig(Base):
    __tablename__ = "AIConfig"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    provider: Mapped[str] = mapped_column(Unicode(50), nullable=False)
    model: Mapped[str] = mapped_column(Unicode(100), nullable=False)
    api_key: Mapped[str] = mapped_column(Unicode(500), nullable=False)
    prompt_template: Mapped[str] = mapped_column(UnicodeText, nullable=False)

    __table_args__ = (
        CheckConstraint("id = 1", name="ck_ai_config_singleton"),
    )


class AuditLog(Base):
    __tablename__ = "AuditLog"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str | None] = mapped_column(Unicode(50), nullable=True)
    role: Mapped[str | None] = mapped_column(Unicode(20), nullable=True)
    action: Mapped[str] = mapped_column(Unicode(50), nullable=False)
    entity: Mapped[str] = mapped_column(Unicode(50), nullable=False)
    entity_id: Mapped[str | None] = mapped_column(Unicode(50), nullable=True)
    details: Mapped[str | None] = mapped_column(UnicodeText, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    __table_args__ = (
        Index("ix_audit_log_created_at", "created_at"),
    )


class Reader(Base):
    __tablename__ = "Readers"

    ma: Mapped[str] = mapped_column(Unicode(20), primary_key=True)
    hoTen: Mapped[str] = mapped_column(Unicode(255), nullable=False)
    email: Mapped[str] = mapped_column(Unicode(255), nullable=False)
    soDienThoai: Mapped[str] = mapped_column(Unicode(20), nullable=False)
    loaiDocGia: Mapped[str] = mapped_column(Unicode(50), nullable=False)
    trangThaiThe: Mapped[str] = mapped_column(Unicode(20), nullable=False)
    diem_svnet: Mapped[int] = mapped_column(Integer, nullable=False, default=100)
    ngayTao: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    __table_args__ = (
        CheckConstraint("LENGTH(LTRIM(ma)) > 0", name="ck_readers_ma_not_empty"),
        CheckConstraint("LENGTH(LTRIM(hoTen)) > 0", name="ck_readers_ho_ten_not_empty"),
        CheckConstraint("LENGTH(LTRIM(email)) > 0", name="ck_readers_email_not_empty"),
        CheckConstraint("LENGTH(LTRIM(soDienThoai)) > 0", name="ck_readers_phone_not_empty"),
        CheckConstraint(
            "loaiDocGia IN ('sinh_vien', 'giang_vien')",
            name="ck_readers_loai",
        ),
        CheckConstraint(
            "trangThaiThe IN ('hoat_dong', 'khoa')",
            name="ck_readers_trang_thai",
        ),
    )


class BorrowSlip(Base):
    __tablename__ = "BorrowSlips"

    ma_phieu: Mapped[str] = mapped_column(Unicode(20), primary_key=True)
    ma_doc_gia: Mapped[str] = mapped_column(Unicode(20), nullable=False)
    ngay_muon: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    han_tra: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    ngay_tra: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    trang_thai: Mapped[str] = mapped_column(Unicode(20), nullable=False)
    so_lan_gia_han: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    __table_args__ = (
        CheckConstraint(
            "trang_thai IN ('dang_muon', 'da_tra')",
            name="ck_borrow_slips_status",
        ),
        CheckConstraint("so_lan_gia_han >= 0", name="ck_borrow_slips_renew_count"),
        Index("ix_borrow_slips_ma_doc_gia", "ma_doc_gia"),
    )


class BorrowDetail(Base):
    __tablename__ = "BorrowDetails"

    ma_phieu: Mapped[str] = mapped_column(Unicode(20), primary_key=True)
    ma_sach: Mapped[str] = mapped_column(Unicode(20), nullable=False)
    so_luong: Mapped[int] = mapped_column(Integer, nullable=False)
    ngay_tra_chi_tiet: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    copy_id: Mapped[str] = mapped_column(
        Unicode(50),
        ForeignKey("BookCopies.copy_id"),
        primary_key=True,
    )

    __table_args__ = (
        CheckConstraint("so_luong > 0", name="ck_borrow_details_so_luong"),
        Index("ix_borrow_details_ma_sach", "ma_sach"),
    )


class FineHistory(Base):
    __tablename__ = "FineHistory"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ma_phieu: Mapped[str] = mapped_column(Unicode(20), nullable=False)
    ma_doc_gia: Mapped[str] = mapped_column(Unicode(20), nullable=False)
    so_ngay_qua_han: Mapped[int] = mapped_column(Integer, nullable=False)
    so_diem: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    so_tien: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    da_thu: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    ngay_thu: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    ngay_tinh: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    __table_args__ = (
        CheckConstraint("so_ngay_qua_han >= 0", name="ck_fine_history_days"),
        CheckConstraint("so_diem >= 0", name="ck_fine_history_points"),
        CheckConstraint("so_tien >= 0", name="ck_fine_history_amount"),
        Index("ix_fine_history_ma_phieu", "ma_phieu"),
    )


class TheLoai(Base):
    __tablename__ = "TheLoai"

    ma: Mapped[str] = mapped_column(Unicode(20), primary_key=True)
    ten: Mapped[str] = mapped_column(Unicode(100), nullable=False)

    __table_args__ = (
        CheckConstraint("LENGTH(LTRIM(ma)) > 0", name="ck_the_loai_ma_not_empty"),
        CheckConstraint("LENGTH(LTRIM(ten)) > 0", name="ck_the_loai_ten_not_empty"),
    )


class Nxb(Base):
    __tablename__ = "Nxb"

    ma: Mapped[str] = mapped_column(Unicode(20), primary_key=True)
    ten: Mapped[str] = mapped_column(Unicode(255), nullable=False)

    __table_args__ = (
        CheckConstraint("LENGTH(LTRIM(ma)) > 0", name="ck_nxb_ma_not_empty"),
        CheckConstraint("LENGTH(LTRIM(ten)) > 0", name="ck_nxb_ten_not_empty"),
    )


class YeuCau(Base):
    __tablename__ = "YeuCau"

    ma_yeu_cau: Mapped[str] = mapped_column(Unicode(20), primary_key=True)
    loai: Mapped[str] = mapped_column(Unicode(20), nullable=False)
    ma_doc_gia: Mapped[str] = mapped_column(Unicode(20), nullable=False)
    ma_phieu: Mapped[str | None] = mapped_column(Unicode(20), nullable=True)
    items: Mapped[str] = mapped_column(UnicodeText, nullable=False)
    so_ngay_muon: Mapped[int | None] = mapped_column(Integer, nullable=True)
    trang_thai: Mapped[str] = mapped_column(Unicode(20), nullable=False)
    ngay_xu_ly: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    ngay_tao: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    __table_args__ = (
        CheckConstraint(
            "loai IN ('MUON', 'TRA', 'GIA_HAN', 'DAT_TRUOC')",
            name="ck_yeu_cau_loai",
        ),
        CheckConstraint(
            "so_ngay_muon IS NULL OR so_ngay_muon >= 1",
            name="ck_yeu_cau_so_ngay_muon",
        ),
        CheckConstraint(
            "trang_thai IN ('CHO_XU_LY', 'DA_DUYET', 'TU_CHOI')",
            name="ck_yeu_cau_trang_thai",
        ),
        Index("ix_yeu_cau_ma_doc_gia", "ma_doc_gia"),
    )


class DatTruoc(Base):
    __tablename__ = "DatTruoc"

    ma_dat: Mapped[str] = mapped_column(Unicode(20), primary_key=True)
    ma_sach: Mapped[str] = mapped_column(
        Unicode(20),
        ForeignKey("Books.ma"),
        nullable=False,
    )
    ma_doc_gia: Mapped[str] = mapped_column(
        Unicode(20),
        ForeignKey("Readers.ma"),
        nullable=False,
    )
    ngay_dat: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    trang_thai: Mapped[str] = mapped_column(Unicode(20), nullable=False)
    ngay_xu_ly: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    copy_id: Mapped[str | None] = mapped_column(
        Unicode(50),
        ForeignKey("BookCopies.copy_id"),
        nullable=True,
    )
    han_nhan: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    __table_args__ = (
        CheckConstraint(
            "trang_thai IN ('CHO_XU_LY', 'SAN_SANG', 'DA_MUON', 'HUY')",
            name="ck_dat_truoc_trang_thai",
        ),
        Index(
            "uq_dat_truoc_active",
            "ma_sach",
            "ma_doc_gia",
            unique=True,
            mssql_where=text("trang_thai IN ('CHO_XU_LY', 'SAN_SANG')"),
        ),
        Index("ix_dat_truoc_ma_sach", "ma_sach"),
        Index("ix_dat_truoc_ma_doc_gia", "ma_doc_gia"),
    )


class DocThongBao(Base):
    __tablename__ = "DocThongBao"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ma_doc_gia: Mapped[str] = mapped_column(Unicode(20), nullable=False)
    nguon_id: Mapped[str] = mapped_column(Unicode(100), nullable=False)
    da_doc: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    ngay_doc: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    __table_args__ = (
        UniqueConstraint("ma_doc_gia", "nguon_id", name="uq_doc_thong_bao_nguon"),
    )


class AnThongBao(Base):
    __tablename__ = "AnThongBao"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ma_doc_gia: Mapped[str] = mapped_column(Unicode(20), nullable=False)
    nguon_id: Mapped[str] = mapped_column(Unicode(100), nullable=False)
    ngay_an: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    __table_args__ = (
        UniqueConstraint("ma_doc_gia", "nguon_id", name="uq_an_thong_bao_nguon"),
    )
