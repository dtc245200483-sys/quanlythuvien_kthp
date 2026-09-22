/*
 * Cấu hình kết nối API — theo Backend/api_docs.md 0.25.0:
 * chức năng 1–5 + đăng ký, yêu cầu mượn/trả/gia hạn, lịch sử độc giả,
 * quản lý tài khoản, danh mục thể loại/NXB. API key AI do Backend giữ.
 */
window.API = (function () {
  var config = {
    /*
     * Tự động lấy host đang mở web (máy tính: localhost; điện thoại cùng
     * mạng Wi-Fi: IP máy tính) để gọi Backend cho đúng — không cần sửa tay.
     */
    baseUrl: (function () {
      var host = window.location && window.location.hostname;
      if (!host || host === "localhost") {
        host = "localhost";
      }
      return "http://" + host + ":8000";
    })(),
    endpoints: {
      login: "/api/auth/login",
      books: "/api/books",
      createBook: "/api/books",
      updateBook: "/api/books/{ma}",
      deleteBook: "/api/books/{ma}",
      uploadBookCover: "/api/books/upload-cover",
      readers: "/api/readers",
      createReader: "/api/readers",
      updateReader: "/api/readers/{ma}",
      deleteReader: "/api/readers/{ma}",
      lockReader: "/api/readers/{ma}/lock",
      createBorrow: "/api/borrows",
      borrows: "/api/borrows",
      returnBorrow: "/api/borrows/{ma}/return",
      renewBorrow: "/api/borrows/{ma}/renew",
      register: "/api/auth/register",
      myBorrows: "/api/borrows/me",
      deleteMyBorrow: "/api/borrows/me/{ma_phieu}",
      deleteMyBorrows: "/api/borrows/me",
      reservations: "/api/reservations",
      createReservation: "/api/reservations",
      cancelReservation: "/api/reservations/{ma_dat}/cancel",
      fulfillReservation: "/api/reservations/{ma_dat}/fulfill",
      deleteMyReservation: "/api/reservations/me/{ma_dat}",
      deleteMyReservations: "/api/reservations/me",
      confirmReservation: "/api/reservations/{ma_dat}/borrow",
      notifications: "/api/notifications",
      markNotificationRead: "/api/notifications/{source_id}/read",
      markAllNotificationsRead: "/api/notifications/read-all",
      deleteNotification: "/api/notifications/{source_id}",
            exportBooks: "/api/export/books.csv",
      exportBorrows: "/api/export/borrows.csv",
      exportReport: "/api/export/report.csv",
      exportReservations: "/api/export/reservations.csv",
      aiConfig: "/api/admin/config/ai",
      updateAiConfig: "/api/admin/config/ai",
      backup: "/api/admin/backup",
      restore: "/api/admin/restore",
      collectFine: "/api/borrows/{ma}/collect-fine",
      deleteMyRequest: "/api/requests/me/{id}",
      deleteMyRequests: "/api/requests/me",
      requests: "/api/requests",
      createRequest: "/api/requests",
      approveRequest: "/api/requests/{id}/approve",
      rejectRequest: "/api/requests/{id}/reject",
      accounts: "/api/admin/accounts",
      createAccount: "/api/admin/accounts",
      updateAccount: "/api/admin/accounts/{id}",
      deleteAccount: "/api/admin/accounts/{id}",
      categories: "/api/admin/categories",
      createCategory: "/api/admin/categories",
      updateCategory: "/api/admin/categories/{id}",
      deleteCategory: "/api/admin/categories/{id}",
      publishers: "/api/admin/publishers",
      createPublisher: "/api/admin/publishers",
      updatePublisher: "/api/admin/publishers/{id}",
      deletePublisher: "/api/admin/publishers/{id}",
      libraryConfig: "/api/admin/config/library",
      updateLibraryConfig: "/api/admin/config/library",
      profileMe: "/api/profile/me",
      updateProfileMe: "/api/profile/me",
      changeProfilePassword: "/api/profile/me/password",
      uploadProfileAvatar: "/api/profile/me/avatar",
      chatbot: "/api/chatbot/hoi",
      chatbotHealth: "/api/chatbot/health",
      statsTopBooks: "/api/stats/top-books",
      statsTopReaders: "/api/stats/top-readers",
      statsOverdueBooks: "/api/stats/overdue-books"
    },
    fieldMap: {
      login: {
        username: "username",
        password: "password"
      },
      loginResponse: {
        token: "token",
        role: "role",
        name: "name"
      },
      book: {
        ma: "ma",
        ten: "ten",
        tacGia: "tacGia",
        theLoai: "theLoai",
        nxb: "nxb",
        namXb: "namXb",
        soLuong: "soLuong",
        anhBia: "anhBia",
        tomTat: "tomTat",
        trangThai: "trangThai"
      },
      readerCreate: {
        ma: "ma",
        hoTen: "hoTen",
        email: "email",
        soDienThoai: "soDienThoai",
        loaiDocGia: "loaiDocGia",
        trangThaiThe: "trangThaiThe"
      },
      readerOut: {
        ma: "ma",
        hoTen: "hoTen",
        email: "email",
        soDienThoai: "soDienThoai",
        loaiDocGia: "loaiDocGia",
        trangThaiThe: "trangThaiThe",
        ngayTao: "ngayTao"
      },
      lockReader: {
        trangThaiThe: "trangThaiThe"
      },
      borrowSlipOut: {
        maPhieu: "ma_phieu",
        maDocGia: "ma_doc_gia",
        ngayMuon: "ngay_muon",
        hanTra: "han_tra",
        ngayTra: "ngay_tra",
        trangThai: "trang_thai",
        soLanGiaHan: "so_lan_gia_han",
        details: "details"
      },
      borrowDetailOut: {
        maSach: "ma_sach",
        tenSach: "ten_sach",
        soLuong: "so_luong",
        ngayTraChiTiet: "ngay_tra_chi_tiet",
        copyId: "copy_id"
      },
      borrowReturnOut: {
        message: "message",
        ngayTra: "ngay_tra",
        fine: "fine"
      },
      borrowRenewOut: {
        message: "message",
        hanTraMoi: "han_tra_moi",
        soLanGiaHan: "so_lan_gia_han",
        fine: "fine"
      },
      fineOut: {
        soNgayQuaHan: "so_ngay_qua_han",
        soDiem: "so_diem"
      },
      collectFineOut: {
        message: "message",
        soDiemDaThu: "so_diem_da_thu",
        diemConLai: "diem_con_lai",
        ngayThu: "ngay_thu"
      },
      register: {
        username: "username",
        password: "password",
        hoTen: "hoTen",
        email: "email",
        soDienThoai: "soDienThoai",
        loaiDocGia: "loaiDocGia"
      },
      registerResponse: {
        token: "token",
        role: "role",
        name: "name",
        readerMa: "reader_ma"
      },
      borrowHistoryOut: {
        maPhieu: "ma_phieu",
        maDocGia: "ma_doc_gia",
        ngayMuon: "ngay_muon",
        hanTra: "han_tra",
        ngayTra: "ngay_tra",
        trangThai: "trang_thai",
        soLanGiaHan: "so_lan_gia_han",
        details: "details",
        fines: "fines"
      },
      requestOut: {
        maYeuCau: "ma_yeu_cau",
        loai: "loai",
        maDocGia: "ma_doc_gia",
        maPhieu: "ma_phieu",
        items: "items",
        soNgayMuon: "so_ngay_muon",
        trangThai: "trang_thai",
        ngayTao: "ngay_tao",
        canhBao: "canh_bao",
        ghiChu: "ghi_chu"
      },
      accountCreate: {
        username: "username",
        password: "password",
        hoTen: "ho_ten",
        email: "email",
        soDienThoai: "so_dien_thoai",
        role: "role",
        readerId: "reader_id"
      },
      accountOut: {
        id: "id",
        username: "username",
        hoTen: "ho_ten",
        email: "email",
        soDienThoai: "so_dien_thoai",
        role: "role",
        isActive: "is_active",
        readerId: "reader_id",
        createdAt: "created_at"
      },
      profileOut: {
        username: "username",
        hoTen: "ho_ten",
        email: "email",
        soDienThoai: "so_dien_thoai",
        loaiDocGia: "loai_doc_gia",
        role: "role",
        avatarUrl: "avatar_url"
      },
      profileUpdate: {
        hoTen: "ho_ten",
        email: "email",
        soDienThoai: "so_dien_thoai",
        loaiDocGia: "loai_doc_gia"
      },
      profilePassword: {
        matKhauCu: "mat_khau_cu",
        matKhauMoi: "mat_khau_moi"
      },
      catalogItem: {
        ma: "ma",
        ten: "ten"
      },
      libraryConfig: {
        maxBorrowDays: "max_borrow_days",
        overdueFinePointsPerDay: "overdue_fine_points_per_day",
        overdueFineVndPerDayLecturer: "overdue_fine_vnd_per_day_lecturer",
        maxBooksAtOnce: "max_books_at_once"
      },
      collectFineOut: {
        message: "message",
        soDiemDaThu: "so_diem_da_thu",
        soTienDaThu: "so_tien_da_thu",
        diemConLai: "diem_con_lai",
        ngayThu: "ngay_thu"
      },
      fineOut: {
        soNgayQuaHan: "so_ngay_qua_han",
        soDiem: "so_diem",
        soTien: "so_tien",
        daThu: "da_thu",
        ngayThu: "ngay_thu"
      },
      reservationCreate: {
        maSach: "ma_sach",
        maDocGia: "ma_doc_gia"
      },
      reservationOut: {
        maDat: "ma_dat",
        maSach: "ma_sach",
        tenSach: "ten_sach",
        maDocGia: "ma_doc_gia",
        ngayDat: "ngay_dat",
        trangThai: "trang_thai",
        hanNhan: "han_nhan",
        copyId: "copy_id",
        queue_position: "queue_position"
      },
      statsBookOut: {
        maSach: "ma_sach",
        tenSach: "ten_sach",
        soLanMuon: "so_lan_muon"
      },
      statsReaderOut: {
        maDocGia: "ma_doc_gia",
        hoTen: "ho_ten",
        soPhieuMuon: "so_phieu_muon"
      },
      statsOverdueOut: {
        maPhieu: "ma_phieu",
        maSach: "ma_sach",
        tenSach: "ten_sach",
        maDocGia: "ma_doc_gia",
        hoTen: "ho_ten",
        soNgayQuaHan: "so_ngay_qua_han"
      },
      aiConfigOut: {
        provider: "provider",
        model: "model",
        apiKeyMasked: "api_key_masked",
        hasApiKey: "has_api_key",
        promptTemplate: "prompt_template"
      },
      backupOut: {
        message: "message",
        path: "path"
      },
      restoreOut: {
        message: "message"
      }
    },
    roleMap: {
      admin: "admin",
      librarian: "librarian",
      reader: "reader"
    },
    queryMap: {
      books: {
        q: "q",
        theLoai: "theLoai",
        trangThai: "trangThai",
        sort: "sort",
        order: "order"
      },
      borrows: {
        docGia: "docGia",
        trangThai: "trangThai"
      },
      requests: {
        maDocGia: "maDocGia",
        trangThai: "trangThai"
      },
      accounts: {
        role: "role"
      }
    },
    /*
     * Sắp xếp sách (chức năng 5) — Backend ĐÃ hỗ trợ sort/order
     * (api_docs 0.13.0), dùng sắp xếp server-side.
     */
    sortBooksBackend: false
  };

  function missingConfig(name) {
    return {
      ok: false,
      code: "API_CHUA_CO_TAI_LIEU",
      message:
        'Chưa có tài liệu API từ Backend nên chưa thể gọi "' + name + '". ' +
        "Cập nhật Frontend/js/api.js khi có tài liệu từ Thư Ký."
    };
  }

  function call(name, payload, method, pathParams, query) {
    var endpoint = config.endpoints[name];
    if (!config.baseUrl || !endpoint) {
      return Promise.resolve(missingConfig(name));
    }

    var url = config.baseUrl + endpoint;
    if (pathParams) {
      Object.keys(pathParams).forEach(function (key) {
        url = url.split("{" + key + "}").join(encodeURIComponent(pathParams[key]));
      });
    }
    if (query) {
      var parts = [];
      Object.keys(query).forEach(function (key) {
        var value = query[key];
        if (value !== undefined && value !== null && value !== "") {
          parts.push(encodeURIComponent(key) + "=" + encodeURIComponent(value));
        }
      });
      if (parts.length > 0) {
        url += (url.indexOf("?") === -1 ? "?" : "&") + parts.join("&");
      }
    }

    var options = {
      method: method || "GET",
      headers: { Accept: "application/json" }
    };

    if (payload !== undefined) {
      options.headers["Content-Type"] = "application/json";
      options.body = JSON.stringify(payload);
    }

    var session = null;
    try {
      var raw = sessionStorage.getItem("thuvien_session") || localStorage.getItem("thuvien_session");
      session = raw ? JSON.parse(raw) : null;
    } catch (e) {
      session = null;
    }
    if (session && session.token) {
      options.headers.Authorization = "Bearer " + session.token;
    }

    return fetch(url, options)
      .then(function (res) {
        var textPromise = res.text();
        return textPromise.then(function (text) {
          var data = null;
          if (text) {
            try {
              data = JSON.parse(text);
            } catch (e) {
              data = text;
            }
          }
          if (!res.ok) {
            var rawDetail = data && (data.message || data.detail);
            var message;
            if (Array.isArray(rawDetail)) {
              message = rawDetail
                .map(function (d) {
                  return d && d.msg ? d.msg : JSON.stringify(d);
                })
                .join("; ");
            } else if (rawDetail && typeof rawDetail === "object") {
              message = JSON.stringify(rawDetail);
            } else {
              message = rawDetail ? String(rawDetail) : "Lỗi máy chủ: HTTP " + res.status;
            }
            return {
              ok: false,
              code: "HTTP_" + res.status,
              status: res.status,
              message: message,
              data: data,
              fieldErrors: data && data.errors ? data.errors : null
            };
          }
          return { ok: true, status: res.status, data: data };
        });
      })
      .catch(function (err) {
        return {
          ok: false,
          code: "NETWORK_ERROR",
          message:
            "Không kết nối được máy chủ. Kiểm tra baseUrl trong api.js và cấu hình CORS của Backend.",
          error: err
        };
      });
  }

  function serializeForm(form, section) {
    var map = config.fieldMap[section];
    if (!map || Object.keys(map).length === 0) {
      return {
        ok: false,
        message:
          'Chưa có cấu hình field cho "' + section + '" trong api.js nên chưa thể gửi dữ liệu.'
      };
    }
    var payload = {};
    Object.keys(map).forEach(function (internalKey) {
      var input = form.elements[internalKey];
      var value = "";
      if (input) {
        if (input.type === "checkbox") {
          value = input.checked;
        } else if (input.type === "number") {
          value = input.value === "" ? "" : Number(input.value);
        } else {
          value = input.value;
        }
      }
      payload[map[internalKey]] = value;
    });
    return { ok: true, payload: payload };
  }

  function mapResponse(section, item) {
    var map = config.fieldMap[section];
    if (!map || Object.keys(map).length === 0) {
      return null;
    }
    var out = {};
    Object.keys(map).forEach(function (internalKey) {
      var apiKey = map[internalKey];
      out[internalKey] = item && item[apiKey] !== undefined ? item[apiKey] : "";
    });
    return out;
  }

  function canonicalRole(rawRole) {
    var map = config.roleMap || {};
    if (map[rawRole]) {
      return map[rawRole];
    }
    if (["admin", "librarian", "reader"].indexOf(rawRole) !== -1) {
      return rawRole;
    }
    return "";
  }

  function buildQuery(name, params) {
    var map = config.queryMap[name];
    if (!map) {
      return { ok: false, query: {} };
    }
    var query = {};
    Object.keys(map).forEach(function (internalKey) {
      var value = params ? params[internalKey] : undefined;
      if (value !== undefined && value !== null && value !== "") {
        query[map[internalKey]] = value;
      }
    });
    return { ok: true, query: query };
  }

  function sortBooks(list, sort, order) {
    if (!Array.isArray(list) || !sort) {
      return list;
    }
    var dir = order === "desc" ? -1 : 1;
    var arr = list.slice();
    arr.sort(function (a, b) {
      if (sort === "ten") {
        return String(a.ten || "").localeCompare(String(b.ten || ""), "vi") * dir;
      }
      if (sort === "tacGia") {
        return String(a.tacGia || "").localeCompare(String(b.tacGia || ""), "vi") * dir;
      }
      if (sort === "namXb") {
        return ((Number(a.namXb) || 0) - (Number(b.namXb) || 0)) * dir;
      }
      if (sort === "soLuong") {
        return ((Number(a.soLuong) || 0) - (Number(b.soLuong) || 0)) * dir;
      }
      return 0;
    });
    return arr;
  }

  function uploadFile(name, file) {
    var endpoint = config.endpoints[name];
    if (!config.baseUrl || !endpoint) {
      return Promise.resolve({
        ok: false,
        code: "API_CHUA_CO_TAI_LIEU",
        message: 'Chưa có cấu hình endpoint "' + name + '" trong api.js.'
      });
    }
    var form = new FormData();
    form.append("file", file);
    var options = {
      method: "POST",
      body: form,
      headers: { Accept: "application/json" }
    };
    var session = null;
    try {
      var raw = sessionStorage.getItem("thuvien_session") || localStorage.getItem("thuvien_session");
      session = raw ? JSON.parse(raw) : null;
    } catch (e) {
      session = null;
    }
    if (session && session.token) {
      options.headers.Authorization = "Bearer " + session.token;
    }
    return fetch(config.baseUrl + endpoint, options)
      .then(function (res) {
        return res.text().then(function (text) {
          var data = null;
          if (text) {
            try {
              data = JSON.parse(text);
            } catch (e) {
              data = text;
            }
          }
          if (!res.ok) {
            var rawDetail = data && (data.message || data.detail);
            var message;
            if (Array.isArray(rawDetail)) {
              message = rawDetail
                .map(function (d) {
                  return d && d.msg ? d.msg : JSON.stringify(d);
                })
                .join("; ");
            } else if (rawDetail && typeof rawDetail === "object") {
              message = JSON.stringify(rawDetail);
            } else {
              message = rawDetail ? String(rawDetail) : "Lỗi máy chủ: HTTP " + res.status;
            }
            return {
              ok: false,
              code: "HTTP_" + res.status,
              status: res.status,
              message: message,
              data: data,
              fieldErrors: data && data.errors ? data.errors : null
            };
          }
          return { ok: true, status: res.status, data: data };
        });
      })
      .catch(function (err) {
        return {
          ok: false,
          code: "NETWORK_ERROR",
          message:
            "Không kết nối được máy chủ. Kiểm tra baseUrl trong api.js và cấu hình CORS của Backend.",
          error: err
        };
      });
  }

  function downloadFile(name, filename) {
    var endpoint = config.endpoints[name];
    if (!config.baseUrl || !endpoint) {
      return Promise.resolve({
        ok: false,
        code: "API_CHUA_CO_TAI_LIEU",
        message: 'Chưa có cấu hình endpoint export "' + name + '" trong api.js.'
      });
    }
    var session = null;
    try {
      var raw = sessionStorage.getItem("thuvien_session") || localStorage.getItem("thuvien_session");
      session = raw ? JSON.parse(raw) : null;
    } catch (e) {
      session = null;
    }
    var headers = { Accept: "text/csv, application/octet-stream" };
    if (session && session.token) {
      headers.Authorization = "Bearer " + session.token;
    }
    return fetch(config.baseUrl + endpoint, { headers: headers })
      .then(function (res) {
        if (!res.ok) {
          return res.text().then(function (text) {
            var message = text && text.indexOf("{") === 0 ? text : "Lỗi khi tải file: HTTP " + res.status;
            return { ok: false, status: res.status, message: message };
          });
        }
        return res.blob().then(function (blob) {
          var url = URL.createObjectURL(blob);
          var a = document.createElement("a");
          a.href = url;
          a.download = filename;
          document.body.appendChild(a);
          a.click();
          a.remove();
          URL.revokeObjectURL(url);
          return { ok: true };
        });
      })
      .catch(function (err) {
        return {
          ok: false,
          code: "NETWORK_ERROR",
          message: "Không tải được file xuất dữ liệu.",
          error: err
        };
      });
  }

  return {
    config: config,
    call: call,
    serializeForm: serializeForm,
    mapResponse: mapResponse,
    canonicalRole: canonicalRole,
    buildQuery: buildQuery,
    sortBooks: sortBooks,
    uploadFile: uploadFile,
    downloadFile: downloadFile
  };
})();
