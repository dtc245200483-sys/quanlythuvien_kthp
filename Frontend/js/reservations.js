/* Trang đặt trước sách — reader xem/huỷ; librarian xử lý (chức năng 6). */
(function () {
  var API = window.API;
  var Auth = window.Auth;
  var messageTimer = null;

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

  function TRANG_THAI_LABEL(t) {
    return {
      CHO_XU_LY: "Chờ xử lý",
      SAN_SANG: "Sẵn sàng",
      DA_MUON: "Đã mượn",
      HUY: "Đã huỷ"
    }[t] || t;
  }

  function normalize(item) {
    if (item.ma_dat !== undefined) {
      return API.mapResponse("reservationOut", item) || item;
    }
    return item;
  }

  function load() {
    setLoading(true);
    API.call("reservations")
      .then(function (res) {
        setLoading(false);
        if (!res.ok) {
          showMessage(res.message);
          return;
        }
        var items = (res.data || []).map(normalize);
        var user = Auth.currentUser();
        if (user && user.role === "reader") {
          renderReader(items);
        } else {
          renderLibrarian(items);
        }
      })
      .catch(function () {
        setLoading(false);
        showMessage("Đã xảy ra lỗi khi tải danh sách đặt trước.");
      });
  }

  function renderReader(list) {
    var tbody = document.getElementById("reader-reservation-tbody");
    tbody.innerHTML = "";
    var hasProcessed = list.some(function (r) {
      return r.trangThai === "HUY" || r.trangThai === "DA_MUON";
    });
    var deleteAllBtn = document.getElementById("delete-processed-reservations-button");
    if (deleteAllBtn) {
      deleteAllBtn.hidden = !hasProcessed;
    }
    if (list.length === 0) {
      var emptyRow = document.createElement("tr");
      var emptyCell = document.createElement("td");
      emptyCell.className = "empty-row";
      emptyCell.colSpan = 7;
      emptyCell.textContent = "Chưa có đặt trước nào.";
      emptyRow.appendChild(emptyCell);
      tbody.appendChild(emptyRow);
      return;
    }
    list.forEach(function (r) {
      var tr = document.createElement("tr");
      var values = [
        r.maDat,
        r.tenSach || r.maSach,
        r.ngayDat ? new Date(r.ngayDat).toLocaleString("vi-VN") : "—",
        r.hanNhan ? new Date(r.hanNhan).toLocaleString("vi-VN") : "—",
        TRANG_THAI_LABEL(r.trangThai),
        r.queue_position !== null && r.queue_position !== undefined ? r.queue_position : "—",
        null
      ];
      values.forEach(function (v, index) {
        var td = document.createElement("td");
        if (index === 6) {
          if (r.trangThai === "CHO_XU_LY") {
            var actions = document.createElement("div");
            actions.className = "row-actions";
            var cancelBtn = document.createElement("button");
            cancelBtn.type = "button";
            cancelBtn.className = "btn btn-danger";
            cancelBtn.textContent = "Huỷ";
            cancelBtn.addEventListener("click", function () {
              cancel(r);
            });
            actions.appendChild(cancelBtn);
            td.appendChild(actions);
          } else if (r.trangThai === "HUY" || r.trangThai === "DA_MUON") {
            var actions = document.createElement("div");
            actions.className = "row-actions";
            var deleteBtn = document.createElement("button");
            deleteBtn.type = "button";
            deleteBtn.className = "btn btn-danger";
            deleteBtn.textContent = "Xoá";
            deleteBtn.addEventListener("click", function () {
              deleteOne(r);
            });
            actions.appendChild(deleteBtn);
            td.appendChild(actions);
          } else {
            td.textContent = "—";
          }
        } else {
          td.textContent = v;
        }
        tr.appendChild(td);
      });
      tbody.appendChild(tr);
    });
  }

  function renderLibrarian(list) {
    var tbody = document.getElementById("librarian-reservation-tbody");
    tbody.innerHTML = "";
    var user = Auth.currentUser() || {};
    var isAdmin = user.role === "admin";
    var hasProcessed = list.some(function (r) {
      return r.trangThai === "HUY" || r.trangThai === "DA_MUON";
    });
    var deleteAllBtn = document.getElementById("delete-processed-librarian-button");
    if (deleteAllBtn) {
      deleteAllBtn.hidden = isAdmin || !hasProcessed;
    }
    if (list.length === 0) {
      var emptyRow = document.createElement("tr");
      var emptyCell = document.createElement("td");
      emptyCell.className = "empty-row";
      emptyCell.colSpan = 9;
      emptyCell.textContent = "Chưa có đặt trước nào.";
      emptyRow.appendChild(emptyCell);
      tbody.appendChild(emptyRow);
      return;
    }
    list.forEach(function (r) {
      var tr = document.createElement("tr");
      var values = [
        r.maDat,
        r.maSach,
        r.tenSach || "—",
        r.maDocGia || "—",
        r.ngayDat ? new Date(r.ngayDat).toLocaleString("vi-VN") : "—",
        r.hanNhan ? new Date(r.hanNhan).toLocaleString("vi-VN") : "—",
        TRANG_THAI_LABEL(r.trangThai),
        r.queue_position !== null && r.queue_position !== undefined ? r.queue_position : "—",
        null
      ];
      values.forEach(function (v, index) {
        var td = document.createElement("td");
        if (index === 8) {
          if (isAdmin) {
            td.textContent = "—";
          } else {
            var actions = document.createElement("div");
            actions.className = "row-actions";
            if (r.trangThai === "HUY" || r.trangThai === "DA_MUON") {
              var deleteBtn = document.createElement("button");
              deleteBtn.type = "button";
              deleteBtn.className = "btn btn-danger";
              deleteBtn.textContent = "Xoá";
              deleteBtn.addEventListener("click", function () {
                deleteOne(r);
              });
              actions.appendChild(deleteBtn);
            } else if (r.trangThai === "CHO_XU_LY") {
              if (r.queue_position === 1) {
                var ready = document.createElement("button");
                ready.type = "button";
                ready.className = "btn btn-primary";
                ready.textContent = "Sẵn sàng";
                ready.title = "Duyệt sẵn sàng nhận sách cho người đứng đầu hàng đợi";
                ready.addEventListener("click", function () {
                  fulfill(r);
                });
                actions.appendChild(ready);
              } else {
                var waitBtn = document.createElement("button");
                waitBtn.type = "button";
                waitBtn.className = "btn btn-secondary";
                waitBtn.disabled = true;
                waitBtn.title = "Đang chờ đến lượt phục vụ theo thứ tự hàng đợi";
                waitBtn.textContent = "Chờ lượt";
                actions.appendChild(waitBtn);
              }
            }
            if (r.trangThai === "SAN_SANG") {
              var confirmBtn = document.createElement("button");
              confirmBtn.type = "button";
              confirmBtn.className = "btn btn-primary";
              confirmBtn.textContent = "Xác nhận đã lấy";
              confirmBtn.addEventListener("click", function () {
                confirmBorrow(r);
              });
              actions.appendChild(confirmBtn);
            }
            if (r.trangThai === "CHO_XU_LY" || r.trangThai === "SAN_SANG") {
              var cancelBtn = document.createElement("button");
              cancelBtn.type = "button";
              cancelBtn.className = "btn btn-danger";
              cancelBtn.textContent = "Huỷ";
              cancelBtn.addEventListener("click", function () {
                cancel(r);
              });
              actions.appendChild(cancelBtn);
            }
            td.appendChild(actions);
          }
        } else {
          td.textContent = v;
        }
        tr.appendChild(td);
      });
      tbody.appendChild(tr);
    });
  }

  function confirmBorrow(r) {
    var ok = window.confirm(
      'Xác nhận độc giả đã lấy sách "' + (r.tenSach || r.maSach) + '"? Hệ thống sẽ lập phiếu mượn.'
    );
    if (!ok) {
      return;
    }
    API.call("confirmReservation", undefined, "PUT", { ma_dat: r.maDat })
      .then(function (res) {
        if (!res.ok) {
          showMessage(res.message || "Lỗi khi xác nhận đặt trước.", "alert-error");
          return;
        }
        showMessage("Đã xác nhận lấy sách — đặt trước hoàn thành.", "alert-success");
        load();
      })
      .catch(function () {
        showMessage("Đã xảy ra lỗi khi xác nhận đặt trước.", "alert-error");
      });
  }

  function cancel(r) {
    var ok = window.confirm('Huỷ đặt trước "' + (r.tenSach || r.maSach) + '"?');
    if (!ok) {
      return;
    }
    API.call("cancelReservation", undefined, "PUT", { ma_dat: r.maDat }).then(function (res) {
      if (!res.ok) {
        showMessage(res.message);
        return;
      }
      showMessage("Đã huỷ đặt trước.", "alert-success");
      load();
    });
  }

  function deleteOne(r) {
    var ok = window.confirm(
      'Xoá đặt trước "' + (r.tenSach || r.maSach) + '" khỏi lịch sử?'
    );
    if (!ok) {
      return;
    }
    API.call("deleteMyReservation", undefined, "DELETE", { ma_dat: r.maDat }).then(function (res) {
      if (!res.ok) {
        showMessage(res.message);
        return;
      }
      showMessage("Đã xoá đặt trước khỏi lịch sử.", "alert-success");
      load();
    });
  }

  function deleteAllHistory() {
    var ok = window.confirm("Xoá toàn bộ lịch sử đặt trước đã xử lý (Đã huỷ/Đã mượn)?");
    if (!ok) {
      return;
    }
    API.call("deleteMyReservations", undefined, "DELETE").then(function (res) {
      if (!res.ok) {
        showMessage(res.message);
        return;
      }
      showMessage("Đã xoá lịch sử đặt trước đã xử lý.", "alert-success");
      load();
    });
  }

  function fulfill(r) {
    API.call("fulfillReservation", undefined, "PUT", { ma_dat: r.maDat }).then(function (res) {
      if (!res.ok) {
        showMessage(res.message);
        return;
      }
      showMessage("Đã đánh dấu sách sẵn sàng.", "alert-success");
      load();
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    var user = Auth.currentUser();
    if (!user) {
      window.location.replace("index.html");
      return;
    }
    if (user.role === "admin") {
      sessionStorage.setItem("thuvien_access_msg", "Bạn không có quyền truy cập trang này.");
      window.location.replace("search.html");
      return;
    }
    Auth.applyRoleUI();
    var deleteAllBtn = document.getElementById("delete-processed-reservations-button");
    if (deleteAllBtn) {
      deleteAllBtn.addEventListener("click", deleteAllHistory);
    }
    var deleteAllLibBtn = document.getElementById("delete-processed-librarian-button");
    if (deleteAllLibBtn) {
      deleteAllLibBtn.addEventListener("click", deleteAllHistory);
    }
    load();
  });
})();
