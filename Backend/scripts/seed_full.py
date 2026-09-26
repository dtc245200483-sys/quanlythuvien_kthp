"""
seed_full.py — Script khởi tạo dữ liệu mẫu toàn diện (All-in-One Seed).
Dành cho đồ án: Hệ thống quản lý thư viện tích hợp AI (FastAPI + SQL Server + ChromaDB).

Đặc điểm:
1. Chạy hoàn toàn Offline / Standalone (dùng SQLAlchemy trực tiếp, KHÔNG cần Backend server bật trước).
2. Tự động sinh đầy đủ 5 tài khoản mẫu với mật khẩu hash Bcrypt:
   - Admin:      admin / admin1
   - Thủ thư:    librarian / librarian1
   - Độc giả:    reader / reader1
   - Độc giả 1:  docgia1 / docgia1 (liên kết mã DG001)
   - Độc giả 2:  docgia2 / docgia2 (liên kết mã DG002)
3. Nạp đầy đủ cấu hình hệ thống: LibraryConfig, AIConfig.
4. Nạp danh mục Thể loại, Nhà xuất bản và 63 cuốn sách thực tế từ books_catalog.json.
5. Nạp độc giả mẫu, các kịch bản mượn/trả/quá hạn/phạt điểm SVNET/đặt trước.
6. Tự động đồng bộ toàn bộ sách sang ChromaDB Vector Store phục vụ Chatbot AI.
7. Idempotent: chạy lại nhiều lần an toàn, không trùng lặp dữ liệu.

Cách chạy:
    cd Backend
    python scripts/seed_full.py
"""

import os
import sys
import json
from datetime import datetime, timedelta

# Đảm bảo hiển thị tiếng Việt trên Windows console
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# Thêm thư mục Backend và App Root vào sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(CURRENT_DIR)
APP_ROOT = os.path.dirname(BACKEND_DIR)

if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)
if APP_ROOT not in sys.path:
    sys.path.insert(0, APP_ROOT)

from app.database import SessionLocal
from app.models import (
    User, Reader, Book, BookCopy, TheLoai, Nxb,
    BorrowSlip, BorrowDetail, FineHistory,
    DatTruoc, LibraryConfig, AIConfig
)
from app.security import hash_password


def seed_all():
    print("=" * 65)
    print("  KHỞI TẠO DỮ LIỆU MẪU TOÀN DIỆN (ALL-IN-ONE SEED)")
    print("  Hệ thống Quản lý Thư viện Tích hợp AI")
    print("=" * 65)

    db = SessionLocal()
    try:
        # ── 1. Cấu hình hệ thống (LibraryConfig & AIConfig) ──────────────────────
        print("\n[1/6] Khởi tạo cấu hình hệ thống (LibraryConfig, AIConfig)...")
        if not db.get(LibraryConfig, 1):
            db.add(LibraryConfig(
                id=1,
                max_borrow_days=14,
                overdue_fine_points_per_day=2,
                max_books_at_once=5
            ))
            print("  ✓ Đã tạo LibraryConfig mặc định (mượn tối đa 14 ngày, phạt 2 điểm/ngày).")
        else:
            print("  • LibraryConfig đã tồn tại (bỏ qua).")

        if not db.get(AIConfig, 1):
            db.add(AIConfig(
                id=1,
                provider="openrouter",
                model="deepseek/deepseek-chat",
                api_key="your_openrouter_key_here",
                prompt_template="Bạn là trợ lý tra cứu của thư viện trường học..."
            ))
            print("  ✓ Đã tạo AIConfig mặc định (OpenRouter - deepseek/deepseek-chat).")
        else:
            print("  • AIConfig đã tồn tại (bỏ qua).")
        db.commit()

        # ── 2. Danh mục Thể loại & Nhà xuất bản ────────────────────────────────
        print("\n[2/6] Khởi tạo danh mục Thể loại và Nhà xuất bản...")
        the_loai_list = [
            ("TL01", "Kinh tế - Quản trị kinh doanh"),
            ("TL02", "Công nghệ thông tin"),
            ("TL03", "An toàn - Bảo mật thông tin"),
            ("TL04", "Kỹ năng sống - Phát triển bản thân"),
            ("TL05", "Văn học - Nghệ thuật"),
            ("TL06", "Khoa học - Kỹ thuật"),
            ("TL07", "Lịch sử - Xã hội"),
        ]
        for ma_tl, ten_tl in the_loai_list:
            if not db.get(TheLoai, ma_tl):
                db.add(TheLoai(ma=ma_tl, ten=ten_tl))

        nxb_list = [
            ("NXB01", "NXB Kinh Tế"),
            ("NXB02", "NXB Trẻ"),
            ("NXB03", "NXB Bách Khoa"),
            ("NXB04", "NXB Giáo Dục"),
            ("NXB05", "NXB Đại học Quốc gia"),
            ("NXB06", "NXB Tổng Hợp"),
        ]
        for ma_nxb, ten_nxb in nxb_list:
            if not db.get(Nxb, ma_nxb):
                db.add(Nxb(ma=ma_nxb, ten=ten_nxb))
        db.commit()
        print("  ✓ Danh mục Thể loại và NXB đã sẵn sàng.")

        # ── 3. Độc giả mẫu ───────────────────────────────────────────────────
        print("\n[3/6] Khởi tạo hồ sơ độc giả mẫu...")
        readers_data = [
            ("DG001", "Nguyễn Văn An", "DTC245200501@ictu.edu.vn", "0912345001", "sinh_vien"),
            ("DG002", "Trần Thị Bích", "DTC245200502@ictu.edu.vn", "0912345002", "sinh_vien"),
            ("DG003", "Lê Minh Cường", "DTC245200503@ictu.edu.vn", "0912345003", "giang_vien"),
        ]
        for ma, ten, email, sdt, loai in readers_data:
            existing_r = db.get(Reader, ma)
            if not existing_r:
                db.add(Reader(
                    ma=ma,
                    hoTen=ten,
                    email=email,
                    soDienThoai=sdt,
                    loaiDocGia=loai,
                    trangThaiThe="hoat_dong",
                    diem_svnet=100,
                    ngayTao=datetime.now()
                ))
                print(f"  ✓ Đã thêm độc giả [{ma}] {ten}")
        db.commit()

        # ── 4. Tài khoản người dùng (Users) ────────────────────────────────────
        print("\n[4/6] Khởi tạo 5 tài khoản đăng nhập mẫu...")
        users_data = [
            ("admin", "admin1", "Quản trị viên Hệ thống", "admin@ictu.edu.vn", "0900000001", "admin", None),
            ("librarian", "librarian1", "Thủ thư Thư viện", "librarian@ictu.edu.vn", "0900000002", "librarian", None),
            ("reader", "reader1", "Độc giả Vãng lai", "reader@ictu.edu.vn", "0900000003", "reader", None),
            ("docgia1", "docgia1", "Nguyễn Văn An", "DTC245200501@ictu.edu.vn", "0912345001", "reader", "DG001"),
            ("docgia2", "docgia2", "Trần Thị Bích", "DTC245200502@ictu.edu.vn", "0912345002", "reader", "DG002"),
        ]
        for uname, pwd, name, mail, sdt, role, r_id in users_data:
            existing_u = db.query(User).filter(User.username == uname).first()
            if not existing_u:
                db.add(User(
                    username=uname,
                    password_hash=hash_password(pwd),
                    ho_ten=name,
                    email=mail,
                    so_dien_thoai=sdt,
                    role=role,
                    reader_id=r_id,
                    is_active=True
                ))
                print(f"  ✓ Đã tạo tài khoản: {uname:10} (Mật khẩu: {pwd:10} | Quyền: {role})")
            else:
                # Đảm bảo mật khẩu đúng và đã kích hoạt
                existing_u.is_active = True
                existing_u.reader_id = r_id
                print(f"  • Tài khoản {uname} đã tồn tại (đã cập nhật trạng thái hoạt động).")
        db.commit()

        # ── 5. Kho sách từ books_catalog.json (63 cuốn) ────────────────────────
        print("\n[5/6] Nạp danh mục sách vào CSDL...")
        catalog_path = os.path.join(CURRENT_DIR, "books_catalog.json")
        so_sach_nap = 0
        first_books = []
        if os.path.exists(catalog_path):
            with open(catalog_path, encoding="utf-8") as f:
                books = json.load(f)
            
            the_loai_map = {tl.ten: tl.ma for tl in db.query(TheLoai).all()}
            nxb_map = {n.ten: n.ma for n in db.query(Nxb).all()}

            for b in books:
                ma_s = b["ma"]
                so_luong_val = int(b.get("soLuong", 5))
                if not db.get(Book, ma_s):
                    db.add(Book(
                        ma=ma_s,
                        ten=b["ten"],
                        tacGia=b.get("tacGia", "Chưa rõ"),
                        theLoai=b.get("theLoai", "Chung"),
                        nxb=b.get("nxb", "NXB Tổng hợp"),
                        namXb=b.get("namXb", 2024),
                        soLuong=so_luong_val,
                        anhBia=b.get("anhBia", ""),
                        tomTat=b.get("tomTat", ""),
                        theLoaiId=the_loai_map.get(b.get("theLoai")),
                        nxbId=nxb_map.get(b.get("nxb"))
                    ))
                    for i in range(1, so_luong_val + 1):
                        db.add(BookCopy(
                            copy_id=f"{ma_s}-C{i:02d}",
                            book_id=ma_s,
                            status="Có sẵn"
                        ))
                    so_sach_nap += 1
                else:
                    existing_book = db.get(Book, ma_s)
                    if existing_book:
                        existing_count = db.query(BookCopy).filter(BookCopy.book_id == ma_s).count()
                        if existing_count < existing_book.soLuong:
                            for i in range(existing_count + 1, existing_book.soLuong + 1):
                                db.add(BookCopy(
                                    copy_id=f"{ma_s}-C{i:02d}",
                                    book_id=ma_s,
                                    status="Có sẵn"
                                ))
                if len(first_books) < 5:
                    first_books.append(ma_s)
            db.commit()
            print(f"  ✓ Đã nạp thành công sách vào CSDL (Thêm mới: {so_sach_nap} / Tổng catalog: {len(books)} cuốn).")
        else:
            print("  ⚠️ Không tìm thấy file books_catalog.json!")

        # ── 6. Phiếu mượn mẫu, Phạt quá hạn & Đặt trước ───────────────────────
        now = datetime.now()
        b1 = first_books[0] if len(first_books) > 0 else "5CSKDVKD0002"
        b2 = first_books[1] if len(first_books) > 1 else "7TQHQ0003"
        b3 = first_books[2] if len(first_books) > 2 else "BCA0004"
        b4 = first_books[3] if len(first_books) > 3 else "BMTM0005"

        slips_data = [
            ("PM001", "DG001", b1, now - timedelta(days=5), now + timedelta(days=9), None, "dang_muon"),
            ("PM002", "DG002", b2, now - timedelta(days=20), now - timedelta(days=6), now - timedelta(days=6), "da_tra"),
            ("PM003", "DG001", b3, now - timedelta(days=20), now - timedelta(days=6), now - timedelta(days=4), "da_tra"), # Trễ 2 ngày
            ("PM004", "DG002", b4, now - timedelta(days=12), now + timedelta(days=2), None, "dang_muon"), # Còn 2 ngày (sắp hết hạn)
        ]
        for ma_p, dg, ms, nm, ht, nt, tt in slips_data:
            if not db.get(BorrowSlip, ma_p):
                copy = db.query(BookCopy).filter(BookCopy.book_id == ms, BookCopy.status == "Có sẵn").first()
                if not copy:
                    copy = db.query(BookCopy).filter(BookCopy.book_id == ms).first()
                if not copy:
                    copy = BookCopy(copy_id=f"{ms}-C01", book_id=ms, status="Có sẵn")
                    db.add(copy)
                    db.flush()

                if tt == "dang_muon":
                    copy.status = "Đang mượn"

                db.add(BorrowSlip(
                    ma_phieu=ma_p,
                    ma_doc_gia=dg,
                    ngay_muon=nm,
                    han_tra=ht,
                    ngay_tra=nt,
                    trang_thai=tt,
                    so_lan_gia_han=0
                ))
                db.add(BorrowDetail(
                    ma_phieu=ma_p,
                    ma_sach=ms,
                    copy_id=copy.copy_id,
                    so_luong=1,
                    ngay_tra_chi_tiet=nt
                ))
                # Giảm số lượng nếu đang mượn
                book_obj = db.get(Book, ms)
                if tt == "dang_muon" and book_obj and book_obj.soLuong > 0:
                    book_obj.soLuong -= 1

                # Sinh phạt cho PM003
                if ma_p == "PM003":
                    db.add(FineHistory(
                        ma_phieu=ma_p,
                        ma_doc_gia=dg,
                        so_ngay_qua_han=2,
                        so_diem=4,
                        ngay_tinh=nt,
                        da_thu=False
                    ))
                print(f"  ✓ Đã tạo phiếu mượn demo [{ma_p}] ({tt})")

        # Đặt trước mẫu
        if not db.get(DatTruoc, "RV001"):
            copy_res = db.query(BookCopy).filter(BookCopy.book_id == b2, BookCopy.status == "Có sẵn").first()
            if copy_res:
                copy_res.status = "Đang giữ chỗ"
            db.add(DatTruoc(
                ma_dat="RV001",
                ma_sach=b2,
                ma_doc_gia="DG001",
                ngay_dat=now - timedelta(days=3),
                ngay_xu_ly=now - timedelta(days=1),
                trang_thai="SAN_SANG",
                copy_id=copy_res.copy_id if copy_res else None,
                han_nhan=now + timedelta(days=2)
            ))
            print("  ✓ Đã tạo phiếu đặt trước demo [RV001] (SAN_SANG)")
        db.commit()

        # ── 7. Đồng bộ tự động sang ChromaDB Vector Store ──────────────────────
        print("\n[6/6] Đồng bộ tự động toàn bộ sách sang ChromaDB Vector Store...")
        try:
            from chatbotAI.index_sach import dong_bo_toan_bo
            from chatbotAI.vector_store import VectorStore
            all_books = db.query(Book).all()
            vs_data = [{
                "ma_sach": b.ma,
                "ten_sach": b.ten,
                "tac_gia": b.tacGia,
                "tom_tat": b.tomTat or "",
                "the_loai": b.theLoai or "",
                "con_hang": b.soLuong > 0
            } for b in all_books]
            
            dong_bo_toan_bo(vs_data)
            vs = VectorStore()
            print(f"  ✓ Vector Store đã sẵn sàng! Hiện có: {vs.dem_so_luong()} cuốn sách.")
        except Exception as e:
            print(f"  ⚠️ Cảnh báo đồng bộ Vector Store: {e}")
            print("     (Gợi ý: Cần đảm bảo đã cài pip install -r chatbotAI/requirements.txt)")

    finally:
        db.close()

    print("\n" + "=" * 65)
    print("  🎉 HOÀN TẤT SEED DỮ LIỆU THÀNH CÔNG!")
    print("  DANH SÁCH TÀI KHOẢN ĐĂNG NHẬP SẴN SÀNG:")
    print("  1. Quản trị viên (Admin):    admin      / admin1")
    print("  2. Thủ thư (Librarian):      librarian  / librarian1")
    print("  3. Độc giả (Reader demo 1):  docgia1    / docgia1  (Đã có lịch sử mượn & phạt)")
    print("  4. Độc giả (Reader demo 2):  docgia2    / docgia2")
    print("  5. Độc giả (Reader vãng lai): reader    / reader1")
    print("=" * 65)


if __name__ == "__main__":
    seed_all()
