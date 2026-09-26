/* Dashboard thống kê (chức năng 7) — admin + librarian. */
(function () {
  var API = window.API;
  var Auth = window.Auth;
  var messageTimer = null;

  var MOCK = {
    topBooks: [
      { ma_sach: "S001", ten_sach: "Nh\u1eadp m\u00f4n tr\u00ed tu\u1ec7 nh\u00e2n t\u1ea1o", so_lan_muon: 12 },
      { ma_sach: "S002", ten_sach: "L\u1eadp tr\u00ecnh Python c\u01a1 b\u1ea3n", so_lan_muon: 9 },
      { ma_sach: "S003", ten_sach: "C\u1ea5u tr\u00fac d\u1eef li\u1ec7u v\u00e0 gi\u1ea3i thu\u1eadt", so_lan_muon: 7 },
      { ma_sach: "S004", ten_sach: "Ng\u01b0\u1eddi xa l\u1ea1", so_lan_muon: 4 },
      { ma_sach: "S005", ten_sach: "L\u1ecbch s\u1eed Vi\u1ec7t Nam hi\u1ec7n \u0111\u1ea1i", so_lan_muon: 3 }
    ],
    topReaders: [
      { ma_doc_gia: "DTCREADER", ho_ten: "\u0110\u1ed9c gi\u1ea3", so_phieu_muon: 8 },
      { ma_doc_gia: "DTC002", ho_ten: "Nguy\u1ec5n V\u0103n B", so_phieu_muon: 5 },
      { ma_doc_gia: "DTC003", ho_ten: "Tr\u1ea7n Th\u1ecb C", so_phieu_muon: 3 }
    ],
    overdue: [
      { ma_phieu: "PM001", ma_sach: "S001", ten_sach: "Nh\u1eadp m\u00f4n tr\u00ed tu\u1ec7 nh\u00e2n t\u1ea1o", ma_doc_gia: "DTCREADER", ho_ten: "\u0110\u1ed9c gi\u1ea3", so_ngay_qua_han: 3 },
      { ma_phieu: "PM002", ma_sach: "S004", ten_sach: "Ng\u01b0\u1eddi xa l\u1ea1", ma_doc_gia: "DTC002", ho_ten: "Nguy\u1ec5n V\u0103n B", so_ngay_qua_han: 1 }
    ]
  };

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

  function setLoading(visible) {
    var el = document.getElementById("loading");
    if (el) {
      el.hidden = !visible;
    }
  }

  function missing(res) {
    return res && (res.code === "API_CHUA_CO_TAI_LIEU" || res.status === 404 || res.status === 405);
  }

  function normalize(item, section) {
    if (item && item[API.config.fieldMap[section][Object.keys(API.config.fieldMap[section])[0]]] !== undefined) {
      return API.mapResponse(section, item) || item;
    }
    return item;
  }

  function loadStats() {
    setLoading(true);
    Promise.all([
      API.call("statsTopBooks"),
      API.call("statsTopReaders"),
      API.call("statsOverdueBooks")
    ])
      .then(function (rs) {
        setLoading(false);
        var mockUsed = false;
        var tb = rs[0];
        var tr = rs[1];
        var ov = rs[2];
        if (!tb.ok) {
          if (missing(tb)) {
            tb = { ok: true, data: MOCK.topBooks };
            mockUsed = true;
          } else {
            showMessage(tb.message);
            return;
          }
        }
        if (!tr.ok) {
          if (missing(tr)) {
            tr = { ok: true, data: MOCK.topReaders };
            mockUsed = true;
          } else {
            showMessage(tr.message);
            return;
          }
        }
        if (!ov.ok) {
          if (missing(ov)) {
            ov = { ok: true, data: MOCK.overdue };
            mockUsed = true;
          } else {
            showMessage(ov.message);
            return;
          }
        }
        document.getElementById("mock-banner").hidden = !mockUsed;
        renderTopBooks((tb.data || []).map(function (i) { return normalize(i, "statsBookOut"); }));
        renderTopReaders((tr.data || []).map(function (i) { return normalize(i, "statsReaderOut"); }));
        renderOverdue((ov.data || []).map(function (i) { return normalize(i, "statsOverdueOut"); }));
      })
      .catch(function () {
        setLoading(false);
        showMessage("Đã xảy ra lỗi khi tải thống kê.");
      });
  }

  function barCell(value, max) {
    var td = document.createElement("td");
    var track = document.createElement("div");
    track.className = "bar-track";
    var fill = document.createElement("div");
    fill.className = "bar-fill";
    fill.style.width = max > 0 ? Math.round((value / max) * 100) + "%" : "0%";
    track.appendChild(fill);
    td.appendChild(track);
    return td;
  }

  function renderTopBooks(list) {
    var tbody = document.getElementById("top-books-tbody");
    tbody.innerHTML = "";
    if (list.length === 0) {
      emptyRow(tbody, 4);
      return;
    }
    var max = Math.max.apply(null, list.map(function (b) { return Number(b.soLanMuon) || 0; }));
    list.forEach(function (b) {
      var tr = document.createElement("tr");
      var td1 = document.createElement("td");
      td1.textContent = b.maSach;
      var td2 = document.createElement("td");
      td2.textContent = b.tenSach || "—";
      var td3 = document.createElement("td");
      td3.textContent = b.soLanMuon;
      tr.appendChild(td1);
      tr.appendChild(td2);
      tr.appendChild(td3);
      tr.appendChild(barCell(Number(b.soLanMuon) || 0, max));
      tbody.appendChild(tr);
    });
  }

  function renderTopReaders(list) {
    var tbody = document.getElementById("top-readers-tbody");
    tbody.innerHTML = "";
    if (list.length === 0) {
      emptyRow(tbody, 4);
      return;
    }
    var max = Math.max.apply(null, list.map(function (r) { return Number(r.soPhieuMuon) || 0; }));
    list.forEach(function (r) {
      var tr = document.createElement("tr");
      var td1 = document.createElement("td");
      td1.textContent = r.maDocGia;
      var td2 = document.createElement("td");
      td2.textContent = r.hoTen || "—";
      var td3 = document.createElement("td");
      td3.textContent = r.soPhieuMuon;
      tr.appendChild(td1);
      tr.appendChild(td2);
      tr.appendChild(td3);
      tr.appendChild(barCell(Number(r.soPhieuMuon) || 0, max));
      tbody.appendChild(tr);
    });
  }

  function renderOverdue(list) {
    var tbody = document.getElementById("overdue-tbody");
    tbody.innerHTML = "";
    if (list.length === 0) {
      emptyRow(tbody, 5);
      return;
    }
    list.forEach(function (o) {
      var tr = document.createElement("tr");
      var values = [
        o.maPhieu,
        o.maSach,
        o.tenSach || "—",
        (o.hoTen ? o.hoTen + " (" + o.maDocGia + ")" : o.maDocGia),
        o.soNgayQuaHan
      ];
      values.forEach(function (v) {
        var td = document.createElement("td");
        td.textContent = v;
        tr.appendChild(td);
      });
      tbody.appendChild(tr);
    });
  }

  function emptyRow(tbody, colSpan) {
    var tr = document.createElement("tr");
    var td = document.createElement("td");
    td.className = "empty-row";
    td.colSpan = colSpan;
    td.textContent = "Chưa có dữ liệu.";
    tr.appendChild(td);
    tbody.appendChild(tr);
  }

  document.addEventListener("DOMContentLoaded", function () {
    if (!Auth.requireStaff()) {
      return;
    }
    Auth.applyRoleUI();
    loadStats();

    var btnRefresh = document.getElementById("btn-refresh");
    if (btnRefresh) {
      btnRefresh.addEventListener("click", function () {
        loadStats();
      });
    }
  });
})();
