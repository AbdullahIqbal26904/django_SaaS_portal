# SaaS Portal with Django and Oscar eCommerce

A multi-tenant SaaS portal for managing departments, users, and service packages with subscription-based access.

## Features

- **User Management**:
  - Root admin, department admin, and regular user roles
  - Authentication via email/password and OAuth (Google)
  - MFA support
  
- **Department Management**:
  - Create and manage departments
  - Assign department admins
  - Add/remove users from departments
  
- **Service Packages**:
  - Define service packages with pricing and features
  - Different billing cycles (monthly, quarterly, yearly)
  
- **Subscription Management**:
  - Subscribe departments to service packages
  - Track subscription status and expiration
  - Control user access to services
  
- **Payment Tracking**:
  - Record payment transactions
  - Track payment status

## Getting Started

### Prerequisites

- Python 3.8+
- PostgreSQL

### Installation

1. Clone the repository
2. Create a virtual environment:
   ```
   python3 -m venv .venv
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Create a `.env` file in the project root with the following variables:
   ```
   SECRET_KEY=your_secret_key
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1

   # Database Configuration
   DB_NAME=saas_portal
   DB_USER=your_db_user
   DB_PASSWORD=your_db_password
   DB_HOST=your_db_host
   DB_PORT=5432
   ```
5. Configure database settings in `myproject/settings.py`
6. Run migrations:
   ```
   python manage.py migrate
   ```
7. Create a superuser:
   ```
   python manage.py createsuperuser
   ```
8. Run the development server:
   ```
   python manage.py runserver
   ```

## Testing

You can test the application with the following credentials:

- Root Admin:
  - Email: admin@example.com
  - Password: admin123

- Test User:
  - Email: test@example.com
  - Password: password123

## Project Structure

- **user**: Custom user model and authentication
- **department**: Department management
- **service_package**: Service packages and subscriptions
