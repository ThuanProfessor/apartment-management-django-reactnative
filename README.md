
# **Apartment Managements**

Dự án quản lý chung cư bao gồm nhiều nghiệp vụ quan trọng, sử dụng Django Restful để cấu hình API và sử dụng React Native để xây dựng giao diện Mobile App, truy xuất dữ liệu bằng cách gọi các API đã được triển khai lên PythonAnyWhere.
    


##🧩 Main Functionalities
- Quản lý cư dân
- Quản lý căn hộ
- Quản lý hoá đơn
- Quản lý thẻ gửi xe và thân nhân
- Quản lý tủ đồ
- Phản hồi
- Khảo sát
- Thông báo
- Chat realtime
- Xác thực tài khoản thanh toán



## 🛠️Installation

- Đầu tiên, bạn cần clone project về máy local thông qua **🔗HTTPS** hoặc **🔗SSH** :

🔗HTTPS:
```bash
  https://github.com/ThuanProfessor/apartment-management-django-reactnative.git
```
🔗SSH:
```bash
  git@github.com:ThuanProfessor/apartment-management-django-reactnative.git
```

- Tạo môi trường ảo:
```bash
python -m venv thuanvenv
```
- Kích hoạt môi trường ảo:
```bash
thuanvenv\Scripts\activate
```
- Cài đặt các thư viện quan trọng trong file requirements.txt:
```bash
pip install -r requirements.txt
```
- Create Database
*Use the MySQL to create a database named:* **apartment_db**
```bash
CREATE DATABASE xxxx CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```



## 🌐 API Reference

#### 🔐Authentication

Đăng nhập
![POST](https://img.shields.io/badge/-POST-brightgreen)  
```bash 
  POST /api/auth/login/
```
Đăng xuất
![GET](https://img.shields.io/badge/-GET-blue)  
```bash 
  POST /api/auth/logout/
```


Lấy thông tin user hiện tại
![GET](https://img.shields.io/badge/-GET-blue)  
```bash 
  GET /api/auth/showprofile/
```
#### 👤User
Get list user
![GET](https://img.shields.io/badge/-GET-blue)  
```bash 
  GET /api/users/
```
Get current-user
![GET](https://img.shields.io/badge/-GET-blue)  
```bash  
  GET /api/users/current-user/
```
Change-pass
![POST](https://img.shields.io/badge/-POST-brightgreen)  
```bash 
  POST /api/users/change_pass/
```
complete_setup
![POST](https://img.shields.io/badge/-POST-brightgreen)  
```bash 
  POST /api/users/complete_setup/
```
assign_apartment
![PATCH](https://img.shields.io/badge/-PATCH-lightblue)  
```bash 
  PATCH /api/users/{id}/assign_apartment/
```
#### 🏢Apartments
Get list Apartments![GET](https://img.shields.io/badge/-GET-blue)  
```bash 
  GET /api/apartments/
```
Create Apartment
![POST](https://img.shields.io/badge/-POST-brightgreen)  
```bash 
  POST /api/apartments/
```
Update info aparment
![PATCH](https://img.shields.io/badge/-PATCH-lightblue)  
```bash 
  PATCH /api/apartments/{id}/
```
Delete info apartment
![DELETE](https://img.shields.io/badge/-DELETE-red)  
```bash 
  DELETE /api/apartments/{id}/
```
Summary
![GET](https://img.shields.io/badge/-GET-blue)  
```bash 
  GET /api/apartments/{id}/summary/
```
Get list residents in apartments
![GET](https://img.shields.io/badge/-GET-blue)  
```bash 
  GET /api/apartments/{id}/residents/
```





## ✉️Support

Mọi thắt mắc xin vui lòng liên hệ mình thông qua email: beanheo2014@gmail.com


## 🔍Tech Stack

**Backend:** Django REST Framework (DRF)

**Mobile Frontend:** React Native

**Authentication:** Oauth2, Token-based Authentication

**Database:** MySQL


## Badges

Add badges from somewhere like: [shields.io](https://shields.io/)

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)
[![GPLv3 License](https://img.shields.io/badge/License-GPL%20v3-yellow.svg)](https://opensource.org/licenses/)
[![AGPL License](https://img.shields.io/badge/license-AGPL-blue.svg)](http://www.gnu.org/licenses/agpl-3.0)

