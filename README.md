<h1 align="center">🏢 Apartment Managements</h1>

<p align="center">
  <img src="https://img.shields.io/badge/Backend-Django%20Rest%20Framework-blue" />
  <img src="https://img.shields.io/badge/Frontend-React%20Native-lightblue" />
  <img src="https://img.shields.io/badge/Database-MySQL-yellowgreen" />
  <img src="https://img.shields.io/badge/Auth-OAuth2%20%7C%20Token-red" />
</p>

<p align="center">✨ A full-stack apartment management system featuring resident and apartment handling, billing, feedback, surveys, and real-time chat. ✨</p>

---

## 🔧 Features

- 👥 Resident Management  
- 🏠 Apartment Management  
- 📄 Invoice & Billing  
- 🚗 Vehicle & Relative Card Management  
- 📦 Locker Management  
- 💬 Realtime Chat  
- 📢 Announcement System  
- 📊 Survey Handling  
- 🔒 Payment Account Authentication  

---

## 🚀 Installation Guide

### 📁 Clone the Project

🔗 HTTPS:
```bash
git clone https://github.com/ThuanProfessor/apartment-management-django-reactnative.git
🔗 SSH:

bash
Copy
Edit
git clone git@github.com:ThuanProfessor/apartment-management-django-reactnative.git
🐍 Virtual Environment
bash
Copy
Edit
python -m venv thuanvenv
thuanvenv\Scripts\activate
pip install -r requirements.txt
🛠️ MySQL Database Setup
sql
Copy
Edit
CREATE DATABASE apartment_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
🌐 API Reference
🔐 Authentication

Method	Endpoint	Description
POST	/api/auth/login/	Đăng nhập
POST	/api/auth/logout/	Đăng xuất
GET	/api/auth/showprofile/	Lấy thông tin user
👤 User

Method	Endpoint	Description
GET	/api/users/	Lấy danh sách user
GET	/api/users/current-user/	User hiện tại
POST	/api/users/change_pass/	Đổi mật khẩu
POST	/api/users/complete_setup/	Hoàn tất cài đặt
PATCH	/api/users/{id}/assign_apartment/	Gán căn hộ cho user
🏢 Apartments

Method	Endpoint	Description
GET	/api/apartments/	Lấy danh sách căn hộ
POST	/api/apartments/	Tạo mới căn hộ
PATCH	/api/apartments/{id}/	Cập nhật thông tin căn hộ
DELETE	/api/apartments/{id}/	Xoá căn hộ
GET	/api/apartments/{id}/summary/	Tổng quan căn hộ
GET	/api/apartments/{id}/residents/	Cư dân trong căn hộ
🧰 Tech Stack
Backend: Django REST Framework

Mobile App: React Native

Authentication: OAuth2, Token-based

Database: MySQL

📬 Contact Me
<p align="center"> <a href="mailto:beanheo2014@gmail.com"> <img src="https://img.shields.io/badge/Email-beanheo2014@gmail.com-D14836?style=flat-square&logo=gmail&logoColor=white"/> </a> <a href="https://www.linkedin.com/in/hoang-thuan-nguyen-87a538248/"> <img src="https://img.shields.io/badge/LinkedIn-Hoang%20Thuan%20Nguyen-0077B5?style=flat-square&logo=linkedin&logoColor=white"/> </a> <a href="https://www.facebook.com/thuan.nguyenhoang.161/"> <img src="https://img.shields.io/badge/Facebook-Thuan%20Nguyen-1877F2?style=flat-square&logo=facebook&logoColor=white"/> </a> </p>
📌 License




🙌 Support
Nếu bạn có thắc mắc, hãy liên hệ qua email: beanheo2014@gmail.com
