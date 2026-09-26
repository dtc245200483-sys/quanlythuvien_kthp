import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import CORS_ORIGINS, STATIC_DIR
from .routers import (
    accounts, admin, auth, books, borrows, catalog, 
    chatbot, export, notifications, profile, readers, 
    requests, reservations, stats
)

os.makedirs(os.path.join(STATIC_DIR, "avatars"), exist_ok=True)

from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

app = FastAPI(
    title="Hệ thống quản lý thư viện - Backend API",
    version="0.1.0",
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    errors = exc.errors()
    translated_errors = []
    field_errors_dict = {}
    for err in errors:
        msg = err.get("msg", "")
        # Translate common Pydantic validation errors
        if "String should have at most" in msg:
            max_chars = msg.split("at most ")[1].split(" ")[0]
            msg = f"Độ dài tối đa là {max_chars} ký tự."
        elif "String should have at least" in msg:
            min_chars = msg.split("at least ")[1].split(" ")[0]
            msg = f"Độ dài tối thiểu là {min_chars} ký tự."
        elif "Field required" in msg:
            msg = "Trường này là bắt buộc."
        elif "Input should be a valid string" in msg:
            msg = "Vui lòng nhập chuỗi ký tự hợp lệ."
        elif "Input should be greater than or equal to" in msg:
            val = msg.split("equal to ")[1]
            msg = f"Giá trị phải lớn hơn hoặc bằng {val}."
        elif "Input should be less than or equal to" in msg:
            val = msg.split("equal to ")[1]
            msg = f"Giá trị phải nhỏ hơn hoặc bằng {val}."
        elif "valid integer" in msg or "unable to parse string as an integer" in msg:
            msg = "Phải là số nguyên hợp lệ."
        elif "valid number" in msg or "unable to parse" in msg:
            msg = "Phải là một số hợp lệ."
        
        # Build field path
        loc = err.get("loc", [])
        field_name = ".".join([str(x) for x in loc if str(x) != "body"])
        field_name_original = field_name
        
        field_labels = {
            "ma": "Mã",
            "ten": "Tên",
            "tacGia": "Tác giả",
            "theLoai": "Thể loại",
            "nxb": "Nhà xuất bản",
            "namXb": "Năm xuất bản",
            "soLuong": "Số lượng",
            "anhBia": "Ảnh bìa",
            "username": "Tài khoản",
            "password": "Mật khẩu",
            "hoTen": "Họ tên",
            "email": "Email",
            "soDienThoai": "Số điện thoại",
        }
        
        # Custom messages for specific fields
        if field_name == "theLoai" and ("tối thiểu là 1" in msg or "bắt buộc" in msg):
            msg = "Vui lòng chọn thể loại."
            field_name = ""
        elif field_name == "nxb" and ("tối thiểu là 1" in msg or "bắt buộc" in msg):
            msg = "Vui lòng chọn nhà xuất bản."
            field_name = ""
        elif field_name in ["ten", "tacGia", "ma", "hoTen", "username", "password", "email", "soDienThoai", "anhBia"] and ("tối thiểu là 1" in msg or "bắt buộc" in msg):
            label = field_labels.get(field_name, field_name).lower()
            msg = f"Vui lòng nhập {label}."
            field_name = ""
            
        if field_name:
            field_display = field_labels.get(field_name, field_name)
            translated_errors.append(f"{field_display}: {msg}")
            field_errors_dict[field_name_original] = msg
        else:
            translated_errors.append(msg)
            # If we don't have a specific field name anymore (like for theLoai/nxb overrides), we use the original one
            if field_name_original:
                field_errors_dict[field_name_original] = msg
            
    return JSONResponse(
        status_code=422,
        content={
            "detail": "; ".join(translated_errors),
            "errors": field_errors_dict
        },
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_no_cache_headers(request: Request, call_next):
    response = await call_next(request)
    path = request.url.path
    if path.endswith((".js", ".css", ".html")) or path == "/" or "/static/" in path:
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response

app.include_router(auth.router)
app.include_router(books.router)
app.include_router(admin.router)
app.include_router(readers.router)
app.include_router(borrows.router)
app.include_router(requests.router)
app.include_router(accounts.router)
app.include_router(catalog.router)
app.include_router(reservations.router)
app.include_router(notifications.router)
app.include_router(stats.router)
app.include_router(export.router)
app.include_router(profile.router)
app.include_router(chatbot.router)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

frontend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend"))
if not os.path.exists(frontend_path):
    frontend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "Frontend"))
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
