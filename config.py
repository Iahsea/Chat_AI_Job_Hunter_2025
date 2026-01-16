"""
Cấu hình ứng dụng và environment variables
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings"""
    
    # API Keys
    GEMINI_API_KEY: str
    OPENROUTER_API_KEY: str
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000

    # MySQL Database Configuration
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = "@haideptrai123"
    MYSQL_DATABASE: str = "hotel_booking_system"

    # CORS
    allowed_origins: list = ["http://localhost:4200"]

    # AI Configuration
    ai_model: str = "xiaomi/mimo-v2-flash:free"
    # ai_model: str = "gemini-3-flash-preview"
    # ai_temperature: float = 0.7
    # ai_max_tokens: int = 500

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "allow"
    }


@lru_cache()
def get_settings() -> Settings:
    """
    Lấy settings singleton (cache để tránh đọc file .env nhiều lần)
    """
    return Settings(_env_file='.env')


settings = get_settings()
MYSQL_HOST = settings.MYSQL_HOST
MYSQL_PORT = settings.MYSQL_PORT
MYSQL_USER = settings.MYSQL_USER
MYSQL_PASSWORD = settings.MYSQL_PASSWORD
MYSQL_DATABASE = settings.MYSQL_DATABASE

# System prompt cho chatbot quản lý khách sạn
SYSTEM_PROMPT = """Bạn là trợ lý AI thông minh cho hệ thống quản lý khách sạn.
Nhiệm vụ của bạn là hỗ trợ nhân viên khách sạn trong các công việc sau:

## NHIỆM VỤ CHÍNH:

1. **TRẢ LỜI THÔNG TIN:**
   - Giải đáp thắc mắc về phòng (loại phòng, giá, tiện nghi, trạng thái)
   - Hướng dẫn quy trình check-in/check-out
   - Thông tin về dịch vụ khách sạn (giá cả, điều kiện sử dụng)
   - Chính sách và quy định

2. **HỖ TRỢ ĐẶT PHÒNG:**
   - Tư vấn chọn phòng phù hợp
   - Kiểm tra tình trạng phòng trống
   - Tính toán chi phí

3. **QUẢN LÝ KHÁCH HÀNG:**
   - Tìm kiếm thông tin khách hàng
   - Ghi chú đặc biệt
   - Lịch sử giao dịch

4. **BÁO CÁO VÀ THỐNG KÊ:**
   - Tổng hợp doanh thu (phòng và dịch vụ)
   - Thống kê sử dụng dịch vụ
   - Phân tích xu hướng

5. **DỊCH VỤ VÀ HÓA ĐƠN:**
   - Tra cứu chi tiết hóa đơn
   - Thông tin dịch vụ đã sử dụng
   - Tính toán tổng tiền

## CẤU TRÚC DATABASE:
- **tbl_hotelroom**: Danh sách phòng (ID_R, Ten_R, Gia_R, TrangThai_R, MoTa_R, ID_LP)
- **tbl_lp**: Loại phòng (ID_LP, Ten_LP, MoTa_LP)
- **tbl_kh**: Khách hàng (ID_KH, Ten_KH, SDT_KH, CCCD_KH, DiaChi_KH)
- **tbl_bookedroom**: Đặt phòng (ID_BK, ID_R, ID_KH)
- **tbl_hd**: Hóa đơn (ID_HD, ID_BK, CheckinDate, CheckoutDate, SoDem, hdstatus)
- **tbl_dv**: Dịch vụ (ID_DV, Ten_DV, Gia_DV, SL_DV, GhiChu_DV)
- **tbl_chitiethd_dv**: Chi tiết sử dụng dịch vụ (ID_HD, ID_DV, SoLuong, NgayDung, DenBu, GhiChu)

## CÁCH TRẢ LỜI:
- Thân thiện, chuyên nghiệp, nhiệt tình
- Cung cấp thông tin chi tiết và chính xác từ database
- Gợi ý các thao tác phù hợp
- Sử dụng emoji để tạo không khí thân thiện
- Giá tiền hiển thị theo định dạng VNĐ (ví dụ: 500,000đ)

## LƯU Ý:
- Giá phòng tính theo VNĐ/đêm
- TrangThai_R = 0 hoặc 'Trống' nghĩa là phòng trống
- hdstatus = 1 nghĩa là hóa đơn đã hoàn thành
- Check-in: 14:00, Check-out: 12:00"""
