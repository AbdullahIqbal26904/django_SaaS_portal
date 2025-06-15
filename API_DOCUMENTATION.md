# API Documentation for Next.js Integration

This document outlines the API endpoints available for integration with your Next.js frontend.

> **Note**: See [RESELLER_API_DOCUMENTATION.md](./RESELLER_API_DOCUMENTATION.md) for detailed documentation on the reseller/partner layer functionality.

## Authentication Endpoints

### Login
- **URL:** `/api/users/auth/login/`
- **Method:** `POST`
- **Body:**
  ```json
  {
    "email": "user@example.com",
    "password": "securepassword"
  }
  ```
- **Response:**
  ```json
  {
    "user": {
      "user_id": 1,
      "email": "user@example.com",
      "full_name": "User Name",
      "is_root_admin": false,
      "is_reseller_admin": false,
      "is_department_admin": true,
      "user_type": "direct",
      "mfa_enabled": false,
      "created_at": "2025-05-30T00:00:00Z"
    },
    "tokens": {
      "refresh": "refresh_token_value",
      "access": "access_token_value"
    },
    "admin_departments": [
      {
        "department_id": 1,
        "name": "Marketing",
        "description": "Marketing department",
        "created_at": "2025-05-30T00:00:00Z",
        "updated_at": "2025-05-30T00:00:00Z",
        "admins": [...],
        "users": [...]
      }
    ]
  }
  ```
  > **Note**: The `admin_departments` field is only included when the user is a department admin

### Register
- **URL:** `/api/users/auth/register/`
- **Method:** `POST`
- **Body for Direct Customer Registration:**
  ```json
  {
    "email": "newuser@example.com",
    "full_name": "New User",
    "password": "securepassword"
  }
  ```
- **Body for Reseller Customer Registration (requires authentication):**
  ```json
  {
    "email": "customer@example.com",
    "full_name": "Reseller Customer",
    "password": "securepassword",
    "reseller_id": 1,
    "department_name": "Customer Department" // Optional, defaults to user's name + Department
  }
  ```
- **Response:** Same as login with additional department info for reseller registrations

### Refresh Token
- **URL:** `/api/token/refresh/`
- **Method:** `POST`
- **Body:**
  ```json
  {
    "refresh": "refresh_token_value"
  }
  ```
- **Response:**
  ```json
  {
    "access": "new_access_token_value"
  }
  ```

## User Endpoints

### Get User Profile
- **URL:** `/api/users/profile/`
- **Method:** `GET`
- **Auth Required:** Yes
- **Response:**
  ```json
  {
    "user_id": 1,
    "email": "user@example.com",
    "full_name": "User Name",
    "is_root_admin": false,
    "mfa_enabled": false,
    "created_at": "2025-05-30T00:00:00Z"
  }
  ```

### List All Users (Root Admin Only)
- **URL:** `/api/users/users/`
- **Method:** `GET`
- **Auth Required:** Yes (Root Admin only)
- **Response:**
  ```json
  [
    {
      "user_id": 1,
      "email": "user@example.com",
      "full_name": "User Name",
      "is_root_admin": false,
      "is_reseller_admin": false,
      "is_department_admin": true,
      "mfa_enabled": false,
      "created_at": "2025-05-30T00:00:00Z",
      "user_type": "direct"
    }
  ]
  ```

### Get User Detail
- **URL:** `/api/users/users/{id}/`
- **Method:** `GET`
- **Auth Required:** Yes (Root Admin only or self)
- **Response:**
  ```json
  {
    "user_id": 1,
    "email": "user@example.com",
    "full_name": "User Name",
    "is_root_admin": false,
    "is_reseller_admin": false,
    "is_department_admin": true,
    "mfa_enabled": false,
    "created_at": "2025-05-30T00:00:00Z",
    "user_type": "direct",
    "departments": [
      {
        "department_id": 1,
        "name": "Marketing",
        "description": "Marketing department",
        "created_at": "2025-05-30T00:00:00Z",
        "updated_at": "2025-05-30T00:00:00Z"
      }
    ]
  }
  ```

### Update User
- **URL:** `/api/users/users/{id}/`
- **Method:** `PUT`
- **Auth Required:** Yes (Root Admin only or self)
- **Body:**
  ```json
  {
    "full_name": "Updated Name",
    "email": "updated@example.com"
  }
  ```
- **Response:** Same as get user detail

### Delete User
- **URL:** `/api/users/users/{id}/`
- **Method:** `DELETE`
- **Auth Required:** Yes (Root Admin only)
- **Response:** Status 204 No Content

## Department Endpoints

### List Departments
- **URL:** `/api/departments/departments/`
- **Method:** `GET`
- **Auth Required:** Yes
- **Access:** All authenticated users (including normal users)
- **Response:**
  ```json
  [
    {
      "department_id": 1,
      "name": "Marketing",
      "description": "Marketing department",
      "created_at": "2025-05-30T00:00:00Z",
      "updated_at": "2025-05-30T00:00:00Z"
    }
  ]
  ```

### Create Department
- **URL:** `/api/departments/departments/`
- **Method:** `POST`
- **Auth Required:** Yes
- **Body:**
  ```json
  {
    "name": "Sales",
    "description": "Sales department"
  }
  ```
- **Response:**
  ```json
  {
    "department_id": 2,
    "name": "Sales",
    "description": "Sales department",
    "created_at": "2025-05-30T00:00:00Z",
    "updated_at": "2025-05-30T00:00:00Z"
  }
  ```

### Get Department Detail
- **URL:** `/api/departments/departments/{id}/`
- **Method:** `GET`
- **Auth Required:** Yes
- **Access:** All authenticated users (including normal users)
- **Response:**
  ```json
  {
    "department_id": 1,
    "name": "Marketing",
    "description": "Marketing department",
    "created_at": "2025-05-30T00:00:00Z",
    "updated_at": "2025-05-30T00:00:00Z",
    "admins": [
      {
        "user_id": 1,
        "email": "admin@example.com",
        "full_name": "Admin User",
        "is_root_admin": false,
        "mfa_enabled": false,
        "created_at": "2025-05-30T00:00:00Z"
      }
    ],
    "users": [
      {
        "user_id": 2,
        "email": "user@example.com",
        "full_name": "Regular User",
        "is_root_admin": false,
        "mfa_enabled": false,
        "created_at": "2025-05-30T00:00:00Z"
      }
    ]
  }
  ```

### Update Department
- **URL:** `/api/departments/departments/{id}/`
- **Method:** `PUT`
- **Auth Required:** Yes (Root Admin or Department Admin)
- **Body:**
  ```json
  {
    "name": "Updated Marketing",
    "description": "Updated marketing department description"
  }
  ```
- **Response:**
  ```json
  {
    "department_id": 1,
    "name": "Updated Marketing",
    "description": "Updated marketing department description",
    "created_at": "2025-05-30T00:00:00Z",
    "updated_at": "2025-06-15T00:00:00Z"
  }
  ```

### Delete Department
- **URL:** `/api/departments/departments/{id}/`
- **Method:** `DELETE`
- **Auth Required:** Yes (Root Admin only)
- **Response:** Status 204 No Content

### Get Current Admin Departments
- **URL:** `/api/departments/me/admin/`
- **Method:** `GET`
- **Auth Required:** Yes (Department Admin)
- **Response:**
  ```json
  [
    {
      "department_id": 1,
      "name": "Marketing",
      "description": "Marketing department",
      "created_at": "2025-05-30T00:00:00Z",
      "updated_at": "2025-05-30T00:00:00Z",
      "admins": [ /* List of admin users */ ],
      "users": [ /* List of regular users */ ]
    }
  ]
  ```

## Department Admin Management (Updated)

### Add Department Admin
- **URL:** `/api/departments/departments/{department_id}/admins/`
- **Method:** `POST`
- **Auth Required:** Yes (Root Admin only)
- **Body:**
  ```json
  {
    "email": "newadmin@example.com",
    "full_name": "New Admin",
    "password": "securepassword"  // Optional if user already exists
  }
  ```
- **Response:**
  ```json
  {
    "id": 1,
    "user": 3,
    "department": 1,
    "assigned_at": "2025-05-30T00:00:00Z",
    "user_details": {
      "user_id": 3,
      "email": "newadmin@example.com",
      "full_name": "New Admin",
      "is_root_admin": false,
      "mfa_enabled": false,
      "created_at": "2025-05-30T00:00:00Z"
    },
    "department_details": {
      "department_id": 1,
      "name": "Marketing",
      "description": "Marketing department",
      "created_at": "2025-05-30T00:00:00Z",
      "updated_at": "2025-05-30T00:00:00Z"
    }
  }
  ```

### Remove Department Admin
- **URL:** `/api/departments/departments/{department_id}/admins/`
- **Method:** `DELETE`
- **Auth Required:** Yes (Root Admin only)
- **Body:**
  ```json
  {
    "email": "admin@example.com"
  }
  ```
- **Response:** Status 204 No Content

## Department User Management (Updated)

### Add User to Department
- **URL:** `/api/departments/departments/{department_id}/users/`
- **Method:** `POST`
- **Auth Required:** Yes (Department Admin or Root Admin)
- **Body:**
  ```json
  {
    "email": "newuser@example.com",
    "full_name": "New User",
    "password": "securepassword"  // Optional if user already exists
  }
  ```
- **Response:**
  ```json
  {
    "id": 1,
    "user": 4,
    "department": 1,
    "user_details": {
      "user_id": 4,
      "email": "newuser@example.com",
      "full_name": "New User",
      "is_root_admin": false,
      "mfa_enabled": false,
      "created_at": "2025-05-30T00:00:00Z"
    },
    "department_details": {
      "department_id": 1,
      "name": "Marketing",
      "description": "Marketing department",
      "created_at": "2025-05-30T00:00:00Z",
      "updated_at": "2025-05-30T00:00:00Z"
    }
  }
  ```

### Remove User from Department
- **URL:** `/api/departments/departments/{department_id}/users/`
- **Method:** `DELETE`
- **Auth Required:** Yes (Department Admin or Root Admin)
- **Body:**
  ```json
  {
    "email": "user@example.com"
  }
  ```
- **Response:** Status 204 No Content

## Service Package Endpoints

### List Service Packages
- **URL:** `/api/services/packages/`
- **Method:** `GET`
- **Auth Required:** Yes
- **Query Parameters:**
  - `active_only=true` (optional, defaults to true)
- **Response:**
  ```json
  [
    {
      "id": 1,
      "name": "Basic Plan",
      "description": "Basic service package",
      "price": "9.99",
      "billing_cycle": "monthly",
      "features": {
        "feature1": true,
        "feature2": false
      },
      "is_active": true,
      "created_at": "2025-05-30T00:00:00Z",
      "updated_at": "2025-05-30T00:00:00Z"
    }
  ]
  ```

### Get Service Package Detail
- **URL:** `/api/services/packages/{id}/`
- **Method:** `GET`
- **Auth Required:** Yes
- **Response:**
  ```json
  {
    "id": 1,
    "name": "Basic Plan",
    "description": "Basic service package",
    "price": "9.99",
    "billing_cycle": "monthly",
    "features": {
      "feature1": true,
      "feature2": false
    },
    "is_active": true,
    "created_at": "2025-05-30T00:00:00Z",
    "updated_at": "2025-05-30T00:00:00Z"
  }
  ```

## Subscription Endpoints

### Create Subscription
- **URL:** `/api/services/subscribe/`
- **Method:** `POST`
- **Auth Required:** Yes
- **Body:**
  ```json
  {
    "department": 1,
    "service_package": 1
  }
  ```
- **Response:**
  ```json
  {
    "id": 1,
    "department": 1,
    "service_package": 1,
    "status": "active",
    "start_date": "2025-05-30",
    "end_date": "2025-06-30",
    "created_at": "2025-05-30T00:00:00Z",
    "updated_at": "2025-05-30T00:00:00Z",
    "department_details": {
      "department_id": 1,
      "name": "Marketing",
      "description": "Marketing department",
      "created_at": "2025-05-30T00:00:00Z",
      "updated_at": "2025-05-30T00:00:00Z"
    },
    "service_package_details": {
      "id": 1,
      "name": "Basic Plan",
      "description": "Basic service package",
      "price": "9.99",
      "billing_cycle": "monthly",
      "features": {
        "feature1": true,
        "feature2": false
      },
      "is_active": true,
      "created_at": "2025-05-30T00:00:00Z",
      "updated_at": "2025-05-30T00:00:00Z"
    }
  }
  ```

### List Subscriptions
- **URL:** `/api/services/subscriptions/`
- **Method:** `GET`
- **Auth Required:** Yes
- **Response:**
  ```json
  [
    {
      "id": 1,
      "department": 1,
      "service_package": 1,
      "status": "active",
      "start_date": "2025-05-30",
      "end_date": "2025-06-30",
      "created_at": "2025-05-30T00:00:00Z",
      "updated_at": "2025-05-30T00:00:00Z",
      "department_details": {
        "department_id": 1,
        "name": "Marketing",
        "description": "Marketing department",
        "created_at": "2025-05-30T00:00:00Z",
        "updated_at": "2025-05-30T00:00:00Z"
      },
      "service_package_details": {
        "id": 1,
        "name": "Basic Plan",
        "description": "Basic service package",
        "price": "9.99",
        "billing_cycle": "monthly",
        "features": {
          "feature1": true,
          "feature2": false
        },
        "is_active": true,
        "created_at": "2025-05-30T00:00:00Z",
        "updated_at": "2025-05-30T00:00:00Z"
      }
    }
  ]
  ```

### Get Subscription Detail
- **URL:** `/api/services/subscriptions/{id}/`
- **Method:** `GET`
- **Auth Required:** Yes
- **Response:**
  ```json
  {
    "id": 1,
    "department": 1,
    "service_package": 1,
    "status": "active",
    "start_date": "2025-05-30",
    "end_date": "2025-06-30",
    "created_at": "2025-05-30T00:00:00Z",
    "updated_at": "2025-05-30T00:00:00Z",
    "department_details": { /* Department details */ },
    "service_package_details": { /* Service package details */ },
    "users": [
      {
        "user_id": 4,
        "email": "user@example.com",
        "full_name": "Regular User",
        "is_root_admin": false,
        "mfa_enabled": false,
        "created_at": "2025-05-30T00:00:00Z"
      }
    ]
  }
  ```

### Cancel Subscription
- **URL:** `/api/services/subscriptions/{id}/`
- **Method:** `DELETE`
- **Auth Required:** Yes (Department Admin or Root Admin)
- **Response:** Status 204 No Content

## Service Access Endpoints

### Grant Service Access to User
- **URL:** `/api/services/subscription-users/{subscription_id}/`
- **Method:** `POST`
- **Auth Required:** Yes
- **Body:**
  ```json
  {
    "user_id": 4
  }
  ```
- **Response:**
  ```json
  {
    "id": 1,
    "user": 4,
    "subscription": 1,
    "service_package": 1,
    "granted_at": "2025-05-30T00:00:00Z",
    "user_details": {
      "user_id": 4,
      "email": "user@example.com",
      "full_name": "Regular User",
      "is_root_admin": false,
      "mfa_enabled": false,
      "created_at": "2025-05-30T00:00:00Z"
    },
    "subscription_details": { /* Subscription details */ },
    "service_package_details": { /* Service package details */ }
  }
  ```

## Using these APIs in Next.js

To use these APIs in your Next.js project:

1. Set up authentication handling to store JWT tokens
2. Create API client functions to interact with these endpoints
3. Use the client functions in your React components

Example API client setup:

```javascript
// api/client.js
import axios from 'axios';

const API_URL = 'http://localhost:8000/api';

// Create axios instance
const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Add authentication interceptor
apiClient.interceptors.request.use(config => {
  const token = localStorage.getItem('accessToken');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Add token refresh interceptor
apiClient.interceptors.response.use(
  response => response,
  async error => {
    const originalRequest = error.config;
    
    if (error.response.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        const refreshToken = localStorage.getItem('refreshToken');
        const response = await axios.post(`${API_URL}/token/refresh/`, {
          refresh: refreshToken
        });
        
        localStorage.setItem('accessToken', response.data.access);
        
        // Retry the original request with new token
        originalRequest.headers.Authorization = `Bearer ${response.data.access}`;
        return apiClient(originalRequest);
      } catch (err) {
        // Refresh token expired or invalid, redirect to login
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        window.location.href = '/login';
        return Promise.reject(err);
      }
    }
    
    return Promise.reject(error);
  }
);

export default apiClient;
```

Example API endpoints:

```javascript
// api/departments.js
import apiClient from './client';

export const getDepartments = () => {
  return apiClient.get('/departments/departments/');
};

export const createDepartment = (data) => {
  return apiClient.post('/departments/departments/', data);
};

export const addDepartmentAdmin = (departmentId, data) => {
  return apiClient.post(`/departments/departments/${departmentId}/admins/`, data);
};

export const addDepartmentUser = (departmentId, data) => {
  return apiClient.post(`/departments/departments/${departmentId}/users/`, data);
};

// Add more API functions as needed
```

Example usage in a component:

```jsx
import { useState, useEffect } from 'react';
import { getDepartments, addDepartmentAdmin } from '../api/departments';

export default function DepartmentsPage() {
  const [departments, setDepartments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  useEffect(() => {
    const fetchDepartments = async () => {
      try {
        const response = await getDepartments();
        setDepartments(response.data);
        setLoading(false);
      } catch (err) {
        setError(err.message);
        setLoading(false);
      }
    };
    
    fetchDepartments();
  }, []);
  
  // Add admin handler
  const handleAddAdmin = async (departmentId, adminData) => {
    try {
      const response = await addDepartmentAdmin(departmentId, adminData);
      // Handle successful admin creation
    } catch (err) {
      // Handle error
    }
  };
  
  // Component JSX...
}
```
