# CarZen API Documentation

## 1. API Overview

**Base URL**

`http://127.0.0.1:8000`

**API Version**

`v1`

### Current Endpoints

| Method | Endpoint | Purpose | Status |
|---|---|---|---|
| GET | `/` | Check API health | Working |
| POST | `/v1/auth/register` | Register a new user | Working |
| POST | `/v1/auth/login` | Login and generate JWT | Working |


## 2. API Health Check

### Endpoint

`GET /`

### URL

`http://127.0.0.1:8000/`

### Description

Checks whether the CarZen backend API is running successfully.

### Response

```json
{
    "message": "API is working successfully! For My CarZen"
}
```

### Status Code

`200 OK`

# 3. User Registration API

### Endpoint

`POST /v1/auth/register`

### URL

`http://127.0.0.1:8000/v1/auth/register`

### Description

Creates a new SmartCarX user account.

### Request Headers

```http
Content-Type: application/json
```

### Request Body

```json
{
    "first_name": "Ayush",
    "last_name": "Boghara",
    "username": "ayush_test_01",
    "email": "ayush_test_01@gmail.com",
    "password": "123456789",
    "phone_number": "9876543210",
    "role": "user",
    "status": "active",
    "profile_image_url": null
}
```

### Request Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `first_name` | string | Yes | User's first name |
| `last_name` | string | Yes | User's last name |
| `username` | string | Yes | Unique username |
| `email` | string | Yes | User email address |
| `password` | string | Yes | User password |
| `phone_number` | string | Yes | User phone number |
| `role` | string | Yes | User role, e.g. `user` |
| `status` | string | Yes | Account status, e.g. `active` |
| `profile_image_url` | string/null | No | Profile image URL |

### Successful Response

```json
{
    "id": 1,
    "first_name": "Ayush",
    "last_name": "Boghara",
    "username": "ayush_test_01",
    "email": "ayush_test_01@gmail.com",
    "phone_number": "9876543210",
    "role": "user",
    "status": "active",
    "profile_image_url": null,
    "created_at": "2026-08-20T16:49:50",
    "updated_at": "2026-08-20T16:49:50",
    "deleted_at": null
}
```

### Response Fields

| Field | Type | Description |
|---|---|---|
| `id` | integer | Unique user ID |
| `first_name` | string | User first name |
| `last_name` | string | User last name |
| `username` | string | Unique username |
| `email` | string | User email |
| `phone_number` | string | User phone number |
| `role` | string | User role |
| `status` | string | Account status |
| `profile_image_url` | string/null | Profile image |
| `created_at` | datetime | Account creation time |
| `updated_at` | datetime | Last update time |
| `deleted_at` | datetime/null | Soft deletion timestamp |

### Possible Errors

#### User Already Exists

```json
{
    "detail": "User already exists"
}
```
#### Password is too short. It must be at least 8 characters long.
```json
{
    "detail": "Registration Failed: Password is too short. It must be at least 8 characters long."
}
```
#### special character error
```json
{
    "detail": "Registration Failed: Password must contain at least one special character (e.g., !, @, #, $, %)."
}
```

# 4. User Login API

### Endpoint

`POST /v1/auth/login`

### URL

`http://127.0.0.1:8000/v1/auth/login`

### Description

Authenticates an existing TrueCar user and generates a JWT access token.

### Request Headers

```http
Content-Type: application/json
```

### Request Body

```json
{
    "username": "ayush_test_01",
    "email": "ayush_test_01@gmail.com",
    "password": "123456789"
}
```

### Request Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `username` | string | Yes | Registered username |
| `email` | string | Yes | Registered email |
| `password` | string | Yes | User password |

### Successful Response

```json
{
    "access_token": "<JWT_ACCESS_TOKEN>",
    "token_type": "bearer"
}
```

> The actual JWT returned by the server should be treated as a secret credential. Do not commit it to Git or include it in public documentation.

### Response Fields

| Field | Type | Description |
|---|---|---|
| `access_token` | string | JWT authentication token |
| `token_type` | string | Authentication scheme, normally `bearer` |

### Status Code

`200 OK`

### Possible Errors

#### Invalid email or password.(401 error)

```json
{
    "detail": "Invalid email or password."
}
```
# 5. JWT Authentication

After successful login, the client receives an access token.

For protected APIs, send the token in the request header:

```http
Authorization: Bearer <access_token>
```

### Example

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

The backend can validate the JWT and identify the authenticated user.

# 6. API Development Roadmap

The recommended TrueCar backend development order is:

1. Authentication
2. User management
3. Car management
4. Car image upload
5. Car search and filtering
6. Favorites
7. Seller management
8. Buyer management
9. Orders
10. Payments
11. Notifications
12. Admin APIs
13. API security and rate limiting
14. Production deployment


## Project Information

**Project:** CarZen  
**Backend:** FastAPI  
**Database:** MySQL  
**Authentication:** JWT  
**API Version:** v1  
**Environment:** Local Development  
**Base URL:** `http://127.0.0.1:8000`

