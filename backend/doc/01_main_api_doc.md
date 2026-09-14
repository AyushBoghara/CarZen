# CarZen API Documentation

**Project:** CarZen

**Backend:** FastAPI

**Database:** MySQL

**Authentication:** JWT

**API Version:** v1

**Environment:** Local Development

**Base URL:** `http://127.0.0.1:8000`

---

## Table of Contents

1. [API Overview](#1-api-overview)
2. [Health Check](#2-health-check)
3. [Authentication](#3-authentication)
   - [3.1 Register](#31-register-a-new-user)
   - [3.2 Login](#32-login)
   - [3.3 Using the JWT](#33-using-the-jwt)
4. [User Management APIs](#4-user-management-apis)
   - [4.1 Get Current User Profile](#41-get-current-user-profile)
   - [4.2 Update Current User Profile](#42-update-current-user-profile)
   - [4.3 Change Current User Password](#43-change-current-user-password)
   - [4.4 Delete Current User Account](#44-delete-current-user-account)
   - [4.5 Get User by ID](#45-get-user-by-id)
5. [Admin User Management APIs](#5-admin-user-management-apis)
6. [Notes](#6-notes)
7. [API Development Roadmap](#7-api-development-roadmap)

---

## 1. API Overview

Run or Start Backend server Command : **`python run.py`**

| #    | Method | Endpoint                                | Purpose                                  | Status  |
| ---- | ------ | --------------------------------------- | ---------------------------------------- | ------- |
| 1.0  | GET    | `/`                                     | Check API health                         | Working |
| 1.1  | POST   | `/v1/auth/register`                     | Register a new user                      | Working |
| 1.2  | POST   | `/v1/auth/login`                        | Login and generate JWT                   | Working |
| 1.3  | GET    | `/v1/users/me`                          | Get authenticated user's profile         | Working |
| 1.4  | PATCH  | `/v1/users/me`                          | Update authenticated user's profile      | Working |
| 1.5  | POST   | `/v1/users/me/change-password`          | Change authenticated user's password     | Working |
| 1.6  | DELETE | `/v1/users/me`                          | Soft delete authenticated user's account | Working |
| 1.7  | GET    | `/v1/users/{user_id}`                   | Get user by ID (self or admin)           | Working |
| 1.8  | GET    | `/v1/admin/users`                       | List all non-deleted users (admin)       | Working |
| 1.9  | GET    | `/v1/admin/users/{user_id}`             | Get a specific user by ID (admin)        | Working |
| 1.10 | PATCH  | `/v1/admin/users/{user_id}/role-status` | Update a user's role/status (admin)      | Working |
| 1.11 | DELETE | `/v1/admin/users/{user_id}`             | Soft delete a user account (admin)       | Working |

> **Note:** All endpoints below the health check are prefixed with `/v1`. Older sections of this doc referenced paths without the prefix (e.g. `/users/me`) — the correct, working path is `/v1/users/me`.

---

## 2. Health Check

### `GET /`

Checks whether the CarZen backend API is running successfully.

**Response — `200 OK`**

```json
{
  "message": "API is working successfully! For My CarZen"
}
```

---

## 3. Authentication

### 3.1 Register a New User

User: **`POST /v1/auth/register`**

Admin User: **`POST /v1/auth/register-admin`**

Creates a new CarZen user account.

**Headers**

```http
Content-Type: application/json
```

**Request Body**

```json
{
  "first_name": "Ayush",
  "last_name": "Boghara",
  "username": "ayush_test_01",
  "email": "ayush_test_01@gmail.com",
  "password": "123456789",
  "phone_number": "9876543210",
  "role": "user or admin",
  "status": "active",
  "profile_image_url": null
}
```

**Request Parameters**

| Field               | Type           | Required | Description                            |
| ------------------- | -------------- | -------- | -------------------------------------- |
| `first_name`        | string         | Yes      | User's first name                      |
| `last_name`         | string         | Yes      | User's last name                       |
| `username`          | string         | Yes      | Unique username                        |
| `email`             | string         | Yes      | User email address                     |
| `password`          | string         | Yes      | User password                          |
| `phone_number`      | string         | Yes      | User phone number                      |
| `role`              | string         | Yes      | User role, e.g. `user` or `admin` etc. |
| `status`            | string         | Yes      | Account status, e.g. `active`          |
| `profile_image_url` | string \| null | No       | Profile image URL                      |

**Success Response — `201 Created`**

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

**Response Fields**

| Field               | Type             | Description             |
| ------------------- | ---------------- | ----------------------- |
| `id`                | integer          | Unique user ID          |
| `first_name`        | string           | User first name         |
| `last_name`         | string           | User last name          |
| `username`          | string           | Unique username         |
| `email`             | string           | User email              |
| `phone_number`      | string           | User phone number       |
| `role`              | string           | User role               |
| `status`            | string           | Account status          |
| `profile_image_url` | string \| null   | Profile image           |
| `created_at`        | datetime         | Account creation time   |
| `updated_at`        | datetime         | Last update time        |
| `deleted_at`        | datetime \| null | Soft deletion timestamp |

**Possible Errors**

| Case                               | Response                                                                                                           |
| ---------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| User already exists                | `{ "detail": "User already exists" }`                                                                              |
| Password too short (< 8 chars)     | `{ "detail": "Registration Failed: Password is too short. It must be at least 8 characters long." }`               |
| Password missing special character | `{ "detail": "Registration Failed: Password must contain at least one special character (e.g., !, @, #, $, %)." }` |

---

### 3.2 Login

**`POST /v1/auth/login`**

Authenticates an existing CarZen user and generates a JWT access token.

**Headers**

```http
Content-Type: application/json
```

**Request Body**

```json
{
  "username": "ayush_test_01",
  "email": "ayush_test_01@gmail.com",
  "password": "123456789"
}
```

**Request Parameters**

| Field      | Type   | Required | Description         |
| ---------- | ------ | -------- | ------------------- |
| `username` | string | Yes      | Registered username |
| `email`    | string | Yes      | Registered email    |
| `password` | string | Yes      | User password       |

**Success Response — `200 OK`**

```json
{
  "access_token": "<JWT_ACCESS_TOKEN>",
  "token_type": "bearer"
}
```

> ⚠️ The JWT returned by the server is a secret credential. Do not commit it to version control or include it in public documentation.

**Response Fields**

| Field          | Type   | Description                              |
| -------------- | ------ | ---------------------------------------- |
| `access_token` | string | JWT authentication token                 |
| `token_type`   | string | Authentication scheme, normally `bearer` |

**Possible Errors**

| Case                      | Status             | Response                                     |
| ------------------------- | ------------------ | -------------------------------------------- |
| Invalid email or password | `401 Unauthorized` | `{ "detail": "Invalid email or password." }` |

---

### 3.3 Using the JWT

After a successful login, include the access token in the `Authorization` header of every protected request:

```http
Authorization: Bearer <access_token>
```

**Example**

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

The backend validates the JWT and identifies the authenticated user on each request.

---

## 4. User Management APIs

All endpoints in this section require:

```http
Authorization: Bearer <access_token>
```

| Method | Endpoint                       | Description                                                        | Access             |
| ------ | ------------------------------ | ------------------------------------------------------------------ | ------------------ |
| GET    | `/v1/users/me`                 | Returns the authenticated user's profile                           | Authenticated user |
| PATCH  | `/v1/users/me`                 | Updates profile fields (name, username, email, phone, image URL)   | Authenticated user |
| POST   | `/v1/users/me/change-password` | Changes the current user's password after verifying the old one    | Authenticated user |
| DELETE | `/v1/users/me`                 | Soft deletes the current account by marking it inactive            | Authenticated user |
| GET    | `/v1/users/{user_id}`          | Returns a user by ID if the requester is the same user or an admin | Self or admin      |


---

### 4.1 Get Current User Profile

**`GET /v1/users/me`**

Retrieves the profile details of the currently authenticated user based on the JWT access token.

**Headers**

```http
Authorization: Bearer <access_token>
```

**Request Body:** None

**Success Response — `200 OK`**

```json
{
  "id": 1,
  "first_name": "Ayush",
  "last_name": "Boghara",
  "username": "ayush_test_01",
  "email": "ayush_test_01@gmail.com",
  "phone_number": "9876543210",
  "profile_image_url": "https://static.vecteezy.com/vite/assets/photo-masthead-375-BoK_p8LG.webp"
}
```

---

### 4.2 Update Current User Profile

**`PATCH /v1/users/update/me`**

Updates the profile information of the currently authenticated user. Only include the fields that need to be changed.

**Headers**

| Key             | Value                   |
| --------------- | ----------------------- |
| `Authorization` | `Bearer <access_token>` |
| `Content-Type`  | `application/json`      |

**Request Body**

```json
{
  "first_name": "Ayush",
  "last_name": "Boghara",
  "username": "ayush_test_01",
  "email": "ayush_test_01@gmail.com",
  "phone_number": "9876543210",
  "profile_image_url": "https://static.vecteezy.com/vite/assets/photo-masthead-375-BoK_p8LG.webp"
}
```

> **Note:** Only send real values for optional fields, or omit them entirely — do not send placeholder type annotations.

**Success Response — `200 OK`**

```json
{
  "message": "User profile updated successfully"
}
```

---

### 4.3 Change Current User Password

**`POST /v1/users/me/change-password`**

Allows the currently authenticated user to change their password. The existing password must be provided for verification.

**Headers**

| Key             | Value                   |
| --------------- | ----------------------- |
| `Authorization` | `Bearer <access_token>` |
| `Content-Type`  | `application/json`      |

**Request Body**

```json
{
  "current_password": "YourCurrentPassword",
  "new_password": "YourNewSecurePassword"
}
```

**Success Response — `200 OK`**

```json
{
  "message": "Password changed successfully"
}
```

**Possible Errors**

| Case                       | Status             | Response                                         |
| -------------------------- | ------------------ | ------------------------------------------------ |
| Current password incorrect | `400 Bad Request`  | `{ "detail": "Current password is incorrect" }`  |
| Invalid/expired token      | `401 Unauthorized` | `{ "detail": "Could not validate credentials" }` |

---

### 4.4 Delete Current User Account

**`DELETE /v1/users/me`**

Soft deletes the account of the currently authenticated user (marks it inactive via `deleted_at`).

> ⚠️ **Warning:** Depending on the backend implementation, this may permanently affect associated data.

**Headers**

```http
Authorization: Bearer <access_token>
```

**Request Body:** None (unless a confirmation payload is required by your implementation)

**Success Response — `200 OK` or `204 No Content`**

```json
{
  "message": "User account deleted successfully"
}
```

---

### 4.5 Get User by ID

**`GET /v1/users/{user_id}`**\
**`GET /v1/users/1`**

Retrieves information about a specific user by their unique ID. Access depends on the authenticated user's permissions (self or admin).

**Path Parameters**

| Parameter | Type    | Description           |
| --------- | ------- | --------------------- |
| `user_id` | integer | Unique ID of the user |

**Headers**

```http
Authorization: Bearer <access_token>
```

**Request Body:** None

**Possible Responses**

| Status          | Meaning                             | Response                                                         |
| --------------- | ----------------------------------- | ---------------------------------------------------------------- |
| `200 OK`        | User details retrieved successfully | User object                                                      |
| `403 Forbidden` | Requester lacks permission          | `{ "detail": "You do not have permission to access this user" }` |
| `404 Not Found` | User does not exist                 | `{ "detail": "User not found" }`                                 |

---

# 5. Admin User Management APIs

All endpoints in this section require an authenticated user with `role = admin`.

| Method | Endpoint                                | Description                             |
| ------ | --------------------------------------- | --------------------------------------- |
| GET    | `/v1/admin/users`                       | Lists all non-deleted users             |
| GET    | `/v1/admin/users/{user_id}`             | Retrieves a specific user by ID         |
| PATCH  | `/v1/admin/users/{user_id}/role-status` | Updates a user's `role` and/or `status` |
| DELETE | `/v1/admin/users/{user_id}`             | Soft deletes a user account             |
| GET    | `/v1/admin/update/me`          | Updates profile fields (name, username, email, phone, image URL)  | Authenticated user or admin |
---

### 5.1 List All Users

**`GET /v1/admin/users`**

Lists all non-deleted users.

**Headers**

```http
Authorization: Bearer <access_token>
```

**Request Body:** None

**Success Response — `200 OK`**

```json
[
  {
    "id": 1,
    "first_name": "admin",
    "last_name": "admin",
    "username": "admin",
    "email": "admin@gmail.com",
    "phone_number": "1354567890",
    "role": "admin",
    "status": "active",
    "profile_image_url": null,
    "created_at": "2026-08-25T12:49:44",
    "updated_at": "2026-08-25T12:49:44",
    "deleted_at": null
  },
  {
    "id": 3,
    "first_name": "Ayush",
    "last_name": "Boghara",
    "username": "ayush_test_02",
    "email": "ayush_test_02@gmail.com",
    "phone_number": "9876544210",
    "role": "user",
    "status": "active",
    "profile_image_url": null,
    "created_at": "2026-08-25T13:24:10",
    "updated_at": "2026-08-25T13:24:10",
    "deleted_at": null
  },
  {
    "id": 4,
    "first_name": "vishal",
    "last_name": "D",
    "username": "vishal",
    "email": "vishal@gmail.com",
    "phone_number": "7876544210",
    "role": "user",
    "status": "active",
    "profile_image_url": null,
    "created_at": "2026-08-25T13:25:34",
    "updated_at": "2026-08-25T13:25:34",
    "deleted_at": null
  },
  {
    "id": 5,
    "first_name": "pinak",
    "last_name": "sakariya",
    "username": "pinak",
    "email": "pinak@gmail.com",
    "phone_number": "7896544210",
    "role": "user",
    "status": "active",
    "profile_image_url": null,
    "created_at": "2026-08-25T13:26:28",
    "updated_at": "2026-08-25T13:26:28",
    "deleted_at": null
  }
]
```

Returns an array of user objects. Each object follows the same shape described in [Section 3.1](#31-register-a-new-user).

---

### 5.2 Get User by ID (Admin)

**`GET /v1/admin/users/{user_id}`**

Retrieves a specific user by ID.

**Path Parameters**

| Parameter | Type    | Description           |
| --------- | ------- | --------------------- |
| `user_id` | integer | Unique ID of the user |

**Headers**

```http
Authorization: Bearer <access_token>
```

**Request Body:** None

**Success Response — `200 OK`**

```json
{
  "id": 5,
  "first_name": "pinak",
  "last_name": "sakariya",
  "username": "pinak",
  "email": "pinak@gmail.com",
  "phone_number": "7896544210",
  "role": "user",
  "status": "active",
  "profile_image_url": null,
  "created_at": "2026-08-25T13:26:28",
  "updated_at": "2026-08-25T13:26:28",
  "deleted_at": null
}
```

**Possible Errors**

| Case           | Response                          |
| -------------- | --------------------------------- |
| User not found | `{ "detail": "User not found." }` |

---

### 5.3 Update User Role & Status

**`PATCH /v1/admin/users/{user_id}/role-status`**

Updates a user's `role` and/or `status`.

**Path Parameters**

| Parameter | Type    | Description           |
| --------- | ------- | --------------------- |
| `user_id` | integer | Unique ID of the user |

**Headers**

| Key             | Value                   |
| --------------- | ----------------------- |
| `Authorization` | `Bearer <access_token>` |
| `Content-Type`  | `application/json`      |

**Request Body**

```json
{
  "role": "seller",
  "status": "active"
}
```

**Success Response — `200 OK`**

```json
{
  "id": 5,
  "first_name": "pinak",
  "last_name": "sakariya",
  "username": "pinak",
  "email": "pinak@gmail.com",
  "phone_number": "7896544210",
  "role": "user",
  "status": "active",
  "profile_image_url": null,
  "created_at": "2026-08-25T13:26:28",
  "updated_at": "2026-08-25T13:26:28",
  "deleted_at": null
}
```

Returns the updated user object reflecting the new `role` and/or `status`.

---

### 5.4 Delete User (Admin)

**`DELETE /v1/admin/users/{user_id}`**

Soft deletes a user account.

**Path Parameters**

| Parameter | Type    | Description           |
| --------- | ------- | --------------------- |
| `user_id` | integer | Unique ID of the user |

**Headers**

```http
Authorization: Bearer <access_token>
```

**Request Body:** None

**Success Response — `200 OK`**

```json
{
  "message": "User account deleted successfully."
}
```

### 5.5 Update Admin Profile

**`PATCH /v1/admin/update/me`**

Updates a admin's all Information.

**Path Parameters**

| Parameter           | Type   | Description                       |
| ------------------- | ------ | --------------------------------- |
| `first_name`        | string | edit the first name               |
| `last_name`         | string | edit the last name                |
| `username`          | string | edit the username                 |
| `email`             | string | Unique email id                   |
| `phone_number`      | string | Unique number                     |
| `profile_image_url` | string | Unique image for user's and admin |

**Headers**

| Key             | Value                   |
| --------------- | ----------------------- |
| `Authorization` | `Bearer <access_token>` |
| `Content-Type`  | `application/json`      |

**Request Body**

```json
{
  "first_name": "admin",
  "last_name": "admin",
  "username": "admin",
  "email": "admin1@gmail.com",
  "phone_number": "9856320147",
  "profile_image_url": "https://static.vecteezy.com/vite/assets/photo-masthead-375-BoK_p8LG.webp"
}
```

**Success Response — `200 OK`**

```json
{
  "id": 1,
  "first_name": "admin",
  "last_name": "admin",
  "username": "admin",
  "email": "admin1@gmail.com",
  "phone_number": "9856320147",
  "role": "admin",
  "status": "active",
  "profile_image_url": "https://static.vecteezy.com/vite/assets/photo-masthead-375-BoK_p8LG.webp",
  "created_at": "2026-08-25T12:49:44",
  "updated_at": "2026-08-25T13:56:48",
  "deleted_at": null
}
```

---

## 6. Notes

- Public registration cannot create admin accounts.
- Public registration always creates active accounts.
- Deleted users are soft deleted using the `deleted_at` field.
- Inactive, blocked, or deleted users cannot use protected APIs.

---

## 7. API Development Roadmap

Recommended backend development order:

1. Authentication
2. User management and Admin
3. Car management
4. Car image upload
5. Car search and filtering
6. Favorites
7. Seller management
8. Buyer management
9. Orders
10. Payments
11. Notifications
12. API security and rate limiting
13. Production deployment
