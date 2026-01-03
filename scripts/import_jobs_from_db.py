"""
Script import dữ liệu công việc thực tế từ database vào vector DB
Kết nối với database MySQL/PostgreSQL và nạp tất cả công việc vào ChromaDB
"""

import sys
import re
from pathlib import Path

# Thêm thư mục gốc vào path để import được services và config
sys.path.append(str(Path(__file__).parent.parent))

from services.vector_service import add_job_to_vector, check_job_exists, get_all_job_ids
from config import get_settings

# Lấy cấu hình database từ Settings
settings = get_settings()
DB_CONFIG = {
    'host': settings.db_host,
    'port': settings.db_port,
    'database': settings.db_name,
    'user': settings.db_user,
    'password': settings.db_password
}

# File lưu danh sách job bị lỗi
FAILED_JOBS_FILE = Path(__file__).parent / "failed_jobs.txt"


def clean_html(html_text):
    """Loại bỏ HTML tags và giữ lại text thuần"""
    if not html_text:
        return ""
    clean = re.sub(r'<[^>]+>', '', html_text)
    clean = re.sub(r'\s+', ' ', clean).strip()
    return clean


def save_failed_job(job_id: str):
    """Lưu id job bị lỗi vào file"""
    with open(FAILED_JOBS_FILE, "a", encoding="utf-8") as f:
        f.write(f"{job_id}\n")


def get_failed_job_ids():
    """Lấy danh sách id các job bị lỗi từ file"""
    if not FAILED_JOBS_FILE.exists():
        return set()
    with open(FAILED_JOBS_FILE, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f if line.strip())


def clear_failed_jobs_file():
    """Xóa file lưu job bị lỗi sau khi re-import thành công"""
    if FAILED_JOBS_FILE.exists():
        FAILED_JOBS_FILE.unlink()


def import_jobs_from_mysql(reimport_mode=False):
    """
    Import công việc từ MySQL database
    
    Args:
        reimport_mode: Nếu True, chỉ import các job chưa có trong vector DB
    """
    try:
        import pymysql
        
        print("=" * 60)
        print("🔌 KẾT NỐI VỚI DATABASE MYSQL")
        print("=" * 60)
        
        # Kết nối database
        connection = pymysql.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database=DB_CONFIG['database'],
            cursorclass=pymysql.cursors.DictCursor
        )
        
        # Lấy danh sách id đã có trong vector DB
        existing_ids = get_all_job_ids()
        print(f"📊 Vector DB hiện có {len(existing_ids)} công việc")
        
        with connection.cursor() as cursor:
            # Lấy tất cả công việc active
            sql = """
                SELECT id, name, description, location, salary, level, job_type, 
                       years_of_experience, end_date, start_date, work_mode
                FROM jobs
                WHERE active = 1
                ORDER BY id
            """
            cursor.execute(sql)
            jobs = cursor.fetchall()
            
            print(f"📊 Tìm thấy {len(jobs)} công việc trong database")
            
            if reimport_mode:
                print("🔄 Chế độ: Chỉ import các job chưa có trong vector DB")
            
            print("=" * 60)
            print("🚀 BẮT ĐẦU IMPORT VÀO VECTOR DATABASE")
            print("=" * 60)
            
            success_count = 0
            error_count = 0
            skipped_count = 0
            
            for job in jobs:
                try:
                    job_id = str(job.get('id', ''))
                    
                    # Nếu ở chế độ re-import, bỏ qua job đã tồn tại
                    if reimport_mode and job_id in existing_ids:
                        skipped_count += 1
                        print(f"⏭️  [{job_id}] Đã tồn tại, bỏ qua")
                        continue
                    
                    name = job.get('name', '')
                    description = clean_html(job.get('description', '')) or "Không có mô tả"
                    location = job.get('location', '')
                    salary = f"{job.get('salary', ''):,}đ" if job.get('salary') else "Thỏa thuận"
                    level = job.get('level', '')
                    job_type = job.get('job_type', '')
                    years_of_experience = job.get('years_of_experience', '')
                    end_date = job.get('end_date', '')
                    start_date = job.get('start_date', '')
                    work_mode = job.get('work_mode', '')
                    
                    # Tạo text đầy đủ cho vector DB
                    text = (
                        f"{name} tại {location}. {description}. "
                        f"Mức lương: {salary}. Cấp bậc: {level}. Loại công việc: {job_type}. "
                        f"Kinh nghiệm: {years_of_experience}. "
                        f"Bắt đầu: {start_date}, Kết thúc: {end_date}. "
                        f"Hình thức làm việc: {work_mode}."
                    )
                    
                    # Thêm vào vector DB
                    add_job_to_vector(job_id, text)
                    print(f"✅ [{job_id}] {name}")
                    success_count += 1
                    
                except Exception as e:
                    print(f"❌ Lỗi khi import job {job.get('id', 'unknown')}: {e}")
                    error_count += 1
                    # Lưu job bị lỗi vào file
                    save_failed_job(str(job.get('id', '')))
            
            print("=" * 60)
            print(f"🎉 HOÀN TẤT!")
            print(f"   ✅ Thành công: {success_count}")
            if reimport_mode:
                print(f"   ⏭️  Đã bỏ qua: {skipped_count}")
            print(f"   ❌ Lỗi: {error_count}")
            print("=" * 60)
            
            if error_count > 0:
                print(f"💾 Đã lưu {error_count} job bị lỗi vào file: {FAILED_JOBS_FILE}")
                print("💡 Bạn có thể chạy lại với lựa chọn '3' để re-import các job bị lỗi")
        
        connection.close()
        
    except ImportError:
        print("❌ Chưa cài đặt pymysql. Chạy: pip install pymysql")
    except Exception as e:
        print(f"❌ Lỗi kết nối database: {e}")
        print("💡 Kiểm tra lại DB_CONFIG trong script")


def reimport_failed_jobs_mysql():
    """Re-import các job bị lỗi từ lần import trước"""
    try:
        import pymysql
        
        # Kiểm tra file failed_jobs.txt
        failed_ids = get_failed_job_ids()
        if not failed_ids:
            print("=" * 60)
            print("✅ Không có job bị lỗi cần re-import!")
            print("=" * 60)
            return
        
        print("=" * 60)
        print(f"🔄 RE-IMPORT {len(failed_ids)} JOB BỊ LỖI")
        print("=" * 60)
        print(f"📋 Danh sách job cần re-import: {', '.join(sorted(failed_ids))}")
        print("=" * 60)
        
        # Lấy danh sách id đã có trong vector DB
        existing_ids = get_all_job_ids()
        print(f"📊 Vector DB hiện có {len(existing_ids)} công việc")
        
        # Kết nối database
        connection = pymysql.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database=DB_CONFIG['database'],
            cursorclass=pymysql.cursors.DictCursor
        )
        
        with connection.cursor() as cursor:
            success_count = 0
            error_count = 0
            skipped_count = 0
            
            for job_id in failed_ids:
                try:
                    # Kiểm tra xem job đã có trong vector DB chưa
                    if job_id in existing_ids:
                        print(f"⏭️  [{job_id}] Đã tồn tại trong vector DB, bỏ qua")
                        skipped_count += 1
                        continue
                    
                    # Lấy thông tin job từ database
                    sql = """
                        SELECT id, name, description, location, salary, level, job_type,
                               years_of_experience, end_date, start_date, work_mode
                        FROM jobs
                        WHERE id = %s AND active = 1
                    """
                    cursor.execute(sql, (job_id,))
                    job = cursor.fetchone()
                    
                    if not job:
                        print(f"⚠️  [{job_id}] Không tìm thấy trong database hoặc đã bị xóa")
                        continue
                    
                    name = job.get('name', '')
                    description = clean_html(job.get('description', '')) or "Không có mô tả"
                    location = job.get('location', '')
                    salary = f"{job.get('salary', ''):,}đ" if job.get('salary') else "Thỏa thuận"
                    level = job.get('level', '')
                    job_type = job.get('job_type', '')
                    years_of_experience = job.get('years_of_experience', '')
                    end_date = job.get('end_date', '')
                    start_date = job.get('start_date', '')
                    work_mode = job.get('work_mode', '')
                    
                    # Tạo text đầy đủ cho vector DB
                    text = (
                        f"{name} tại {location}. {description}. "
                        f"Mức lương: {salary}. Cấp bậc: {level}. Loại công việc: {job_type}. "
                        f"Kinh nghiệm: {years_of_experience}. "
                        f"Bắt đầu: {start_date}, Kết thúc: {end_date}. "
                        f"Hình thức làm việc: {work_mode}."
                    )
                    
                    # Thêm vào vector DB
                    add_job_to_vector(job_id, text)
                    print(f"✅ [{job_id}] {name}")
                    success_count += 1
                    
                except Exception as e:
                    print(f"❌ Lỗi khi re-import job {job_id}: {e}")
                    error_count += 1
            
            print("=" * 60)
            print(f"🎉 HOÀN TẤT RE-IMPORT!")
            print(f"   ✅ Thành công: {success_count}")
            print(f"   ⏭️  Đã bỏ qua: {skipped_count}")
            print(f"   ❌ Vẫn lỗi: {error_count}")
            print("=" * 60)
            
            if error_count == 0 and success_count > 0:
                # Xóa file failed_jobs.txt nếu tất cả đều thành công
                clear_failed_jobs_file()
                print("🗑️  Đã xóa file failed_jobs.txt")
            elif error_count > 0:
                print("💡 Vẫn còn job bị lỗi. Hãy kiểm tra kết nối mạng và thử lại sau.")
        
        connection.close()
        
    except ImportError:
        print("❌ Chưa cài đặt pymysql. Chạy: pip install pymysql")
    except Exception as e:
        print(f"❌ Lỗi: {e}")


if __name__ == "__main__":
    print("=" * 60)
    print("📦 IMPORT JOBS VÀO VECTOR DATABASE")
    print("=" * 60)
    print("Chọn chức năng:")
    print("1. Import tất cả jobs từ MySQL (có thể trùng)")
    print("2. Import chỉ các jobs chưa có trong vector DB (MySQL)")
    print("3. Re-import các jobs bị lỗi lần trước (MySQL)")
    print("=" * 60)
    
    choice = input("Nhập lựa chọn (1, 2 hoặc 3): ").strip()
    
    if choice == "1":
        import_jobs_from_mysql(reimport_mode=False)
    elif choice == "2":
        import_jobs_from_mysql(reimport_mode=True)
    elif choice == "3":
        reimport_failed_jobs_mysql()
    else:
        print("❌ Lựa chọn không hợp lệ!")