"""
Database module - Kết nối và truy vấn MySQL database hotel_booking_system
"""

import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

load_dotenv()


class DatabaseManager:
    """Quản lý kết nối và truy vấn database hotel_booking_system"""
    
    def __init__(self):
        self.config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': int(os.getenv('DB_PORT', 3306)),
            'database': os.getenv('DB_NAME', 'hotel_booking_system'),
            'user': os.getenv('DB_USER', 'root'),
            'password': os.getenv('DB_PASSWORD', ''),
            'charset': 'utf8mb4',
            'use_unicode': True
        }
    
    def get_connection(self):
        """Tạo kết nối database"""
        try:
            connection = mysql.connector.connect(**self.config)
            return connection
        except Error as e:
            print(f"Lỗi kết nối database: {e}")
            return None
    
    def execute_query(self, query: str, params: tuple = None) -> list:
        """Thực thi truy vấn và trả về kết quả"""
        connection = self.get_connection()
        if not connection:
            return []
        
        try:
            cursor = connection.cursor(dictionary=True)
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            results = cursor.fetchall()
            return results
        except Error as e:
            print(f"Lỗi truy vấn: {e}")
            return []
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    
    # ============ KHÁCH SẠN (hotels) ============
    
    def get_all_hotels(self) -> list:
        """Lấy danh sách tất cả khách sạn đã được duyệt"""
        query = """
            SELECT h.id, h.name, h.address, h.city, h.country, h.description, 
                   h.rating, h.status, u.full_name as owner_name
            FROM hotels h
            LEFT JOIN users u ON h.owner_id = u.id
            WHERE h.status = 'APPROVED'
            ORDER BY h.rating DESC, h.name
        """
        return self.execute_query(query)
    
    def get_hotel_by_id(self, hotel_id: int) -> dict:
        """Lấy thông tin khách sạn theo ID"""
        query = """
            SELECT h.*, u.full_name as owner_name, u.email as owner_email
            FROM hotels h
            LEFT JOIN users u ON h.owner_id = u.id
            WHERE h.id = %s
        """
        results = self.execute_query(query, (hotel_id,))
        return results[0] if results else None
    
    def get_hotels_by_city(self, city: str) -> list:
        """Tìm khách sạn theo thành phố"""
        query = """
            SELECT h.id, h.name, h.address, h.city, h.rating, h.description
            FROM hotels h
            WHERE h.city LIKE %s AND h.status = 'APPROVED'
            ORDER BY h.rating DESC
        """
        return self.execute_query(query, (f"%{city}%",))
    
    def search_hotels(self, keyword: str) -> list:
        """Tìm kiếm khách sạn theo từ khóa"""
        query = """
            SELECT h.id, h.name, h.address, h.city, h.rating, h.description
            FROM hotels h
            WHERE h.status = 'APPROVED' 
              AND (h.name LIKE %s OR h.city LIKE %s OR h.description LIKE %s)
            ORDER BY h.rating DESC
        """
        keyword_param = f"%{keyword}%"
        return self.execute_query(query, (keyword_param, keyword_param, keyword_param))
    
    # ============ LOẠI PHÒNG (room_types) ============
    
    def get_all_room_types(self) -> list:
        """Lấy danh sách tất cả loại phòng đã được duyệt"""
        query = """
            SELECT rt.id, rt.name, rt.description, rt.room_type, rt.price_per_night,
                   rt.total_rooms, rt.available_rooms, rt.max_occupancy, rt.status,
                   h.name as hotel_name, h.city as hotel_city
            FROM room_types rt
            JOIN hotels h ON rt.hotel_id = h.id
            WHERE rt.status = 'APPROVED' AND h.status = 'APPROVED'
            ORDER BY rt.price_per_night ASC
        """
        return self.execute_query(query)
    
    def get_room_types_by_hotel(self, hotel_id: int) -> list:
        """Lấy danh sách loại phòng của một khách sạn"""
        query = """
            SELECT rt.id, rt.name, rt.description, rt.room_type, rt.price_per_night,
                   rt.total_rooms, rt.available_rooms, rt.max_occupancy,
                   rtd.room_size, rtd.bed_type, rtd.bed_count, rtd.room_view
            FROM room_types rt
            LEFT JOIN room_type_details rtd ON rt.id = rtd.room_type_id
            WHERE rt.hotel_id = %s AND rt.status = 'APPROVED'
            ORDER BY rt.price_per_night ASC
        """
        return self.execute_query(query, (hotel_id,))
    
    def get_available_rooms(self, check_in: str = None, check_out: str = None) -> list:
        """Lấy danh sách phòng còn trống"""
        query = """
            SELECT rt.id, rt.name, rt.room_type, rt.price_per_night, 
                   rt.available_rooms, rt.max_occupancy,
                   h.name as hotel_name, h.city as hotel_city, h.rating
            FROM room_types rt
            JOIN hotels h ON rt.hotel_id = h.id
            WHERE rt.status = 'APPROVED' 
              AND h.status = 'APPROVED'
              AND rt.available_rooms > 0
            ORDER BY rt.price_per_night ASC
        """
        return self.execute_query(query)
    
    def get_room_type_by_id(self, room_type_id: int) -> dict:
        """Lấy thông tin chi tiết loại phòng theo ID"""
        query = """
            SELECT rt.*, h.name as hotel_name, h.city as hotel_city, h.address as hotel_address,
                   rtd.room_size, rtd.bed_type, rtd.bed_count, rtd.room_view, rtd.has_balcony,
                   rtp.smoking_policy, rtp.cancellation_policy, rtp.check_in_time, rtp.check_out_time
            FROM room_types rt
            JOIN hotels h ON rt.hotel_id = h.id
            LEFT JOIN room_type_details rtd ON rt.id = rtd.room_type_id
            LEFT JOIN room_type_policies rtp ON rt.id = rtp.room_type_id
            WHERE rt.id = %s
        """
        results = self.execute_query(query, (room_type_id,))
        return results[0] if results else None
    
    # ============ ĐẶT PHÒNG (bookings) ============
    
    def get_all_bookings(self) -> list:
        """Lấy danh sách tất cả đặt phòng"""
        query = """
            SELECT b.id, b.guest_name, b.guest_email, b.guest_phone,
                   b.check_in_date, b.check_out_date, b.number_of_guests,
                   b.number_of_rooms, b.total_price, b.booking_status,
                   b.special_requests, b.created_at,
                   rt.name as room_type_name, rt.room_type,
                   h.name as hotel_name, h.city as hotel_city,
                   u.full_name as user_name
            FROM bookings b
            JOIN room_types rt ON b.room_type_id = rt.id
            JOIN hotels h ON rt.hotel_id = h.id
            LEFT JOIN users u ON b.user_id = u.id
            ORDER BY b.created_at DESC
        """
        return self.execute_query(query)
    
    def get_booking_by_id(self, booking_id: int) -> dict:
        """Lấy thông tin đặt phòng theo ID"""
        query = """
            SELECT b.*, rt.name as room_type_name, rt.room_type, rt.price_per_night,
                   h.name as hotel_name, h.city as hotel_city, h.address as hotel_address,
                   u.full_name as user_name, u.email as user_email
            FROM bookings b
            JOIN room_types rt ON b.room_type_id = rt.id
            JOIN hotels h ON rt.hotel_id = h.id
            LEFT JOIN users u ON b.user_id = u.id
            WHERE b.id = %s
        """
        results = self.execute_query(query, (booking_id,))
        return results[0] if results else None
    
    def get_bookings_by_status(self, status: str) -> list:
        """Lấy danh sách đặt phòng theo trạng thái"""
        query = """
            SELECT b.id, b.guest_name, b.check_in_date, b.check_out_date,
                   b.total_price, b.booking_status,
                   rt.name as room_type_name, h.name as hotel_name
            FROM bookings b
            JOIN room_types rt ON b.room_type_id = rt.id
            JOIN hotels h ON rt.hotel_id = h.id
            WHERE b.booking_status = %s
            ORDER BY b.created_at DESC
        """
        return self.execute_query(query, (status,))
    
    def get_bookings_by_date_range(self, start_date: str, end_date: str) -> list:
        """Lấy đặt phòng trong khoảng thời gian"""
        query = """
            SELECT b.id, b.guest_name, b.check_in_date, b.check_out_date,
                   b.total_price, b.booking_status,
                   rt.name as room_type_name, h.name as hotel_name
            FROM bookings b
            JOIN room_types rt ON b.room_type_id = rt.id
            JOIN hotels h ON rt.hotel_id = h.id
            WHERE b.check_in_date >= %s AND b.check_out_date <= %s
            ORDER BY b.check_in_date
        """
        return self.execute_query(query, (start_date, end_date))
    
    # ============ THANH TOÁN (payments) ============
    
    def get_all_payments(self) -> list:
        """Lấy danh sách tất cả thanh toán"""
        query = """
            SELECT p.id, p.payment_method, p.payment_status, p.amount,
                   p.transaction_id, p.payment_date, p.created_at,
                   b.guest_name, b.check_in_date, b.check_out_date,
                   h.name as hotel_name
            FROM payments p
            JOIN bookings b ON p.booking_id = b.id
            JOIN room_types rt ON b.room_type_id = rt.id
            JOIN hotels h ON rt.hotel_id = h.id
            ORDER BY p.created_at DESC
        """
        return self.execute_query(query)
    
    def get_payment_by_booking(self, booking_id: int) -> dict:
        """Lấy thông tin thanh toán theo booking ID"""
        query = """
            SELECT p.*, b.guest_name, b.total_price as booking_total
            FROM payments p
            JOIN bookings b ON p.booking_id = b.id
            WHERE p.booking_id = %s
        """
        results = self.execute_query(query, (booking_id,))
        return results[0] if results else None
    
    # ============ NGƯỜI DÙNG (users) ============
    
    def get_all_users(self) -> list:
        """Lấy danh sách tất cả người dùng"""
        query = """
            SELECT id, username, full_name, email, phone, role, is_active, created_at
            FROM users
            ORDER BY created_at DESC
        """
        return self.execute_query(query)

    def get_user_stats(self) -> dict:
            """Thống kê người dùng"""
            query = """
                SELECT 
                    COUNT(*) as total_users,
                    SUM(CASE WHEN role = 'CUSTOMER' THEN 1 ELSE 0 END) as customers,
                    SUM(CASE WHEN role = 'HOTEL_OWNER' THEN 1 ELSE 0 END) as hotel_owners
                FROM users
            """
            results = self.execute_query(query)
            return results[0] if results else {}            
    
    def get_user_by_id(self, user_id: int) -> dict:
        """Lấy thông tin người dùng theo ID"""
        query = """
            SELECT id, username, full_name, email, phone, role, is_active, created_at
            FROM users
            WHERE id = %s
        """
        results = self.execute_query(query, (user_id,))
        return results[0] if results else None
    
    def get_users_by_role(self, role: str) -> list:
        """Lấy danh sách người dùng theo vai trò"""
        query = """
            SELECT id, username, full_name, email, phone, role, is_active
            FROM users
            WHERE role = %s
            ORDER BY full_name
        """
        return self.execute_query(query, (role,))
    
    # ============ TIỆN NGHI (amenities) ============
    
    def get_all_amenities(self) -> list:
        """Lấy danh sách tất cả tiện nghi"""
        query = """
            SELECT id, name, description, category
            FROM amenities
            ORDER BY category, name
        """
        return self.execute_query(query)
    
    def get_amenities_by_hotel(self, hotel_id: int) -> list:
        """Lấy danh sách tiện nghi của một khách sạn"""
        query = """
            SELECT a.id, a.name, a.description, a.category
            FROM amenities a
            JOIN hotel_amenities ha ON a.id = ha.amenity_id
            WHERE ha.hotel_id = %s
            ORDER BY a.category, a.name
        """
        return self.execute_query(query, (hotel_id,))
    
    def get_amenities_by_room_type(self, room_type_id: int) -> list:
        """Lấy danh sách tiện nghi của một loại phòng"""
        query = """
            SELECT a.id, a.name, a.description, a.category
            FROM amenities a
            JOIN room_type_amenities rta ON a.id = rta.amenity_id
            WHERE rta.room_type_id = %s
            ORDER BY a.category, a.name
        """
        return self.execute_query(query, (room_type_id,))
    
    # ============ ĐÁNH GIÁ (reviews) ============
    
    def get_reviews_by_hotel(self, hotel_id: int) -> list:
        """Lấy danh sách đánh giá của một khách sạn"""
        query = """
            SELECT r.id, r.rating, r.comment, r.created_at,
                   u.full_name as reviewer_name, rt.name as room_type_name
            FROM reviews r
            JOIN users u ON r.user_id = u.id
            JOIN room_types rt ON r.room_type_id = rt.id
            WHERE r.hotel_id = %s
            ORDER BY r.created_at DESC
        """
        return self.execute_query(query, (hotel_id,))
    
    def get_average_rating_by_hotel(self, hotel_id: int) -> dict:
        """Lấy điểm đánh giá trung bình của khách sạn"""
        query = """
            SELECT AVG(rating) as avg_rating, COUNT(*) as total_reviews
            FROM reviews
            WHERE hotel_id = %s
        """
        results = self.execute_query(query, (hotel_id,))
        return results[0] if results else None
    
    # ============ LIÊN HỆ (contacts) ============
    
    def get_all_contacts(self) -> list:
        """Lấy danh sách tất cả liên hệ"""
        query = """
            SELECT id, name, email, subject, message, is_read, created_at
            FROM contacts
            ORDER BY created_at DESC
        """
        return self.execute_query(query)
    
    def get_unread_contacts(self) -> list:
        """Lấy danh sách liên hệ chưa đọc"""
        query = """
            SELECT id, name, email, subject, message, created_at
            FROM contacts
            WHERE is_read = 0
            ORDER BY created_at DESC
        """
        return self.execute_query(query)
    
    # ============ THỐNG KÊ ============
    
    def get_booking_stats(self) -> dict:
        """Thống kê đặt phòng"""
        query = """
            SELECT 
                COUNT(*) as total_bookings,
                SUM(CASE WHEN booking_status = 'PENDING' THEN 1 ELSE 0 END) as pending,
                SUM(CASE WHEN booking_status = 'CONFIRMED' THEN 1 ELSE 0 END) as confirmed,
                SUM(CASE WHEN booking_status = 'COMPLETED' THEN 1 ELSE 0 END) as completed,
                SUM(CASE WHEN booking_status = 'CANCELLED' THEN 1 ELSE 0 END) as cancelled
            FROM bookings
        """
        results = self.execute_query(query)
        return results[0] if results else {}
    
    def get_revenue_stats(self) -> dict:
        """Thống kê doanh thu"""
        query = """
            SELECT 
                SUM(CASE WHEN p.payment_status = 'PAID' THEN p.amount ELSE 0 END) as total_revenue,
                SUM(CASE WHEN p.payment_status = 'PENDING' THEN p.amount ELSE 0 END) as pending_revenue,
                COUNT(DISTINCT CASE WHEN p.payment_status = 'PAID' THEN p.booking_id END) as paid_bookings
            FROM payments p
        """
        results = self.execute_query(query)
        return results[0] if results else {}
    
    def get_monthly_revenue(self) -> list:
        """Thống kê doanh thu theo tháng"""
        query = """
            SELECT 
                DATE_FORMAT(p.payment_date, '%Y-%m') as month,
                COUNT(DISTINCT p.booking_id) as total_bookings,
                SUM(p.amount) as total_revenue
            FROM payments p
            WHERE p.payment_status = 'PAID' AND p.payment_date IS NOT NULL
            GROUP BY DATE_FORMAT(p.payment_date, '%Y-%m')
            ORDER BY month DESC
            LIMIT 12
        """
        return self.execute_query(query)
    
    def get_hotel_stats(self) -> dict:
        """Thống kê khách sạn"""
        query = """
            SELECT 
                COUNT(*) as total_hotels,
                SUM(CASE WHEN status = 'APPROVED' THEN 1 ELSE 0 END) as approved,
                SUM(CASE WHEN status = 'PENDING' THEN 1 ELSE 0 END) as pending,
                SUM(CASE WHEN status = 'REJECTED' THEN 1 ELSE 0 END) as rejected
            FROM hotels
        """
        results = self.execute_query(query)
        return results[0] if results else {}
    
    def get_room_stats(self) -> dict:
        """Thống kê phòng"""
        query = """
            SELECT 
                SUM(total_rooms) as total_rooms,
                SUM(available_rooms) as available_rooms,
                SUM(total_rooms - available_rooms) as occupied_rooms,
                COUNT(*) as total_room_types
            FROM room_types
            WHERE status = 'APPROVED'
        """
        results = self.execute_query(query)
        return results[0] if results else {}
    

    def get_top_hotels_by_bookings(self, limit: int = 10) -> list:
        """Lấy top khách sạn có nhiều đặt phòng nhất"""
        query = """
            SELECT h.id, h.name, h.city, h.rating,
                   COUNT(b.id) as total_bookings,
                   SUM(b.total_price) as total_revenue
            FROM hotels h
            JOIN room_types rt ON h.id = rt.hotel_id
            JOIN bookings b ON rt.id = b.room_type_id
            WHERE h.status = 'APPROVED'
            GROUP BY h.id, h.name, h.city, h.rating
            ORDER BY total_bookings DESC
            LIMIT %s
        """
        return self.execute_query(query, (limit,))
    
    def get_top_room_types_by_bookings(self, limit: int = 10) -> list:
        """Lấy top loại phòng được đặt nhiều nhất"""
        query = """
            SELECT rt.id, rt.name, rt.room_type, rt.price_per_night,
                   h.name as hotel_name, h.city as hotel_city,
                   COUNT(b.id) as total_bookings,
                   SUM(b.total_price) as total_revenue
            FROM room_types rt
            JOIN hotels h ON rt.hotel_id = h.id
            JOIN bookings b ON rt.id = b.room_type_id
            WHERE rt.status = 'APPROVED'
            GROUP BY rt.id, rt.name, rt.room_type, rt.price_per_night, h.name, h.city
            ORDER BY total_bookings DESC
            LIMIT %s
        """
        return self.execute_query(query, (limit,))


# Singleton instance
db_manager = DatabaseManager()


def get_database_context() -> str:
    """
    Lấy thông tin tổng quan từ database để cung cấp context cho AI
    """
    context_parts = []
    
    # Thống kê khách sạn
    hotel_stats = db_manager.get_hotel_stats()
    if hotel_stats:
        context_parts.append("=== THỐNG KÊ KHÁCH SẠN ===")
        context_parts.append(f"- Tổng số khách sạn: {hotel_stats.get('total_hotels', 0)}")
        context_parts.append(f"- Đã duyệt: {hotel_stats.get('approved', 0)}")
        context_parts.append(f"- Chờ duyệt: {hotel_stats.get('pending', 0)}")
    
    # Thống kê phòng
    room_stats = db_manager.get_room_stats()
    if room_stats:
        context_parts.append("\n=== THỐNG KÊ PHÒNG ===")
        context_parts.append(f"- Tổng số phòng: {room_stats.get('total_rooms', 0)}")
        context_parts.append(f"- Phòng trống: {room_stats.get('available_rooms', 0)}")
        context_parts.append(f"- Phòng đang sử dụng: {room_stats.get('occupied_rooms', 0)}")
        context_parts.append(f"- Số loại phòng: {room_stats.get('total_room_types', 0)}")
    
    # Danh sách khách sạn
    hotels = db_manager.get_all_hotels()
    if hotels:
        context_parts.append("\n=== DANH SÁCH KHÁCH SẠN ===")
        for hotel in hotels[:15]:  # Giới hạn 15 khách sạn
            rating = f"⭐{hotel['rating']}" if hotel.get('rating') else "Chưa có đánh giá"
            context_parts.append(f"- {hotel['name']} ({hotel['city']}): {rating}")
    
    # Danh sách loại phòng có sẵn
    rooms = db_manager.get_available_rooms()
    if rooms:
        context_parts.append("\n=== PHÒNG CÒN TRỐNG ===")
        for room in rooms[:15]:  # Giới hạn 15 phòng
            price = f"{int(room['price_per_night']):,}đ/đêm" if room.get('price_per_night') else "Liên hệ"
            context_parts.append(f"- {room['name']} tại {room['hotel_name']} ({room['hotel_city']}): {price} - Còn {room['available_rooms']} phòng")
    
    # Thống kê đặt phòng
    booking_stats = db_manager.get_booking_stats()
    if booking_stats:
        context_parts.append("\n=== THỐNG KÊ ĐẶT PHÒNG ===")
        context_parts.append(f"- Tổng số đặt phòng: {booking_stats.get('total_bookings', 0)}")
        context_parts.append(f"- Chờ xác nhận: {booking_stats.get('pending', 0)}")
        context_parts.append(f"- Đã xác nhận: {booking_stats.get('confirmed', 0)}")
        context_parts.append(f"- Hoàn thành: {booking_stats.get('completed', 0)}")
        context_parts.append(f"- Đã hủy: {booking_stats.get('cancelled', 0)}")
    
    # Thống kê doanh thu
    revenue_stats = db_manager.get_revenue_stats()
    if revenue_stats:
        context_parts.append("\n=== THỐNG KÊ DOANH THU ===")
        total_revenue = revenue_stats.get('total_revenue') or 0
        pending_revenue = revenue_stats.get('pending_revenue') or 0
        context_parts.append(f"- Tổng doanh thu: {int(total_revenue):,}đ")
        context_parts.append(f"- Doanh thu chờ thanh toán: {int(pending_revenue):,}đ")
        context_parts.append(f"- Số booking đã thanh toán: {revenue_stats.get('paid_bookings', 0)}")
    
    # Doanh thu theo tháng
    monthly_revenue = db_manager.get_monthly_revenue()
    if monthly_revenue:
        context_parts.append("\n=== DOANH THU THEO THÁNG ===")
        for month in monthly_revenue[:6]:  # 6 tháng gần nhất
            revenue = month.get('total_revenue') or 0
            context_parts.append(f"- Tháng {month['month']}: {int(revenue):,}đ ({month['total_bookings']} booking)")
    
    # Thống kê người dùng
    user_stats = db_manager.get_user_stats()
    if user_stats:
        context_parts.append("\n=== THỐNG KÊ NGƯỜI DÙNG ===")
        context_parts.append(f"- Tổng người dùng: {user_stats.get('total_users', 0)}")
        context_parts.append(f"- Khách hàng: {user_stats.get('customers', 0)}")
        context_parts.append(f"- Chủ khách sạn: {user_stats.get('hotel_owners', 0)}")
    
    # Top khách sạn
    top_hotels = db_manager.get_top_hotels_by_bookings(5)
    if top_hotels:
        context_parts.append("\n=== TOP KHÁCH SẠN ĐƯỢC ĐẶT NHIỀU NHẤT ===")
        for hotel in top_hotels:
            revenue = hotel.get('total_revenue') or 0
            context_parts.append(f"- {hotel['name']} ({hotel['city']}): {hotel['total_bookings']} đặt phòng, doanh thu {int(revenue):,}đ")
    
    return "\n".join(context_parts)


def get_hotel_details_for_ai(hotel_id: int) -> str:
    """Lấy chi tiết khách sạn dạng text cho AI"""
    hotel = db_manager.get_hotel_by_id(hotel_id)
    if not hotel:
        return f"Không tìm thấy khách sạn {hotel_id}"
    
    details = [f"=== KHÁCH SẠN: {hotel['name']} ==="]
    details.append(f"Địa chỉ: {hotel.get('address', 'N/A')}, {hotel.get('city', 'N/A')}")
    details.append(f"Đánh giá: {hotel.get('rating', 'Chưa có')} ⭐")
    details.append(f"Mô tả: {hotel.get('description', 'N/A')}")
    details.append(f"Chủ sở hữu: {hotel.get('owner_name', 'N/A')}")
    
    # Tiện nghi
    amenities = db_manager.get_amenities_by_hotel(hotel_id)
    if amenities:
        details.append("\nTiện nghi:")
        for amenity in amenities:
            details.append(f"  - {amenity['name']}")
    
    # Loại phòng
    room_types = db_manager.get_room_types_by_hotel(hotel_id)
    if room_types:
        details.append("\nCác loại phòng:")
        for rt in room_types:
            price = f"{int(rt['price_per_night']):,}đ/đêm" if rt.get('price_per_night') else "Liên hệ"
            details.append(f"  - {rt['name']} ({rt['room_type']}): {price} - Còn {rt['available_rooms']}/{rt['total_rooms']} phòng")
    
    # Đánh giá
    reviews = db_manager.get_reviews_by_hotel(hotel_id)
    if reviews:
        details.append(f"\nĐánh giá gần đây ({len(reviews)} đánh giá):")
        for review in reviews[:5]:
            details.append(f"  - {review['reviewer_name']}: {review['rating']}⭐ - {review.get('comment', '')[:100]}")
    
    return "\n".join(details)


def get_booking_details_for_ai(booking_id: int) -> str:
    """Lấy chi tiết đặt phòng dạng text cho AI"""
    booking = db_manager.get_booking_by_id(booking_id)
    if not booking:
        return f"Không tìm thấy đặt phòng {booking_id}"
    
    details = [f"=== ĐẶT PHÒNG #{booking_id} ==="]
    details.append(f"Khách hàng: {booking.get('guest_name', 'N/A')}")
    details.append(f"Email: {booking.get('guest_email', 'N/A')}")
    details.append(f"Điện thoại: {booking.get('guest_phone', 'N/A')}")
    details.append(f"Khách sạn: {booking.get('hotel_name', 'N/A')} ({booking.get('hotel_city', 'N/A')})")
    details.append(f"Loại phòng: {booking.get('room_type_name', 'N/A')}")
    details.append(f"Check-in: {booking.get('check_in_date')}")
    details.append(f"Check-out: {booking.get('check_out_date')}")
    details.append(f"Số khách: {booking.get('number_of_guests')}")
    details.append(f"Số phòng: {booking.get('number_of_rooms')}")
    details.append(f"Tổng tiền: {int(booking.get('total_price', 0)):,}đ")
    details.append(f"Trạng thái: {booking.get('booking_status')}")
    
    if booking.get('special_requests'):
        details.append(f"Yêu cầu đặc biệt: {booking['special_requests']}")
    
    # Thông tin thanh toán
    payment = db_manager.get_payment_by_booking(booking_id)
    if payment:
        details.append(f"\nThanh toán:")
        details.append(f"  - Phương thức: {payment.get('payment_method')}")
        details.append(f"  - Trạng thái: {payment.get('payment_status')}")
        details.append(f"  - Số tiền: {int(payment.get('amount', 0)):,}đ")
        if payment.get('payment_date'):
            details.append(f"  - Ngày thanh toán: {payment['payment_date']}")
    
    return "\n".join(details)

# Backward compatibility: provide get_invoice_details_for_ai as an alias for booking details
def get_invoice_details_for_ai(invoice_id: int) -> str:
    """Lấy chi tiết hóa đơn dạng text cho AI (tương thích cũ, dùng booking_id)"""
    return get_booking_details_for_ai(invoice_id)
