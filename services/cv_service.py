"""
CV Service - Xử lý đọc và phân tích CV PDF
"""
import PyPDF2
import re
from typing import Dict, List, Optional
from io import BytesIO


class CVService:
    """Service xử lý CV PDF"""
    
    def __init__(self):
        pass
    
    def extract_text_from_pdf(self, pdf_file: bytes) -> str:
        """
        Trích xuất text từ file PDF
        
        Args:
            pdf_file: Nội dung file PDF dạng bytes
            
        Returns:
            str: Text đã trích xuất từ PDF
        """
        try:
            pdf_reader = PyPDF2.PdfReader(BytesIO(pdf_file))
            text = ""
            
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            
            print(f"**********📄 Đã trích xuất {text}")
            return text.strip()
        except Exception as e:
            raise Exception(f"Lỗi khi đọc PDF: {str(e)}")
    
    def extract_email(self, text: str) -> Optional[str]:
        """Trích xuất email từ text"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        print(f"**********📧 Tìm thấy email: {emails}")
        return emails[0] if emails else None
    
    def extract_phone(self, text: str) -> Optional[str]:
        """Trích xuất số điện thoại từ text"""
        phone_patterns = [
            r'\+?\d{1,3}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}',
            r'\d{10,11}',
            r'\(\d{3}\)\s*\d{3}[-.\s]?\d{4}'
        ]
        
        for pattern in phone_patterns:
            phones = re.findall(pattern, text)
            if phones:
                print(f"**********📞 Tìm thấy số điện thoại: {phones}" )
                return phones[0]
        return None
    
    def extract_skills(self, text: str) -> List[str]:
        """
        Trích xuất các kỹ năng từ CV
        Tìm kiếm các từ khóa phổ biến trong lĩnh vực công nghệ
        """
        # Danh sách kỹ năng phổ biến (có thể mở rộng)
        common_skills = [
            # Programming Languages
            'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'php', 'ruby', 'go', 'rust',
            'swift', 'kotlin', 'scala', 'r', 'matlab',
            
            # Web Technologies
            'html', 'css', 'react', 'angular', 'vue', 'nodejs', 'express', 'django', 'flask',
            'spring', 'fastapi', 'nextjs', 'nuxt',
            
            # Databases
            'mysql', 'postgresql', 'mongodb', 'redis', 'oracle', 'sql server', 'sqlite',
            'dynamodb', 'cassandra', 'elasticsearch',
            
            # Cloud & DevOps
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'gitlab', 'github',
            'terraform', 'ansible', 'ci/cd', 'devops',
            
            # Mobile
            'android', 'ios', 'react native', 'flutter', 'xamarin',
            
            # Data & AI
            'machine learning', 'deep learning', 'data science', 'ai', 'nlp', 'computer vision',
            'tensorflow', 'pytorch', 'keras', 'pandas', 'numpy', 'scikit-learn',
            
            # Other
            'git', 'agile', 'scrum', 'rest api', 'graphql', 'microservices', 'linux',
            'testing', 'junit', 'selenium', 'jest'
        ]
        
        text_lower = text.lower()
        found_skills = []
        
        for skill in common_skills:
            if skill.lower() in text_lower:
                found_skills.append(skill.title())
        print(f"**********🛠️ Tìm thấy kỹ năng: {found_skills}")
        # Loại bỏ trùng lặp và giữ nguyên thứ tự
        return list(dict.fromkeys(found_skills))
    
    def extract_experience_years(self, text: str) -> Optional[int]:
        """
        Trích xuất số năm kinh nghiệm từ CV
        Tìm các pattern như: "5 years", "3+ years", "2-3 years"
        """
        patterns = [
            r'(\d+)\+?\s*(?:years?|năm)',
            r'(\d+)-\d+\s*(?:years?|năm)',
        ]
        print(f"**********⏳ Tìm thấy số năm kinh nghiệm với các pattern: {patterns}")
        for pattern in patterns:
            matches = re.findall(pattern, text.lower())
            if matches:
                try:
                    return int(matches[0])
                except:
                    pass
        return None
    
    def analyze_cv(self, pdf_file: bytes) -> Dict:
        """
        Phân tích toàn bộ CV và trả về thông tin có cấu trúc
        
        Args:
            pdf_file: Nội dung file PDF dạng bytes
            
        Returns:
            Dict chứa thông tin đã phân tích
        """
        try:
            # Trích xuất text từ PDF
            text = self.extract_text_from_pdf(pdf_file)
            
            if not text or len(text) < 50:
                raise Exception("CV quá ngắn hoặc không đọc được nội dung")
            
            # Phân tích các thông tin
            email = self.extract_email(text)
            phone = self.extract_phone(text)
            skills = self.extract_skills(text)
            experience_years = self.extract_experience_years(text)
            
            return {
                "success": True,
                "full_text": text,
                "email": email,
                "phone": phone,
                "skills": skills,
                "experience_years": experience_years,
                "text_length": len(text)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def create_job_search_query(self, cv_analysis: Dict) -> str:
        """
        Tạo query tìm kiếm công việc dựa trên phân tích CV
        
        Args:
            cv_analysis: Kết quả phân tích CV từ analyze_cv()
            
        Returns:
            str: Query string để tìm kiếm trong vector DB
        """
        if not cv_analysis.get("success"):
            return ""
        
        query_parts = []
        
        # Thêm kỹ năng vào query
        skills = cv_analysis.get("skills", [])
        if skills:
            # Chọn tối đa 10 kỹ năng quan trọng nhất
            top_skills = skills[:10]
            query_parts.append(f"Kỹ năng: {', '.join(top_skills)}")
        
        # Thêm kinh nghiệm
        exp_years = cv_analysis.get("experience_years")
        if exp_years:
            if exp_years < 2:
                query_parts.append("Junior, fresher, entry level")
            elif exp_years < 5:
                query_parts.append("Middle, intermediate level")
            else:
                query_parts.append("Senior, expert level")
        
        # Tạo query string
        if query_parts:
            return ". ".join(query_parts)
        else:
            # Fallback: sử dụng một phần text từ CV
            full_text = cv_analysis.get("full_text", "")
            return full_text[:500] if full_text else "Tìm việc làm"


# Singleton instance
_cv_service = None

def get_cv_service() -> CVService:
    """Lấy singleton instance của CVService"""
    global _cv_service
    if _cv_service is None:
        _cv_service = CVService()
    return _cv_service
