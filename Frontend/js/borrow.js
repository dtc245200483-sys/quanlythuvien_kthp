/* Trang mượn / trả / gia hạn sách (chỉ librarian — admin không thao tác phiếu mượn). */
(function () {
  var API = window.API;
  var Auth = window.Auth;
  var messageTimer = null;
  var availableBooks = [];

  var finesList = [];

  function showMessage(text, type) {
    var el = document.getElementById("page-message");
    if (!el) {
      return;
    }
    if (messageTimer) {
      clearTimeout(messageTimer);
    }
    el.className = "alert " + (type || "alert-error");
    el.textContent = text;
    el.hidden = false;
    messageTimer = setTimeout(function () {
      el.hidden = true;
      messageTimer = null;
    }, 6000);
  }

  function clearMessage() {
    if (messageTimer) {
      clearTimeout(messageTimer);
      messageTimer = null;
    }
    var el = document.getElementById("page-message");
    if (el) {
      el.hidden = true;
    }
  }

  function setLoading(visible) {
    var el = document.getElementById("loading");
    if (el) {
      el.hidden = !visible;
    }
  }

  function loadReaders() {
    API.call("readers")
      .then(function (res) {
        if (!res.ok) {
          showMessage(res.message);
          return;
        }
        var select = document.getElementById("borrow-reader");
        select.innerHTML = '<option value="">— Chọn độc giả —</option>';
        (res.data || []).forEach(function (item) {
          var reader = API.mapResponse("readerOut", item);
          if (!reader) {
            return;
          }
          var option = document.createElement("option");
          option.value = reader.ma;
          option.textContent = reader.ma + " — " + reader.hoTen;
          select.appendChild(option);
        });
      })
      .catch(function () {
        showMessage("Đã xảy ra lỗi khi tải danh sách độc giả.");
      });
  }

  function loadLibraryConfig() {
    API.call("libraryConfig")
      .then(function (res) {
        if (!res.ok) {
          return;
        }
        var cfg = API.mapResponse("libraryConfig", res.data);
        if (!cfg) {
          return;
        }
        var input = document.getElementById("borrow-so-ngay");
        if (input) {
          input.value = cfg.maxBorrowDays || 14;
          input.max = cfg.maxBorrowDays || 365;
        }
      })
      .catch(function () {});
  }

  function refreshItemSelects() {
    document.querySelectorAll(".borrow-item-book").forEach(function (select) {
      var current = select.value;
      select.innerHTML = '<option value="">— Chọn sách —</option>';
      availableBooks.forEach(function (book) {
        var option = document.createElement("option");
        option.value = book.ma;
        option.textContent = book.ma + " — " + book.ten + " (còn " + book.soLuong + ")";
        select.appendChild(option);
      });
      select.value = current;
    });
  }

  function loadBooksCon() {
    var built = API.buildQuery("books", { trangThai: "con" });
    API.call("books", undefined, "GET", undefined, built.query)
      .then(function (res) {
        if (!res.ok) {
          showMessage(res.message);
          return;
        }
        availableBooks = (res.data || []).map(function (item) {
          return API.mapResponse("book", item) || item;
        });
        refreshItemSelects();
      })
      .catch(function () {
        showMessage("Đã xảy ra lỗi khi tải danh sách sách còn.");
      });
  }

  function addItemRow() {
    var container = document.getElementById("borrow-items");
    var row = document.createElement("div");
    row.className = "borrow-item-row";

    var bookGroup = document.createElement("div");
    bookGroup.className = "form-group borrow-item-book-group";
    var bookLabel = document.createElement("label");
    bookLabel.textContent = "Sách";
    var bookSelect = document.createElement("select");
    bookSelect.className = "borrow-item-book";
    bookSelect.innerHTML = '<option value="">— Chọn sách —</option>';
    availableBooks.forEach(function (book) {
      var option = document.createElement("option");
      option.value = book.ma;
      option.textContent = book.ma + " — " + book.ten + " (còn " + book.soLuong + ")";
      bookSelect.appendChild(option);
    });
    bookGroup.appendChild(bookLabel);
    bookGroup.appendChild(bookSelect);

    var qtyGroup = document.createElement("div");
    qtyGroup.className = "form-group borrow-item-qty-group";
    var qtyLabel = document.createElement("label");
    qtyLabel.textContent = "Số lượng";
    var qtyInput = document.createElement("input");
    qtyInput.type = "number";
    qtyInput.min = "1";
    qtyInput.value = "1";
    qtyGroup.appendChild(qtyLabel);
    qtyGroup.appendChild(qtyInput);

    var removeBtn = document.createElement("button");
    removeBtn.type = "button";
    removeBtn.className = "btn btn-danger";
    removeBtn.textContent = "Xoá dòng";
    removeBtn.addEventListener("click", function () {
      row.remove();
    });

    row.appendChild(bookGroup);
    row.appendChild(qtyGroup);
    row.appendChild(removeBtn);
    container.appendChild(row);
  }

  function createBorrow() {
    var maPhieu = document.getElementById("borrow-ma-phieu").value.trim();
    var maDocGia = document.getElementById("borrow-reader").value;
    if (!maPhieu) {
      showMessage("Vui lòng nhập mã phiếu mượn.");
      return;
    }
    if (!maDocGia) {
      showMessage("Vui lòng chọn độc giả.");
      return;
    }

    var items = [];
    var rows = document.querySelectorAll(".borrow-item-row");
    rows.forEach(function (row) {
      var maSach = row.querySelector(".borrow-item-book").value;
      var soLuong = parseInt(row.querySelector(".borrow-item-qty-group input").value, 10);
      if (maSach && soLuong >= 1) {
        items.push({ ma_sach: maSach, so_luong: soLuong });
      }
    });
    if (items.length === 0) {
      showMessage("Vui lòng chọn ít nhất 1 sách với số lượng hợp lệ.");
      return;
    }

    var payload = {
      ma_phieu: maPhieu,
      ma_doc_gia: maDocGia,
      so_ngay_muon: parseInt(document.getElementById("borrow-so-ngay").value, 10),
      items: items
    };
    if (!payload.so_ngay_muon || payload.so_ngay_muon < 1) {
      showMessage("Vui lòng nhập số ngày mượn hợp lệ (>= 1).");
      return;
    }

    API.call("createBorrow", payload, "POST")
      .then(function (res) {
        if (!res.ok) {
          showMessage(res.message);
          return;
        }
        showMessage("Đã lập phiếu mượn " + maPhieu + ".", "alert-success");
        document.getElementById("borrow-ma-phieu").value = "";
        document.querySelectorAll(".borrow-item-row:not(:first-child)").forEach(function (r) {
          r.remove();
        });
        var firstBook = document.querySelector(".borrow-item-book");
        var firstQty = document.querySelector(".borrow-item-qty-group input");
        if (firstBook) {
          firstBook.value = "";
        }
        if (firstQty) {
          firstQty.value = "1";
        }
        loadBooksCon();
        loadActiveBorrows();
      })
      .catch(function () {
        showMessage("Đã xảy ra lỗi không xác định khi lập phiếu mượn.");
      });
  }

  function loadActiveBorrows() {
    var built = API.buildQuery("borrows", { trangThai: "dang_muon" });
    API.call("borrows", undefined, "GET", undefined, built.query)
      .then(function (res) {
        if (!res.ok) {
          showMessage(res.message);
          return;
        }
        renderActive(res.data || []);
      })
      .catch(function () {
        showMessage("Đã xảy ra lỗi khi tải danh sách phiếu mượn.");
      });
  }

  function renderActive(list) {
    var tbody = document.getElementById("active-borrow-tbody");
    tbody.innerHTML = "";
    if (list.length === 0) {
      var emptyRow = document.createElement("tr");
      var emptyCell = document.createElement("td");
      emptyCell.className = "empty-row";
      emptyCell.colSpan = 7;
      emptyCell.textContent = "Không có phiếu mượn nào đang mượn.";
      emptyRow.appendChild(emptyCell);
      tbody.appendChild(emptyRow);
      return;
    }
    list.forEach(function (item) {
      var slip = API.mapResponse("borrowSlipOut", item);
      if (!slip) {
        return;
      }
      tbody.appendChild(slipRow(slip));
    });
  }

  function slipRow(slip) {
    var tr = document.createElement("tr");
    var detailsText = (slip.details || [])
      .map(function (d) {
        var detail = API.mapResponse("borrowDetailOut", d);
        if (!detail) return "";
        var text = (detail.tenSach || detail.maSach) + " x" + detail.soLuong;
        if (detail.copyId) {
          text += " (Mã bản: " + detail.copyId + ")";
        }
        return text;
      })
      .filter(Boolean)
      .join(", ");

    var values = [
      slip.maPhieu,
      slip.maDocGia,
      slip.ngayMuon ? new Date(slip.ngayMuon).toLocaleString("vi-VN") : "—",
      slip.hanTra ? new Date(slip.hanTra).toLocaleString("vi-VN") : "—",
      String(slip.soLanGiaHan || 0) + "/1",
      detailsText
    ];
    values.forEach(function (value) {
      var td = document.createElement("td");
      td.textContent = value || "—";
      tr.appendChild(td);
    });

    var actionsTd = document.createElement("td");
    var actions = document.createElement("div");
    actions.className = "row-actions";

    if (Number(slip.soLanGiaHan) < 1) {
      var renewBtn = document.createElement("button");
      renewBtn.type = "button";
      renewBtn.className = "btn btn-secondary";
      renewBtn.textContent = "Gia hạn";
      renewBtn.addEventListener("click", function () {
        renewSlip(slip);
      });
      actions.appendChild(renewBtn);
    }

    var returnBtn = document.createElement("button");
    returnBtn.type = "button";
    returnBtn.className = "btn btn-primary";
    returnBtn.textContent = "Trả sách";
    returnBtn.addEventListener("click", function () {
      returnSlip(slip);
    });
    actions.appendChild(returnBtn);

    actionsTd.appendChild(actions);
    tr.appendChild(actionsTd);
    return tr;
  }

  function returnSlip(slip) {
    API.call("returnBorrow", undefined, "PUT", { ma: slip.maPhieu })
      .then(function (res) {
        if (!res.ok) {
          showMessage(res.message);
          return;
        }
        var mapped = API.mapResponse("borrowReturnOut", res.data);
        var text = mapped && mapped.message ? mapped.message : "Đã trả sách.";
        var fine = mapped && mapped.fine ? API.mapResponse("fineOut", mapped.fine) : null;
        if (fine && Number(fine.soNgayQuaHan) > 0) {
          var fineText = Number(fine.soTien) > 0
            ? Number(fine.soTien).toLocaleString("vi-VN") + " VNĐ"
            : fine.soDiem + " điểm";
          text += " — Quá hạn " + fine.soNgayQuaHan + " ngày, phạt " + fineText + ".";
        }
        showMessage(text, "alert-success");
        loadActiveBorrows();
        loadBooksCon();
        loadFines();
      })
      .catch(function () {
        showMessage("Đã xảy ra lỗi không xác định khi trả sách.");
      });
  }

  function renewSlip(slip) {
    API.call("renewBorrow", undefined, "PUT", { ma: slip.maPhieu })
      .then(function (res) {
        if (!res.ok) {
          showMessage(res.message);
          return;
        }
        var mapped = API.mapResponse("borrowRenewOut", res.data);
        var text = mapped && mapped.message ? mapped.message : "Đã gia hạn phiếu mượn.";
        if (mapped && mapped.hanTraMoi) {
          text += " Hạn trả mới: " + new Date(mapped.hanTraMoi).toLocaleString("vi-VN");
        }
        var fine = mapped && mapped.fine ? API.mapResponse("fineOut", mapped.fine) : null;
        if (fine && Number(fine.soNgayQuaHan) > 0) {
          var fineText = Number(fine.soTien) > 0
            ? Number(fine.soTien).toLocaleString("vi-VN") + " VNĐ"
            : fine.soDiem + " điểm";
          text += " (phạt quá hạn " + fine.soNgayQuaHan + " ngày: " + fineText + ")";
        }
        showMessage(text, "alert-success");
        loadActiveBorrows();
        loadBooksCon();
        loadFines();
      })
      .catch(function () {
        showMessage("Đã xảy ra lỗi không xác định khi gia hạn phiếu mượn.");
      });
  }

  function loadFines() {
    var banner = document.getElementById("fine-banner");
    if (banner) {
      banner.hidden = true;
    }
    API.call("borrows", undefined, "GET", undefined, { trangThai: "da_tra" })
      .then(function (res) {
        if (!res.ok) {
          showMessage(res.message);
          return;
        }
        finesList = [];
        (res.data || []).forEach(function (slip) {
          (slip.fines || []).forEach(function (f) {
            if (!f.da_thu) {
              finesList.push({
                ma_phieu: slip.ma_phieu,
                ma_doc_gia: slip.ma_doc_gia,
                so_ngay_qua_han: f.so_ngay_qua_han,
                so_diem: f.so_diem || 0,
                so_tien: f.so_tien || 0
              });
            }
          });
        });
        renderFines();
      })
      .catch(function () {
        showMessage("Đã xảy ra lỗi khi tải danh sách phạt.");
      });
  }

  function renderFines() {
    var tbody = document.getElementById("fine-tbody");
    tbody.innerHTML = "";
    if (finesList.length === 0) {
      var emptyRow = document.createElement("tr");
      var emptyCell = document.createElement("td");
      emptyCell.className = "empty-row";
      emptyCell.colSpan = 5;
      emptyCell.textContent = "Không có khoản phạt chưa thu.";
      emptyRow.appendChild(emptyCell);
      tbody.appendChild(emptyRow);
      return;
    }
    finesList.forEach(function (f) {
      var tr = document.createElement("tr");
      var mucPhat = f.so_tien > 0
        ? Number(f.so_tien).toLocaleString("vi-VN") + " VNĐ"
        : f.so_diem + " điểm";
      var values = [f.ma_phieu, f.ma_doc_gia, f.so_ngay_qua_han, mucPhat];
      values.forEach(function (v) {
        var td = document.createElement("td");
        td.textContent = v;
        tr.appendChild(td);
      });
      var td = document.createElement("td");
      var btn = document.createElement("button");
      btn.type = "button";
      btn.className = "btn btn-primary";
      btn.textContent = "\u0110\u00e3 thu";
      btn.addEventListener("click", function () {
        collectFine(f);
      });
      td.appendChild(btn);
      tr.appendChild(td);
      tbody.appendChild(tr);
    });
  }

  function collectFine(f) {
    API.call("collectFine", undefined, "POST", { ma: f.ma_phieu })
      .then(function (res) {
        if (!res.ok) {
          showMessage(
            res.status === 404 || res.status === 405 || res.code === "API_CHUA_CO_TAI_LIEU"
              ? "Backend chưa hỗ trợ thu phạt (cần API POST /api/borrows/{ma}/collect-fine)."
              : res.message
          );
          return;
        }
        var mapped = API.mapResponse("collectFineOut", res.data);
        var text = "Đã thu phạt phiếu " + f.ma_phieu + ".";
        if (res.data && res.data.so_tien_da_thu > 0) {
          text += " Thu " + Number(res.data.so_tien_da_thu).toLocaleString("vi-VN") + " VNĐ.";
        } else if (mapped && mapped.soDiemDaThu > 0) {
          text +=
            " Trừ " + mapped.soDiemDaThu + " điểm, điểm còn lại " + mapped.diemConLai + ".";
        }
        showMessage(text, "alert-success");
        finesList = finesList.filter(function (x) {
          return x.ma_phieu !== f.ma_phieu;
        });
        renderFines();
      })
      .catch(function () {
        showMessage("Đã xảy ra lỗi khi thu phạt.");
      });
  }

  function init() {
    if (!Auth.requireLibrarian()) {
      return;
    }
    Auth.applyRoleUI();

    document.getElementById("add-borrow-item").addEventListener("click", addItemRow);
    document.getElementById("create-borrow-button").addEventListener("click", createBorrow);
    loadFines();

    loadReaders();
    loadLibraryConfig();
    loadBooksCon();
    loadActiveBorrows();
    addItemRow();
  }

  document.addEventListener("DOMContentLoaded", init);
})();
