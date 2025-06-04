# Reseller/Partner Layer API Documentation

## Overview
This document outlines the API endpoints for the reseller/partner layer functionality. This layer allows resellers/partners to sign up customers under their account, with separate billing and management.

## Authentication
All API endpoints require authentication with a JWT token, which should be included in the Authorization header as `Bearer <token>`.

## Reseller Management Endpoints

### List Resellers
- **URL:** `/api/resellers/resellers/`
- **Method:** `GET`
- **Auth Required:** Yes
- **Access:** Root admins see all resellers, reseller admins see only their own resellers
- **Response:**
  ```json
  [
    {
      "reseller_id": 1,
      "name": "Partner Company LLC",
      "description": "Technology solutions partner",
      "is_active": true,
      "commission_rate": "15.00",
      "created_at": "2025-06-01T10:00:00Z",
      "updated_at": "2025-06-01T10:00:00Z"
    }
  ]
  ```

### Create Reseller
- **URL:** `/api/resellers/resellers/`
- **Method:** `POST`
- **Auth Required:** Yes
- **Access:** Root admins only
- **Body:**
  ```json
  {
    "name": "New Partner Inc",
    "description": "Cloud solutions partner",
    "is_active": true,
    "commission_rate": "10.00"
  }
  ```
- **Response:**
  ```json
  {
    "reseller_id": 2,
    "name": "New Partner Inc",
    "description": "Cloud solutions partner",
    "is_active": true,
    "commission_rate": "10.00",
    "created_at": "2025-06-05T15:30:00Z",
    "updated_at": "2025-06-05T15:30:00Z"
  }
  ```

### Get Reseller Details
- **URL:** `/api/resellers/resellers/{reseller_id}/`
- **Method:** `GET`
- **Auth Required:** Yes
- **Access:** Root admins and admins of the specific reseller
- **Response:**
  ```json
  {
    "reseller_id": 1,
    "name": "Partner Company LLC",
    "description": "Technology solutions partner",
    "is_active": true,
    "commission_rate": "15.00",
    "created_at": "2025-06-01T10:00:00Z",
    "updated_at": "2025-06-01T10:00:00Z",
    "admins": [
      {
        "user_id": 5,
        "email": "partner_admin@example.com",
        "full_name": "Partner Admin",
        "is_root_admin": false,
        "is_reseller_admin": true,
        "user_type": "reseller",
        "mfa_enabled": false,
        "created_at": "2025-06-01T10:00:00Z"
      }
    ],
    "customers": [
      {
        "department_id": 3,
        "name": "Customer Company",
        "description": "Reseller customer",
        "created_at": "2025-06-02T14:30:00Z",
        "updated_at": "2025-06-02T14:30:00Z"
      }
    ]
  }
  ```

### Add Reseller Admin
- **URL:** `/api/resellers/resellers/{reseller_id}/admins/`
- **Method:** `POST`
- **Auth Required:** Yes
- **Access:** Root admins only
- **Body:**
  ```json
  {
    "email": "new_admin@partner.com",
    "full_name": "New Partner Admin",
    "password": "securepassword"  // Only required if creating a new user
  }
  ```
- **Response:**
  ```json
  {
    "id": 2,
    "user": 7,
    "reseller": 1,
    "assigned_at": "2025-06-05T16:00:00Z",
    "user_details": {
      "user_id": 7,
      "email": "new_admin@partner.com",
      "full_name": "New Partner Admin",
      "is_root_admin": false,
      "is_reseller_admin": true,
      "user_type": "reseller",
      "mfa_enabled": false,
      "created_at": "2025-06-05T16:00:00Z"
    },
    "reseller_details": {
      "reseller_id": 1,
      "name": "Partner Company LLC",
      "description": "Technology solutions partner",
      "is_active": true,
      "commission_rate": "15.00",
      "created_at": "2025-06-01T10:00:00Z",
      "updated_at": "2025-06-01T10:00:00Z"
    }
  }
  ```

### Remove Reseller Admin
- **URL:** `/api/resellers/resellers/{reseller_id}/admins/`
- **Method:** `DELETE`
- **Auth Required:** Yes
- **Access:** Root admins only
- **Body:**
  ```json
  {
    "email": "admin_to_remove@partner.com"
  }
  ```
- **Response:** `204 No Content`

## Reseller Customer Management

### List Reseller Customers
- **URL:** `/api/resellers/resellers/{reseller_id}/customers/`
- **Method:** `GET`
- **Auth Required:** Yes
- **Access:** Root admins and admins of the specific reseller
- **Response:**
  ```json
  [
    {
      "id": 1,
      "reseller": 1,
      "department": 3,
      "is_active": true,
      "created_at": "2025-06-02T14:30:00Z",
      "department_details": {
        "department_id": 3,
        "name": "Customer Company",
        "description": "Reseller customer",
        "created_at": "2025-06-02T14:30:00Z",
        "updated_at": "2025-06-02T14:30:00Z"
      },
      "reseller_details": {
        "reseller_id": 1,
        "name": "Partner Company LLC",
        "description": "Technology solutions partner",
        "is_active": true,
        "commission_rate": "15.00",
        "created_at": "2025-06-01T10:00:00Z",
        "updated_at": "2025-06-01T10:00:00Z"
      }
    }
  ]
  ```

### Create Reseller Customer
- **URL:** `/api/resellers/resellers/{reseller_id}/customers/`
- **Method:** `POST`
- **Auth Required:** Yes
- **Access:** Root admins and admins of the specific reseller
- **Body:**
  ```json
  {
    "name": "New Customer Ltd",
    "description": "New client for our reseller"
  }
  ```
- **Response:**
  ```json
  {
    "id": 2,
    "reseller": 1,
    "department": 4,
    "is_active": true,
    "created_at": "2025-06-05T16:15:00Z",
    "department_details": {
      "department_id": 4,
      "name": "New Customer Ltd",
      "description": "New client for our reseller",
      "created_at": "2025-06-05T16:15:00Z",
      "updated_at": "2025-06-05T16:15:00Z"
    },
    "reseller_details": {
      "reseller_id": 1,
      "name": "Partner Company LLC",
      "description": "Technology solutions partner",
      "is_active": true,
      "commission_rate": "15.00",
      "created_at": "2025-06-01T10:00:00Z",
      "updated_at": "2025-06-01T10:00:00Z"
    }
  }
  ```

### Remove Reseller Customer
- **URL:** `/api/resellers/resellers/{reseller_id}/customers/{customer_id}/`
- **Method:** `DELETE`
- **Auth Required:** Yes
- **Access:** Root admins and admins of the specific reseller
- **Response:** `204 No Content`

## Reseller Subscription Management

### Create Subscription for Reseller Customer
- **URL:** `/api/resellers/resellers/{reseller_id}/subscriptions/`
- **Method:** `POST`
- **Auth Required:** Yes
- **Access:** Root admins and admins of the specific reseller
- **Body:**
  ```json
  {
    "department": 4,
    "service_package": 2
  }
  ```
- **Response:**
  ```json
  {
    "id": 3,
    "department": 4,
    "service_package": 2,
    "status": "active",
    "start_date": "2025-06-05",
    "end_date": "2025-07-05",
    "subscription_source": "reseller",
    "reseller": 1,
    "created_at": "2025-06-05T16:30:00Z",
    "updated_at": "2025-06-05T16:30:00Z",
    "department_details": {
      "department_id": 4,
      "name": "New Customer Ltd",
      "description": "New client for our reseller",
      "created_at": "2025-06-05T16:15:00Z",
      "updated_at": "2025-06-05T16:15:00Z"
    },
    "service_package_details": {
      "id": 2,
      "name": "Premium Package",
      "description": "Premium service offering",
      "price": "199.99",
      "billing_cycle": "monthly",
      "features": {
        "feature1": true,
        "feature2": true,
        "premium_support": true
      },
      "is_active": true
    },
    "reseller_details": {
      "reseller_id": 1,
      "name": "Partner Company LLC",
      "description": "Technology solutions partner",
      "is_active": true,
      "commission_rate": "15.00"
    }
  }
  ```
