/* Mượn / Trả sách — dành cho thủ thư (librarian) */
(function () {
  var API = window.API;
  var Auth = window.Auth;
  var messageTimer = null;

  // ── Helpers ──────────────────────────────────────────────────────────────

  function showMessage(text, type) {
    var el = document.getElementById("page-message");
    if (!el) return;
    if (messageTimer) clearTimeout(messageTimer);
    el.className = "alert " + (type || "alert-error");
    el.textContent = text;
    el.hidden = false;
    window.scrollTo({ top: 0, behavior: "smooth" });
    messageTimer = setTimeout(function () {
      el.hidden = true;
      messageTimer = null;
    }, 7000);
  }

  function setLoading(visible) {
    var el = document.getElementById("loading");
    if (el) el.hidden = !visible;
  }

  function fmtDate(iso) {
    if (!iso) return "—";
    return new Date(iso).toLocaleString("vi-VN");
  }

  function isOverdue(hanTra) {
    if (!hanTra) return false;
    return new Date(hanTra) < new Date();
  }

  // ── Thêm dòng sách vào form tạo phiếu ────────────────────────────────────

  var itemIndex = 0;

  function addBorrowItem() {
    itemIndex++;
    var container = document.getElementById("borrow-items");
    var row = document.createElement("div");
    row.className = "form-grid";
    row.dataset.idx = itemIndex;
    row.style.cssText = "align-items:center; margin-bottom:0.5rem; gap:0.5rem;";

    var maInput = document.createElement("input");
    maInput.type = "text";
    maInput.placeholder = "Mã sách (VD: CNKT0009)";
    maInput.maxLength = 20;
    maInput.className = "borrow-item-ma";
    maInput.id = "item-ma-" + itemIndex;

    var removeBtn = document.createElement("button");
    removeBtn.type = "button";
    removeBtn.className = "btn btn-danger";
    removeBtn.textContent = "✕";
    removeBtn.style.cssText = "padding:0.4rem 0.7rem; min-width:unset;";
    removeBtn.addEventListener("click", function () {
      container.removeChild(row);
    });

    row.appendChild(maInput);
    row.appendChild(removeBtn);
    container.appendChild(row);
    maInput.focus();
  }

  function getItems() {
    var inputs = document.querySelectorAll(".borrow-item-ma");
    var items = [];
    inputs.forEach(function (input) {
      var ma = (input.value || "").trim();
      if (ma) items.push({ ma_sach: ma, so_luong: 1 });
    });
    return items;
  }

  // ── Tạo phiếu mượn mới ──────────────────────────────────────────────────

  function submitBorrow() {
    var maPhieu = (document.getElementById("borrow-ma-phieu").value || "").trim();
    var maDocGia = (document.getElementById("borrow-ma-doc-gia").value || "").trim();
    var soNgayEl = document.getElementById("borrow-so-ngay");
    var soNgay = soNgayEl ? soNgayEl.value : "";
    var items = getItems();

    if (!maPhieu) { showMessage("Vui lòng nhập mã phiếu mượn."); return; }
    if (!maDocGia) { showMessage("Vui lòng nhập mã độc giả."); return; }
    if (items.length === 0) { showMessage("Vui lòng thêm ít nhất 1 cuốn sách."); return; }

    var body = { ma_phieu: maPhieu, ma_doc_gia: maDocGia, items: items };
    if (soNgay) body.so_ngay_muon = parseInt(soNgay, 10);

    setLoading(true);
    API.call("createBorrow", null, "POST", body)
      .then(function (res) {
        setLoading(false);
        if (!res.ok) { showMessage("Lỗi tạo phiếu: " + res.message); return; }
        showMessage("Đã tạo phiếu mượn " + maPhieu + " thành công.", "alert-success");
        document.getElementById("borrow-ma-phieu").value = "";
        document.getElementById("borrow-ma-doc-gia").value = "";
        document.getElementById("borrow-items").innerHTML = "";
        itemIndex = 0;
        addBorrowItem();
        loadBorrows();
      })
      .catch(function () {
        setLoading(false);
        showMessage("Đã xảy ra lỗi kết nối khi tạo phiếu mượn.");
      });
  }

  // ── Load & render danh sách phiếu ─────────────────────────────────────────

  function loadBorrows() {
    var docGia = (document.getElementById("filter-doc-gia").value || "").trim();
    var trangThai = document.getElementById("filter-trang-thai").value;
    var params = {};
    if (docGia) params.docGia = docGia;
    if (trangThai) params.trangThai = trangThai;

    setLoading(true);
    API.call("borrows", params, "GET")
      .then(function (res) {
        setLoading(false);
        if (!res.ok) { showMessage("Lỗi tải danh sách: " + res.message); return; }
        renderBorrows(res.data || []);
      })
      .catch(function () {
        setLoading(false);
        showMessage("Đã xảy ra lỗi kết nối.");
      });
  }

  function renderBorrows(list) {
    var tbody = document.getElementById("borrows-tbody");
    tbody.innerHTML = "";
    if (!list.length) {
      var tr = document.createElement("tr");
      var td = document.createElement("td");
      td.colSpan = 10; td.className = "empty-row";
      td.textContent = "Không có phiếu mượn nào.";
      tr.appendChild(td); tbody.appendChild(tr);
      return;
    }

    list.forEach(function (raw) {
      var slip = API.mapResponse("borrowSlipOut", raw) || raw;
      var fines = raw.fines || [];
      var tr = document.createElement("tr");
      var maPhieu = slip.maPhieu || raw.ma_phieu;
      var trangThai = slip.trangThai || raw.trang_thai;
      var soLanGiaHan = (slip.soLanGiaHan != null) ? slip.soLanGiaHan : (raw.so_lan_gia_han || 0);
      var hanTra = slip.hanTra || raw.han_tra;

      if (trangThai === "dang_muon" && isOverdue(hanTra)) {
        tr.style.background = "rgba(239,68,68,0.08)";
      }

      var sachText = (raw.details || []).map(function (d) {
        var det = API.mapResponse("borrowDetailOut", d) || d;
        return (det.tenSach || det.ten_sach || det.maSach || det.ma_sach || "?")
          + " [" + (det.copyId || det.copy_id || "—") + "]";
      }).join("; ") || "—";

      var phatText = fines.length ? fines.map(function (f) {
        var fi = API.mapResponse("fineOut", f) || f;
        var daThu = f.da_thu || f.daThu;
        var soTien = fi.soTien || f.so_tien || 0;
        var soDiem = fi.soDiem || f.so_diem || 0;
        var amt = soTien > 0
          ? Number(soTien).toLocaleString("vi-VN") + " VNĐ"
          : soDiem + " điểm";
        return amt + (daThu ? " ✓" : " (chưa thu)");
      }).join("; ") : "—";

      var statusLabel = trangThai === "dang_muon"
        ? (isOverdue(hanTra) ? "⚠ Quá hạn" : "Đang mượn")
        : "Đã trả";

      var cells = [
        maPhieu,
        slip.maDocGia || raw.ma_doc_gia,
        sachText,
        fmtDate(slip.ngayMuon || raw.ngay_muon),
        fmtDate(hanTra),
        fmtDate(slip.ngayTra || raw.ngay_tra),
        soLanGiaHan + "/1",
        statusLabel,
        phatText
      ];
      cells.forEach(function (val) {
        var td = document.createElement("td");
        td.textContent = val;
        if (val === "⚠ Quá hạn") td.style.color = "#dc2626";
        if (val === "Đã trả") td.style.color = "#16a34a";
        tr.appendChild(td);
      });

      // Cột thao tác
      var actionsTd = document.createElement("td");
      var actions = document.createElement("div");
      actions.className = "row-actions";

      if (trangThai === "dang_muon") {
        var retBtn = document.createElement("button");
        retBtn.type = "button"; retBtn.className = "btn btn-primary";
        retBtn.textContent = "Trả sách";
        retBtn.addEventListener("click", (function (ma) {
          return function () { doReturn(ma); };
        })(maPhieu));
        actions.appendChild(retBtn);

        if (soLanGiaHan < 1) {
          var renBtn = document.createElement("button");
          renBtn.type = "button"; renBtn.className = "btn btn-secondary";
          renBtn.textContent = "Gia hạn";
          renBtn.addEventListener("click", (function (ma) {
            return function () { openRenewModal(ma); };
          })(maPhieu));
          actions.appendChild(renBtn);
        }
      }

      var hasPending = fines.some(function (f) { return !(f.da_thu || f.daThu); });
      if (trangThai === "da_tra" && hasPending) {
        var fineBtn = document.createElement("button");
        fineBtn.type = "button"; fineBtn.className = "btn btn-danger";
        fineBtn.textContent = "Thu phạt";
        fineBtn.addEventListener("click", (function (ma, fs) {
          return function () { openFineModal(ma, fs); };
        })(maPhieu, fines));
        actions.appendChild(fineBtn);
      }

      if (!actions.children.length) actionsTd.textContent = "—";
      else actionsTd.appendChild(actions);
      tr.appendChild(actionsTd);
      tbody.appendChild(tr);
    });
  }

  // ── Trả sách ─────────────────────────────────────────────────────────────

  function doReturn(maPhieu) {
    if (!confirm('Xác nhận trả sách cho phiếu "' + maPhieu + '"?')) return;
    setLoading(true);
    API.call("returnBorrow", null, "PUT", null, { ma: maPhieu })
      .then(function (res) {
        setLoading(false);
        if (!res.ok) { showMessage("Lỗi trả sách: " + res.message); return; }
        var data = res.data || {};
        var extra = "";
        if (data.fine) {
          var soTien = data.fine.so_tien || 0;
          var soDiem = data.fine.so_diem || 0;
          if (soTien > 0) extra = " | Phạt: " + Number(soTien).toLocaleString("vi-VN") + " VNĐ";
          else if (soDiem > 0) extra = " | Phạt: " + soDiem + " điểm SVNET";
        }
        showMessage("Đã trả sách phiếu " + maPhieu + "." + extra, "alert-success");
        loadBorrows();
      })
      .catch(function () { setLoading(false); showMessage("Lỗi khi trả sách."); });
  }

  // ── Modal gia hạn ─────────────────────────────────────────────────────────

  var pendingRenewMa = null;
  function openRenewModal(maPhieu) {
    pendingRenewMa = maPhieu;
    document.getElementById("renew-modal-phieu").textContent = maPhieu;
    document.getElementById("renew-modal").hidden = false;
  }
  function closeRenewModal() {
    document.getElementById("renew-modal").hidden = true;
    pendingRenewMa = null;
  }
  function confirmRenew() {
    if (!pendingRenewMa) return;
    var ma = pendingRenewMa;
    closeRenewModal();
    setLoading(true);
    API.call("renewBorrow", null, "PUT", null, { ma: ma })
      .then(function (res) {
        setLoading(false);
        if (!res.ok) { showMessage("Lỗi gia hạn: " + res.message); return; }
        var d = res.data || {};
        var hanMoi = d.han_tra_moi ? " → Hạn mới: " + fmtDate(d.han_tra_moi) : "";
        showMessage("Đã gia hạn phiếu " + ma + hanMoi + ".", "alert-success");
        loadBorrows();
      })
      .catch(function () { setLoading(false); showMessage("Lỗi khi gia hạn."); });
  }

  // ── Modal thu phạt ────────────────────────────────────────────────────────

  var pendingFineMa = null;
  function openFineModal(maPhieu, fines) {
    pendingFineMa = maPhieu;
    document.getElementById("fine-modal-phieu").textContent = maPhieu;
    var totalNgay = fines.reduce(function (s, f) { return s + (f.so_ngay_qua_han || 0); }, 0);
    var totalTien = fines.reduce(function (s, f) { return s + (f.so_tien || 0); }, 0);
    var totalDiem = fines.reduce(function (s, f) { return s + (f.so_diem || 0); }, 0);
    var info = "Quá hạn " + totalNgay + " ngày. ";
    info += totalTien > 0
      ? "Tiền phạt: " + Number(totalTien).toLocaleString("vi-VN") + " VNĐ (giảng viên)."
      : "Điểm cần trừ: " + totalDiem + " điểm SVNET.";
    document.getElementById("fine-modal-info").textContent = info;
    document.getElementById("fine-modal").hidden = false;
  }
  function closeFineModal() {
    document.getElementById("fine-modal").hidden = true;
    pendingFineMa = null;
  }
  function confirmFine() {
    if (!pendingFineMa) return;
    var ma = pendingFineMa;
    closeFineModal();
    setLoading(true);
    API.call("collectFine", null, "POST", null, { ma: ma })
      .then(function (res) {
        setLoading(false);
        if (!res.ok) { showMessage("Lỗi thu phạt: " + res.message); return; }
        var d = res.data || {};
        var msg = d.message || "Đã thu phạt.";
        if (d.so_tien_da_thu > 0)
          msg += " | " + Number(d.so_tien_da_thu).toLocaleString("vi-VN") + " VNĐ.";
        else if (d.so_diem_da_thu > 0)
          msg += " | Trừ " + d.so_diem_da_thu + " điểm. Còn: " + d.diem_con_lai + " điểm.";
        showMessage(msg, "alert-success");
        loadBorrows();
      })
      .catch(function () { setLoading(false); showMessage("Lỗi khi thu phạt."); });
  }

  // ── Khởi động ────────────────────────────────────────────────────────────

  document.addEventListener("DOMContentLoaded", function () {
    if (!Auth.requireLibrarian()) return;
    Auth.applyRoleUI();

    document.getElementById("add-borrow-item").addEventListener("click", addBorrowItem);
    addBorrowItem(); // Thêm 1 dòng mặc định

    document.getElementById("submit-borrow").addEventListener("click", submitBorrow);

    document.getElementById("filter-btn").addEventListener("click", loadBorrows);
    document.getElementById("refresh-btn").addEventListener("click", function () {
      document.getElementById("filter-doc-gia").value = "";
      document.getElementById("filter-trang-thai").value = "";
      loadBorrows();
    });
    document.getElementById("filter-doc-gia").addEventListener("keydown", function (e) {
      if (e.key === "Enter") loadBorrows();
    });

    // Modals
    document.getElementById("renew-modal-cancel").addEventListener("click", closeRenewModal);
    document.getElementById("renew-modal-confirm").addEventListener("click", confirmRenew);
    document.getElementById("renew-modal").addEventListener("click", function (e) {
      if (e.target === this) closeRenewModal();
    });
    document.getElementById("fine-modal-cancel").addEventListener("click", closeFineModal);
    document.getElementById("fine-modal-confirm").addEventListener("click", confirmFine);
    document.getElementById("fine-modal").addEventListener("click", function (e) {
      if (e.target === this) closeFineModal();
    });

    // Load ban đầu — hiển thị phiếu đang mượn
    document.getElementById("filter-trang-thai").value = "dang_muon";
    loadBorrows();
  });
})();

