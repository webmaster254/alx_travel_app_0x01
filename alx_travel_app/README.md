# ALX Travel App

A comprehensive travel accommodation booking platform built with Django and Django REST framework.

## Features

### Core Features

- User authentication and authorization
- Property listings with detailed information
- Booking management system
- Review and rating system
- Search and filter functionality
- Admin dashboard for property management

### Technical Stack

- **Backend**: Django 4.2.10
- **API**: Django REST Framework
- **Database**: MySQL
- **Task Queue**: Celery with RabbitMQ
- **API Documentation**: Swagger/OpenAPI (drf-yasg)
- **CORS**: django-cors-headers
- **Environment Management**: django-environ

## Project Structure

```plaintext
alx_travel_app/
├── alx_travel_app/          # Main project directory
│   ├── settings.py         # Django settings
│   ├── urls.py            # Main URL configuration
│   ├── asgi.py            # ASGI config
│   └── wsgi.py            # WSGI config
└── listings/              # Listings app
    ├── migrations/        # Database migrations
    ├── management/        # Management commands
    ├── models.py          # Data models
    ├── serializers.py     # API serializers
    ├── admin.py          # Admin interface
    ├── apps.py           # App config
    ├── urls.py           # App URL configuration
    └── views.py          # API views
```

## Getting Started

### Prerequisites

