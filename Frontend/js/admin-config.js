/* Trang Cấu hình admin — thư viện (UC24), AI (UC26), backup/restore (UC27). */
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
    }, 7000);
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

  // Biến lưu cấu hình hiện tại (để merge khi lưu từng form riêng)
  var _currentCfg = {
    maxBorrowDays: 14,
    overdueFinePointsPerDay: 2,
    overdueFineVndPerDayLecturer: 5000,
    maxBooksAtOnce: 5
  };

  function loadLibraryConfig() {
    clearMessage();
    setLoading(true);
    API.call("libraryConfig")
      .then(function (res) {
        setLoading(false);
        if (!res.ok) {
          showMessage(res.message);
          return;
        }
        var cfg = API.mapResponse("libraryConfig", res.data);
        if (!cfg) {
          showMessage("Chưa có cấu hình field cấu hình thư viện.");
          return;
        }
        // Lưu lại để dùng khi merge
        _currentCfg = {
          maxBorrowDays: cfg.maxBorrowDays,
          overdueFinePointsPerDay: cfg.overdueFinePointsPerDay,
          overdueFineVndPerDayLecturer: cfg.overdueFineVndPerDayLecturer,
          maxBooksAtOnce: cfg.maxBooksAtOnce
        };

        // Cấu hình mượn sách
        var libForm = document.getElementById("library-config-form");
        libForm.elements.maxBorrowDays.value = cfg.maxBorrowDays;
        libForm.elements.maxBooksAtOnce.value = cfg.maxBooksAtOnce;

        // Phạt sinh viên
        var svForm = document.getElementById("student-fine-form");
        svForm.elements.overdueFinePointsPerDay.value =
          cfg.overdueFinePointsPerDay !== "" ? cfg.overdueFinePointsPerDay : 2;

        // Phạt giảng viên
        var gvForm = document.getElementById("lecturer-fine-form");
        gvForm.elements.overdueFineVndPerDayLecturer.value =
          cfg.overdueFineVndPerDayLecturer !== "" ? cfg.overdueFineVndPerDayLecturer : 5000;
      })
      .catch(function () {
        setLoading(false);
        showMessage("Đã xảy ra lỗi khi tải cấu hình thư viện.");
      });
  }

  // Validate số nguyên không âm
  function validateNonNegInt(val, label) {
    if (val === "") return label + " chưa được nhập.";
    var n = Number(val);
    if (isNaN(n) || n < 0 || !Number.isInteger(n)) return label + " phải là số nguyên không âm.";
    return "";
  }

  function validateLibraryConfig(form) {
    var e = validateNonNegInt(form.elements.maxBorrowDays.value, "Số ngày mượn tối đa");
    if (e) return e;
    var nDays = Number(form.elements.maxBorrowDays.value);
    if (nDays < 1 || nDays > 365) return "Số ngày mượn tối đa phải từ 1 đến 365.";
    e = validateNonNegInt(form.elements.maxBooksAtOnce.value, "Giới hạn số sách");
    if (e) return e;
    var nBooks = Number(form.elements.maxBooksAtOnce.value);
    if (nBooks < 1 || nBooks > 100) return "Giới hạn số sách phải từ 1 đến 100.";
    return "";
  }

  // Gửi API với payload đầy đủ 4 trường (merge với _currentCfg)
  function callUpdateConfig(patch, onSuccess) {
    var payload = {
      max_borrow_days: patch.maxBorrowDays !== undefined ? patch.maxBorrowDays : _currentCfg.maxBorrowDays,
      overdue_fine_points_per_day: patch.overdueFinePointsPerDay !== undefined ? patch.overdueFinePointsPerDay : _currentCfg.overdueFinePointsPerDay,
      overdue_fine_vnd_per_day_lecturer: patch.overdueFineVndPerDayLecturer !== undefined ? patch.overdueFineVndPerDayLecturer : _currentCfg.overdueFineVndPerDayLecturer,
      max_books_at_once: patch.maxBooksAtOnce !== undefined ? patch.maxBooksAtOnce : _currentCfg.maxBooksAtOnce
    };
    API.call("updateLibraryConfig", payload, "PUT")
      .then(function (res) {
        if (!res.ok) { showMessage(res.message); return; }
        // Cập nhật cache
        if (patch.maxBorrowDays !== undefined) _currentCfg.maxBorrowDays = patch.maxBorrowDays;
        if (patch.overdueFinePointsPerDay !== undefined) _currentCfg.overdueFinePointsPerDay = patch.overdueFinePointsPerDay;
        if (patch.overdueFineVndPerDayLecturer !== undefined) _currentCfg.overdueFineVndPerDayLecturer = patch.overdueFineVndPerDayLecturer;
        if (patch.maxBooksAtOnce !== undefined) _currentCfg.maxBooksAtOnce = patch.maxBooksAtOnce;
        onSuccess();
      })
      .catch(function () {
        showMessage("Đã xảy ra lỗi kết nối khi lưu.");
      });
  }

  function saveLibraryConfig(e) {
    e.preventDefault();
    var form = document.getElementById("library-config-form");
    var error = validateLibraryConfig(form);
    if (error) { showMessage(error); return; }
    callUpdateConfig({
      maxBorrowDays: parseInt(form.elements.maxBorrowDays.value, 10),
      maxBooksAtOnce: parseInt(form.elements.maxBooksAtOnce.value, 10)
    }, function () {
      showMessage("Đã lưu cấu hình mượn sách.", "alert-success");
    });
  }

  function saveStudentFine(e) {
    e.preventDefault();
    var form = document.getElementById("student-fine-form");
    var val = form.elements.overdueFinePointsPerDay.value;
    var err = validateNonNegInt(val, "Điểm phạt sinh viên");
    if (err) { showMessage(err); return; }
    var n = parseInt(val, 10);
    callUpdateConfig({ overdueFinePointsPerDay: n }, function () {
      showMessage("Đã lưu: Phạt sinh viên — " + n + " điểm SVNET/ngày.", "alert-success");
    });
  }

  function saveLecturerFine(e) {
    e.preventDefault();
    var form = document.getElementById("lecturer-fine-form");
    var val = form.elements.overdueFineVndPerDayLecturer.value;
    var err = validateNonNegInt(val, "Tiền phạt giảng viên");
    if (err) { showMessage(err); return; }
    var n = parseInt(val, 10);
    callUpdateConfig({ overdueFineVndPerDayLecturer: n }, function () {
      showMessage("Đã lưu: Phạt giảng viên — " + Number(n).toLocaleString("vi-VN") + " VNĐ/ngày.", "alert-success");
    });
  }

  function loadAiConfig() {
    clearMessage();
    setLoading(true);
    API.call("aiConfig")
      .then(function (res) {
        setLoading(false);
        if (!res.ok) {
          showMessage(res.message);
          return;
        }
        var cfg = API.mapResponse("aiConfigOut", res.data);
        if (!cfg) {
          showMessage("Chưa có cấu hình field cấu hình AI.");
          return;
        }
        var form = document.getElementById("ai-config-form");
        form.elements.provider.value = cfg.provider;
        form.elements.model.value = cfg.model;
        form.elements.promptTemplate.value = cfg.promptTemplate;
        form.elements.apiKey.value = "";
        form.elements.clearKey.checked = false;
        form.elements.apiKey.placeholder = cfg.hasApiKey
          ? cfg.apiKeyMasked + " — nhập key mới để thay"
          : "Chưa có API key";
        document.getElementById("ai-key-status").textContent = cfg.hasApiKey
          ? "API key hiện tại: " + cfg.apiKeyMasked
          : "Chưa có API key.";
      })
      .catch(function () {
        setLoading(false);
        showMessage("Đã xảy ra lỗi khi tải cấu hình AI.");
      });
  }

  function saveAiConfig(e) {
    e.preventDefault();
    var form = document.getElementById("ai-config-form");
    var payload = {
      provider: form.elements.provider.value,
      model: form.elements.model.value,
      prompt_template: form.elements.promptTemplate.value
    };
    if (form.elements.apiKey.value) {
      payload.api_key = form.elements.apiKey.value;
    }
    if (form.elements.clearKey.checked) {
      payload.api_key = "";
    }
    API.call("updateAiConfig", payload, "PUT")
      .then(function (res) {
        if (!res.ok) {
          showMessage(res.message);
          return;
        }
        showMessage("Đã lưu cấu hình AI.", "alert-success");
        loadAiConfig();
      })
      .catch(function () {
        showMessage("Đã xảy ra lỗi khi lưu cấu hình AI.");
      });
  }

  function backupDatabase() {
    var button = document.getElementById("backup-button");
    button.disabled = true;
    button.textContent = "Đang sao lưu...";
    API.call("backup", undefined, "POST")
      .then(function (res) {
        button.disabled = false;
        button.textContent = "Sao lưu CSDL";
        if (!res.ok) {
          showMessage(res.message);
          return;
        }
        var mapped = API.mapResponse("backupOut", res.data);
        var text = mapped && mapped.message ? mapped.message : "Đã sao lưu CSDL.";
        if (mapped && mapped.path) {
          text += " — " + mapped.path;
        }
        showMessage(text, "alert-success");
      })
      .catch(function () {
        button.disabled = false;
        button.textContent = "Sao lưu CSDL";
        showMessage("Đã xảy ra lỗi khi sao lưu CSDL.");
      });
  }

  function restoreDatabase() {
    var path = document.getElementById("restore-path").value.trim();
    if (!path) {
      showMessage("Vui lòng nhập đường dẫn file .bak.");
      return;
    }
    var ok = window.confirm("Phục hồi sẽ THAY THẾ toàn bộ dữ liệu hiện tại. Tiếp tục?");
    if (!ok) {
      return;
    }
    var button = document.getElementById("restore-button");
    button.disabled = true;
    button.textContent = "Đang phục hồi...";
    API.call("restore", { file_path: path }, "POST")
      .then(function (res) {
        button.disabled = false;
        button.textContent = "Phục hồi CSDL";
        if (!res.ok) {
          showMessage(res.message);
          return;
        }
        var mapped = API.mapResponse("restoreOut", res.data);
        showMessage(mapped && mapped.message ? mapped.message : "Đã phục hồi CSDL.", "alert-success");
      })
      .catch(function () {
        button.disabled = false;
        button.textContent = "Phục hồi CSDL";
        showMessage("Đã xảy ra lỗi khi phục hồi CSDL.");
      });
  }

  document.addEventListener("DOMContentLoaded", function () {
    if (!Auth.requireAdmin()) {
      return;
    }
    Auth.applyRoleUI();
    document.getElementById("library-config-form").addEventListener("submit", saveLibraryConfig);
    document.getElementById("student-fine-form").addEventListener("submit", saveStudentFine);
    document.getElementById("lecturer-fine-form").addEventListener("submit", saveLecturerFine);
    document.getElementById("ai-config-form").addEventListener("submit", saveAiConfig);
    document.getElementById("backup-button").addEventListener("click", backupDatabase);
    document.getElementById("restore-button").addEventListener("click", restoreDatabase);
    loadLibraryConfig();
    loadAiConfig();
  });
})();
