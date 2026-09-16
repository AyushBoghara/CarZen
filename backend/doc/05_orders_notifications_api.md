# Orders & Notifications API 

### Authentication

Most endpoints require an authenticated user.

```http
Authorization: Bearer <access_token>
```

Admin endpoints require an authenticated admin user.


# 1. Notifications API

Notifications allow users to view, filter, read, and delete their notifications.

## Notification Response

```json
{
  "id": 1,
  "title": "Order Accepted",
  "message": "Your order has been accepted by the seller.",
  "notification_type": "ORDER",
  "reference_id": 10,
  "reference_type": "order",
  "is_read": false,
  "created_at": "2026-09-16T10:30:00"
}
```

### Fields

| Field | Type | Description |
|---|---|---|
| `id` | integer | Notification ID |
| `title` | string | Notification title |
| `message` | string | Notification message |
| `notification_type` | enum/null | Type of notification |
| `reference_id` | integer/null | Related entity ID |
| `reference_type` | string/null | Related entity type |
| `is_read` | boolean | Whether notification has been read |
| `created_at` | datetime/null | Creation date and time |


## 1.1 Get Notifications

### Endpoint

```http
GET /notifications
```

### Authentication

Required.

### Query Parameters

| Parameter | Type | Required | Default | Description |
|---|---|---:|---:|---|
| `page` | integer | No | `1` | Page number |
| `limit` | integer | No | `20` | Records per page; maximum `100` |

### Example

```http
GET /notifications?page=1&limit=20
```

### Response

```json
{
  "data": [
    {
      "id": 1,
      "title": "Order Accepted",
      "message": "Your order has been accepted by the seller.",
      "notification_type": "ORDER",
      "reference_id": 10,
      "reference_type": "order",
      "is_read": false,
      "created_at": "2026-09-16T10:30:00"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 1
  }
}
```

## 1.2 Get Unread Notifications

### Endpoint

```http
GET /notifications/unread
```

### Authentication

Required.

### Query Parameters

```text
page
limit
```

### Example

```http
GET /notifications/unread?page=1&limit=20
```

### Purpose

Returns only unread notifications.

---

## 1.3 Mark Notification as Read

### Endpoint

```http
PATCH /notifications/{notification_id}/read
```

### Authentication

Required.

### Path Parameter

| Parameter | Type | Description |
|---|---|---|
| `notification_id` | integer | Notification ID |

### Example

```http
PATCH /notifications/10/read
```

### Request Body

None.

### Response

Returns the updated `NotificationResponse`.

---

## 1.4 Mark All Notifications as Read

### Endpoint

```http
PATCH /notifications/read-all
```

### Authentication

Required.

### Request Body

None.

### Example

```http
PATCH /notifications/read-all
```

### Response

```json
{
  "message": "Marked 5 notifications as read."
}
```

---

## 1.5 Delete Notification

### Endpoint

```http
DELETE /notifications/{notification_id}
```

### Authentication

Required.

### Example

```http
DELETE /notifications/10
```

### Response

```json
{
  "message": "Notification deleted successfully."
}
```

# 2. Orders API

The Orders API handles the order lifecycle between buyers and sellers.

Supported operations:

- Create order
- View order
- View buyer orders
- Cancel buyer order
- View seller orders
- Accept order
- Reject order
- Update seller order status
- Admin order management

---

# 3. Order Request Schemas

## 3.1 OrderCreate

Used when creating an order with the listing ID in the URL.

```json
{
  "amount": 500000,
  "notes": "I am interested in purchasing this car."
}
```

### Fields

| Field | Type | Required | Validation |
|---|---|---:|---|
| `amount` | Decimal | Yes | Must be greater than `0` |
| `notes` | string/null | No | Maximum 5000 characters |

---

## 3.2 OrderCreateRequest

Used when the listing ID is included in the request body.

```json
{
  "listing_id": 10,
  "amount": 500000,
  "notes": "I would like to inspect the car."
}
```

### Fields

| Field | Type | Required | Validation |
|---|---|---:|---|
| `listing_id` | integer | Yes | Must be greater than `0` |
| `amount` | Decimal | Yes | Must be greater than `0` |
| `notes` | string/null | No | Maximum 5000 characters |

---

## 3.3 OrderStatusUpdate

Used to update an order status.

```json
{
  "status": "ACCEPTED"
}
```

> The available values depend on the project's `OrderStatus` enum.

---

# 4. Order Response

The `OrderResponse` contains complete order information.

```json
{
  "id": 25,
  "listing_id": 10,
  "car_id": 5,
  "buyer_id": 3,
  "seller_id": 8,
  "amount": 500000,
  "status": "PENDING",
  "payment_status": "PENDING",
  "notes": "I am interested in purchasing this car.",
  "created_at": "2026-09-16T10:30:00",
  "updated_at": "2026-09-16T10:30:00",
  "completed_at": null,
  "buyer": {},
  "seller": {},
  "listing": {},
  "car": {}
}
```

### Fields

| Field | Type | Description |
|---|---|---|
| `id` | integer | Order ID |
| `listing_id` | integer | Related listing |
| `car_id` | integer | Related car |
| `buyer_id` | integer | Buyer user ID |
| `seller_id` | integer | Seller user ID |
| `amount` | Decimal | Order amount |
| `status` | OrderStatus | Current order status |
| `payment_status` | PaymentStatus | Current payment status |
| `notes` | string/null | Order notes |
| `created_at` | datetime | Creation time |
| `updated_at` | datetime | Last update time |
| `completed_at` | datetime/null | Completion time |
| `buyer` | object | Buyer information |
| `seller` | object | Seller information |
| `listing` | object | Listing information |
| `car` | object | Car information |

---

# 5. Create Order

There are two supported order-creation endpoints.

## 5.1 Create Order Using Request Body

### Endpoint

```http
POST /orders
```

### Authentication

Required.

### Request Body

```json
{
  "listing_id": 10,
  "amount": 500000,
  "notes": "I want to purchase this vehicle."
}
```

### Response

```http
201 Created
```

Returns an `OrderResponse`.

---

## 5.2 Create Order Using Listing ID

### Endpoint

```http
POST /orders/listings/{listing_id}
```

### Authentication

Required.

### Path Parameter

| Parameter | Type | Description |
|---|---|---|
| `listing_id` | integer | Listing ID |

### Example

```http
POST /orders/listings/10
```

### Request Body

```json
{
  "amount": 500000,
  "notes": "Interested in this car."
}
```

### Response

```http
201 Created
```

Returns the created `OrderResponse`.


# 6. Get Order

### Endpoint

```http
GET /orders/{order_id}
```

### Authentication

Required.

### Path Parameter

| Parameter | Type | Description |
|---|---|---|
| `order_id` | integer | Order ID |

### Example

```http
GET /orders/25
```

### Response

Returns complete `OrderResponse`.


# 7. Buyer Orders

## 7.1 Get Buyer's Orders

### Endpoint

```http
GET /buyer/orders
```

### Authentication

Required.

### Query Parameters

| Parameter | Type | Required | Default |
|---|---|---:|---:|
| `page` | integer | No | `1` |
| `limit` | integer | No | `20` |
| `status` | OrderStatus | No | None |

### Example

```http
GET /buyer/orders?page=1&limit=20
```

### Filter by Status

```http
GET /buyer/orders?status=PENDING
```

### Response

```json
{
  "data": [],
  "pagination": {}
}
```

---

## 7.2 Cancel Buyer Order

### Endpoint

```http
PATCH /buyer/orders/{order_id}/cancel
```

### Authentication

Required.

### Example

```http
PATCH /buyer/orders/25/cancel
```

### Request Body

None.

### Response

Returns the updated `OrderResponse`.


# 8. Seller Orders

## 8.1 Get Seller Orders

### Endpoint

```http
GET /seller/orders
```

### Authentication

Required.

### Query Parameters

```text
page
limit
status
```

### Example

```http
GET /seller/orders?page=1&limit=20
```

### Filter

```http
GET /seller/orders?status=PENDING
```

### Response

Returns paginated seller orders.

---

## 8.2 Accept Order

### Endpoint

```http
PATCH /seller/orders/{order_id}/accept
```

### Authentication

Required.

### Example

```http
PATCH /seller/orders/25/accept
```

### Request Body

None.

### Response

Returns the updated `OrderResponse`.

---

## 8.3 Reject Order

### Endpoint

```http
PATCH /seller/orders/{order_id}/reject
```

### Authentication

Required.

### Example

```http
PATCH /seller/orders/25/reject
```

### Request Body

None.

### Response

Returns the updated `OrderResponse`.


## 8.4 Update Seller Order Status

### Endpoint

```http
PATCH /seller/orders/{order_id}/status
```

### Authentication

Required.

### Request Body

```json
{
  "status": "COMPLETED"
}
```

### Example

```http
PATCH /seller/orders/25/status
```

### Response

Returns the updated `OrderResponse`.

# 9. Admin Orders

Admin endpoints require admin authentication.

## 9.1 Get All Orders

### Endpoint

```http
GET /admin/orders
```

### Authentication

Required — Admin only.

### Query Parameters

| Parameter | Type | Required | Default |
|---|---|---:|---:|
| `page` | integer | No | `1` |
| `limit` | integer | No | `20` |
| `status` | OrderStatus | No | None |

### Example

```http
GET /admin/orders?page=1&limit=20
```

### Filter

```http
GET /admin/orders?status=PENDING
```

### Response

Returns paginated orders.

---

## 9.2 Get Admin Order Details

### Endpoint

```http
GET /admin/orders/{order_id}
```

### Authentication

Required — Admin only.

### Example

```http
GET /admin/orders/25
```

### Response

Returns `OrderResponse`.

---

## 9.3 Update Admin Order Status

### Endpoint

```http
PATCH /admin/orders/{order_id}/status
```

### Authentication

Required — Admin only.

### Request Body

```json
{
  "status": "COMPLETED"
}
```

### Example

```http
PATCH /admin/orders/25/status
```

### Response

Returns the updated `OrderResponse`.


# 10. API Summary

## Notifications

| Method | Endpoint | Auth | Purpose |
|---|---|---|---|
| GET | `/notifications` | User | Get notifications |
| GET | `/notifications/unread` | User | Get unread notifications |
| PATCH | `/notifications/read-all` | User | Mark all as read |
| PATCH | `/notifications/{notification_id}/read` | User | Mark one as read |
| DELETE | `/notifications/{notification_id}` | User | Delete notification |

## Buyer or user Orders

| Method | Endpoint | Auth | Purpose |
|---|---|---|---|
| POST | `/orders` | User | Create order |
| POST | `/orders/listings/{listing_id}` | User | Create order for listing |
| GET | `/orders/{order_id}` | User | Get order details |
| GET | `/buyer/orders` | User | Get buyer orders |
| PATCH | `/buyer/orders/{order_id}/cancel` | User | Cancel order |

## Seller Orders

| Method | Endpoint | Auth | Purpose |
|---|---|---|---|
| GET | `/seller/orders` | User | Get seller orders |
| PATCH | `/seller/orders/{order_id}/accept` | User | Accept order |
| PATCH | `/seller/orders/{order_id}/reject` | User | Reject order |
| PATCH | `/seller/orders/{order_id}/status` | User | Update order status |

## Admin Orders

| Method | Endpoint | Auth | Purpose |
|---|---|---|---|
| GET | `/admin/orders` | Admin | Get all orders |
| GET | `/admin/orders/{order_id}` | Admin | Get order details |
| PATCH | `/admin/orders/{order_id}/status` | Admin | Update order status |

---

# 11. Typical Order Flow

```text
Buyer
  |
  | POST /orders
  v
PENDING
  |
  | Seller accepts
  v
ACCEPTED
  |
  | Processing / Payment
  v
PROCESSING
  |
  | Seller/Admin updates
  v
COMPLETED
```

Alternative flow:

```text
PENDING
   |
   +----> Buyer Cancels
   |
   +----> Seller Rejects
```

> Exact status transitions are controlled by the `OrderStatus` enum and `order_service` business logic.


# 12. Error Handling

The backend may return the following errors.

## 400 Bad Request

```json
{
  "detail": "Invalid order data."
}
```

## 403 Forbidden

```json
{
  "detail": "You do not have permission to modify this order."
}
```

## 404 Not Found

```json
{
  "detail": "Order not found."
}
```

## 409 Conflict

```json
{
  "detail": "Order cannot be cancelled in its current status."
}
```

## 422 Validation Error

Example:

```json
{
  "detail": [
    {
      "loc": ["body", "amount"],
      "msg": "Input should be greater than 0"
    }
  ]
}
```

# 13. Important Developer Notes

1. Authentication is required for all endpoints shown above.
2. Admin endpoints require admin authentication.
3. User ownership and permission checks are handled by the service layer.
4. `amount` must be greater than `0`.
5. `notes` can contain a maximum of 5000 characters.
6. Pagination uses `page` and `limit`.
7. `limit` must be between `1` and `100`.
8. Order status values must match the project's `OrderStatus` enum.
9. Payment status is returned through `OrderResponse`.
10. `buyer`, `seller`, `listing`, and `car` are nested response objects.
11. Exact order-status transitions are controlled by backend business logic.
12. The examples above use illustrative IDs and values.

---

# 16. Order and Notification Relationship

```text
Order Created
     |
     v
Notification Created
     |
     +----> Buyer
     |
     +----> Seller
     |
     v
Order Status Changes
     |
     v
New Notification
```

Users can manage notifications through:

```text
GET     /notifications
GET     /notifications/unread
PATCH   /notifications/{id}/read
PATCH   /notifications/read-all
DELETE  /notifications/{id}
```