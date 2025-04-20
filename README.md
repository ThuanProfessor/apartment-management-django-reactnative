To redesign the README for the **Apartment Management** project, I'll create a visually appealing, professional, and well-structured version that enhances readability and engagement. The new design will feature a clean layout, modern typography, consistent color-coded badges, and a polished presentation of the project's functionalities, installation steps, and API references. It will maintain all essential content while making it more intuitive and aesthetically pleasing, optimized for GitHub's markdown rendering.


# <h1 align="center">🏢 Apartment Management System</h1>

<p align="center">
  A comprehensive solution for managing apartments, built with <strong>Django REST Framework</strong> for robust APIs and <strong>React Native</strong> for a seamless mobile experience. Deployed on PythonAnywhere for reliable data access.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="MIT License" />
  <img src="https://img.shields.io/badge/License-GPL%20v3-yellow.svg" alt="GPLv3 License" />
  <img src="https://img.shields.io/badge/License-AGPL-blue.svg" alt="AGPL License" />
</p>

---

## 🌟 **Overview**

The **Apartment Management System** streamlines residential operations through a powerful backend and intuitive mobile app. Key features include resident management, billing, real-time chat, and more, all accessible via secure APIs.

### 🧩 **Core Features**
- **Resident Management**: Track and manage resident information.
- **Apartment Management**: Handle apartment details and assignments.
- **Billing**: Generate and manage invoices.
- **Parking & Dependents**: Manage parking cards and dependent records.
- **Locker Management**: Organize locker assignments.
- **Feedback & Surveys**: Collect resident input.
- **Notifications**: Send real-time updates.
- **Real-Time Chat**: Enable instant communication.
- **Payment Verification**: Secure account authentication.

---

## 🛠️ **Installation**

Follow these steps to set up the project locally.

### 1. Clone the Repository
Use **HTTPS** or **SSH**:
```bash
# HTTPS
git clone https://github.com/ThuanProfessor/apartment-management-django-reactnative.git

# SSH
git clone git@github.com:ThuanProfessor/apartment-management-django-reactnative.git
```

### 2. Set Up Virtual Environment
```bash
python -m venv thuanvenv
```

### 3. Activate Virtual Environment
```bash
# Windows
thuanvenv\Scripts\activate

# macOS/Linux
source thuanvenv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Create Database
Set up a MySQL database named `apartment_db`:
```sql
CREATE DATABASE apartment_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 6. Run Migrations
```bash
python manage.py migrate
```

### 7. Start the Server
```bash
python manage.py runserver
```

---

## 🌐 **API Reference**

The API is built with **Django REST Framework** and supports secure, token-based authentication. Below are key endpoints.

### 🔐 **Authentication**
| Method | Endpoint                     | Description               |
|--------|------------------------------|---------------------------|
| <span style="color:green">POST</span>   | `/api/auth/login/`          | Authenticate user         |
| <span style="color:blue">GET</span>     | `/api/auth/logout/`         | Log out user              |
| <span style="color:blue">GET</span>     | `/api/auth/showprofile/`    | Get current user profile  |

### 👤 **Users**
| Method | Endpoint                             | Description                     |
|--------|--------------------------------------|---------------------------------|
| <span style="color:blue">GET</span>     | `/api/users/`                       | List all users                 |
| <span style="color:blue">GET</span>     | `/api/users/current-user/`          | Get current user details       |
| <span style="color:green">POST</span>   | `/api/users/change_pass/`           | Change user password           |
| <span style="color:green">POST</span>   | `/api/users/complete_setup/`        | Complete user setup            |
| <span style="color:cyan">PATCH</span>   | `/api/users/{id}/assign_apartment/` | Assign apartment to user       |

### 🏢 **Apartments**
| Method | Endpoint                             | Description                          |
|--------|--------------------------------------|--------------------------------------|
| <span style="color:blue">GET</span>     | `/api/apartments/`                  | List all apartments                 |
| <span style="color:green">POST</span>   | `/api/apartments/`                  | Create a new apartment              |
| <span style="color:cyan">PATCH</span>   | `/api/apartments/{id}/`             | Update apartment details            |
| <span style="color:red">DELETE</span>   | `/api/apartments/{id}/`             | Delete an apartment                 |
| <span style="color:blue">GET</span>     | `/api/apartments/{id}/summary/`     | Get apartment summary               |
| <span style="color:blue">GET</span>     | `/api/apartments/{id}/residents/`   | List residents in an apartment      |

---

## 🔍 **Tech Stack**

- **Backend**: Django REST Framework
- **Frontend**: React Native
- **Database**: MySQL
- **Authentication**: OAuth2, Token-based
- **Hosting**: PythonAnywhere

---

## ✉️ **Support**

For questions or issues, reach out via email:  
📧 [beanheo2014@gmail.com](mailto:beanheo2014@gmail.com)

---

## 📜 **Licenses**

<p align="center">
  <a href="https://choosealicense.com/licenses/mit/"><img src="https://img.shields.io/badge/License-MIT-green.svg" alt="MIT License" /></a>
  <a href="https://opensource.org/licenses/"><img src="https://img.shields.io/badge/License-GPL%20v3-yellow.svg" alt="GPLv3 License" /></a>
  <a href="http://www.gnu.org/licenses/agpl-3.0"><img src="https://img.shields.io/badge/License-AGPL-blue.svg" alt="AGPL License" /></a>
</p>

---

<p align="center">
  Built with 💻 and ☕ by <a href="https://github.com/ThuanProfessor">ThuanProfessor</a>
</p>
