# 🌍 Travel Uzbekistan API

A comprehensive backend platform built with Django REST Framework for
travelers exploring Uzbekistan.

This system allows users to: - Discover tourist destinations (Places) -
Share travel experiences (Community) - Communicate via a modern chat
system with reactions and media support

------------------------------------------------------------------------

# 🚀 Core Features

## 🔐 JWT Authentication

Secure login and registration using JSON Web Tokens (JWT).

## 🌍 Regional Registration Lock

User registration is restricted to IP addresses located in Uzbekistan.

## 📧 Email Verification (OTP)

-   4-digit verification code
-   Sent via Gmail SMTP
-   Used for account activation
-   Used for password recovery
-   OTP expires after 5 minutes

## 💬 Advanced Chat System

-   Text messaging
-   Multiple image attachments
-   Emoji reactions
-   Threaded replies (parent-child message support)
-   Media upload support

## 📝 Community Posts

-   Create posts with multiple images
-   Like / Unlike posts
-   Comment system
-   Post tagging
-   Search & filtering

## 🏢 Destinations & Ratings

-   Travel location catalog
-   Category support
-   Search filters
-   Ordering system
-   User rating & review system
-   Multiple image uploads per rating

## 🔔 Notification System

Tracks user-specific activities such as: - Post likes - Post comments -
Unread notifications counter - Mark single/all as read

------------------------------------------------------------------------

# 🛠 Tech Stack

  Layer              Technology
  ------------------ ------------------------------------------------
  Backend            Python 3.11+
  Framework          Django 5.0+
  API                Django REST Framework
  Database           PostgreSQL (Production) / SQLite (Development)
  Authentication     djangorestframework-simplejwt
  Documentation      Swagger / OpenAPI 3.0 (drf-spectacular)
  Background Tasks   Python threading
  Security           django-cors-headers

------------------------------------------------------------------------

# ⚙️ Installation & Setup

## 1️⃣ Clone the Repository

git clone https://github.com/yourusername/travel_project.git cd
travel_project

## 2️⃣ Create Virtual Environment

python -m venv venv

### Activate Environment

Windows: venv`\Scripts`{=tex}`\activate`{=tex}

Linux / Mac: source venv/bin/activate

pip install -r requirements.txt

## 3️⃣ Configure Environment Variables (.env)

Create a `.env` file in the project root:

# Django Core

SECRET_KEY=django-insecure-xxxxxxxxxxxxxxxxxxxxxxxx DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

# Email SMTP Settings

EMAIL_HOST=smtp.gmail.com EMAIL_PORT=587 EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

⚠️ Never expose real credentials in public repositories.

## 4️⃣ Database Migrations

python manage.py makemigrations python manage.py migrate python
manage.py createsuperuser

## 5️⃣ Run Development Server

python manage.py runserver

Server will run at: http://127.0.0.1:8000/

------------------------------------------------------------------------

# 📖 API Documentation

Swagger UI: http://127.0.0.1:8000/swagger/

------------------------------------------------------------------------

# 📁 Project Modules

  Module             Description
  ------------------ ---------------------------------------------------------
  app_auth           Handles JWT authentication, login, password reset logic
  app_user           User profiles, community posts, likes, IP verification
  app_chat           Messaging system, media attachments, emoji reactions
  app_place          Tourist locations, categories, and user ratings
  app_notification   User activity notifications system
  app_stat           Admin panel statistics

------------------------------------------------------------------------

# 🔒 Security Highlights

-   JWT-based authentication
-   OTP expiration (5 minutes)
-   IP-based registration restriction
-   Role-based permissions
-   Protected endpoints
-   CORS configuration
-   Password hashing using Django's secure system

------------------------------------------------------------------------

# 🚀 Production Deployment Notes

-   Set DEBUG=False
-   Use PostgreSQL
-   Use Gunicorn + Nginx
-   Configure HTTPS (SSL)
-   Store secrets securely
-   Use Redis for caching
-   Consider replacing threading with Celery

------------------------------------------------------------------------

# 👨‍💻 Author

Saidakbar Nematov

------------------------------------------------------------------------

A scalable, secure, and production-ready backend architecture for modern
travel & social platforms 🚀
