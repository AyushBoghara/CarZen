# Buyer, Seller & Dashboard APIs

## Overview

This document describes the FastAPI endpoints for:

- Buyer discovery
- Buyer inquiries
- Inquiry messaging
- Buyer purchases
- Buyer dashboard
- Seller dashboard
- Seller inquiry management
- Seller replies to buyer inquiries

All endpoints require authentication through:

```python
Depends(get_current_user)
```

The examples below assume the routers are included without an additional prefix. If your application adds a router prefix, prepend that prefix to each endpoint path.

---

# Authentication

All APIs use the authenticated user returned by:

```python
from app.core.auth_dependencies import get_current_user
```

Example request header:

```http
Authorization: Bearer <access_token>
```

If authentication fails, the API should return the appropriate authentication error, typically `401 Unauthorized`.

---

# Common Error Handling

The Buyer and Seller inquiry routers use the following exception mapping:

| Python Exception | HTTP Status | Meaning |
|---|---:|---|
| `LookupError` | `404` | Requested resource was not found |
| `PermissionError` | `403` | User does not have permission |
| `ValueError` | `409` | Business-rule or conflict error |
| Other `Exception` | `400` | Bad request |

Example error response:

```json
{
  "detail": "Resource not found."
}
```

> **Recommendation:** In production, avoid converting every unexpected `Exception` into `400 Bad Request`. Unexpected server errors should normally become `500 Internal Server Error` and should be logged.

# 1. Buyer Discovery APIs

## 1.1 View Listing

Returns listing details for a buyer and records the listing as recently viewed.

### Endpoint

```http
GET /buyer/listings/{listing_id}
```

### Authentication

Required.

### Tags

`Buyer Discovery`

### Path Parameters

| Parameter | Type | Required | Description |
|---|---|---|---|
| `listing_id` | integer | Yes | ID of the marketplace listing |

### Response Model

```python
ListingResponseSecond
```

### Success Response

**Status:** `200 OK`

Example structure:

```json
{
  "id": 101,
  "car_id": 25,
  "seller_id": 12,
  "title": "2023 Honda City",
  "price": 1450000
}
```

The exact response fields are determined by `ListingResponseSecond`.

### Errors

- `404` — Listing not found
- `403` — User is not allowed to access the listing
- `409` — Business-rule conflict
- `400` — Invalid request

---

## 1.2 Recently Viewed Listings

Returns the buyer's recently viewed listings.

### Endpoint

```http
GET /buyer/recently-viewed
```

### Authentication

Required.

### Tags

`Buyer Discovery`

### Query Parameters

| Parameter | Type | Default | Validation | Description |
|---|---|---:|---|---|
| `limit` | integer | `20` | `1–100` | Maximum number of recently viewed listings |

### Example Request

```http
GET /buyer/recently-viewed?limit=10
```

### Response Model

```python
list[RecentlyViewedListingResponse]
```

### Success Response

**Status:** `200 OK`

Example:

```json
[
  {
    "listing_id": 101,
    "viewed_at": "2026-09-15T18:30:00"
  },
  {
    "listing_id": 95,
    "viewed_at": "2026-09-15T17:20:00"
  }
]
```

The exact response fields are determined by `RecentlyViewedListingResponse`.

---

## 1.3 Interested Cars

Returns cars/listings the buyer has marked as favorites or interested in.

### Endpoint

```http
GET /buyer/interested-cars
```

### Authentication

Required.

### Tags

`Buyer Discovery`

### Response Model

```python
list[FavoriteResponse]
```

### Success Response

**Status:** `200 OK`

Example:

```json
[
  {
    "id": 15,
    "user_id": 7,
    "car_id": 25
  }
]
```

The exact response fields are determined by `FavoriteResponse`.

# 2. Buyer Inquiry APIs

## 2.1 Create Inquiry

Creates an inquiry from a buyer for a marketplace listing.

### Endpoint

```http
POST /buyer/listings/{listing_id}/inquiries
```

### Authentication

Required.

### Tags

`Buyer Inquiries`

### Path Parameters

| Parameter | Type | Required | Description |
|---|---|---|---|
| `listing_id` | integer | Yes | Listing for which the buyer wants to make an inquiry |

### Request Body

Schema:

```python
BuyerInquiryCreate
```

Example:

```json
{
  "message": "Is this vehicle still available?",
  "contact_method": "phone"
}
```

> The exact request fields must match `BuyerInquiryCreate`.

### Success Response

**Status:** `201 Created`

Response model:

```python
BuyerInquiryDetailResponse
```

Example:

```json
{
  "id": 42,
  "listing_id": 101,
  "buyer_id": 7,
  "status": "PENDING",
  "message": "Is this vehicle still available?",
  "created_at": "2026-09-15T19:00:00"
}
```


## 2.2 List Buyer Inquiries

Returns inquiries created by the authenticated buyer.

### Endpoint

```http
GET /buyer/inquiries
```

### Authentication

Required.

### Tags

`Buyer Inquiries`

### Query Parameters

| Parameter | Type | Default | Validation | Description |
|---|---|---:|---|---|
| `page` | integer | `1` | `>= 1` | Page number |
| `limit` | integer | `20` | `1–100` | Number of records per page |

### Example Request

```http
GET /buyer/inquiries?page=1&limit=20
```

### Response Model

```python
PaginatedResponse[BuyerInquiryResponse]
```

### Success Response

**Status:** `200 OK`

Example:

```json
{
  "data": [
    {
      "id": 42,
      "listing_id": 101,
      "status": "PENDING"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 1,
    "pages": 1
  }
}
```

---

## 2.3 Get Buyer Inquiry Details

Returns details of a specific buyer inquiry.

### Endpoint

```http
GET /buyer/inquiries/{inquiry_id}
```

### Authentication

Required.

### Tags

`Buyer Inquiries`

### Path Parameters

| Parameter | Type | Required | Description |
|---|---|---|---|
| `inquiry_id` | integer | Yes | Inquiry ID |

### Response Model

```python
BuyerInquiryDetailResponse
```

### Success Response

**Status:** `200 OK`

Example:

```json
{
  "id": 42,
  "listing_id": 101,
  "buyer_id": 7,
  "status": "PENDING",
  "created_at": "2026-09-15T19:00:00"
}
```

### Errors

- `404` — Inquiry not found
- `403` — Inquiry does not belong to the authenticated buyer

# 3. Inquiry Message APIs

These endpoints allow authenticated participants in an inquiry to view and send messages.


## 3.1 List Inquiry Messages

Returns all messages associated with an inquiry.

### Endpoint

```http
GET /inquiries/{inquiry_id}/messages
```

### Authentication

Required.

### Tags

`Inquiry Messages`

### Path Parameters

| Parameter | Type | Required | Description |
|---|---|---|---|
| `inquiry_id` | integer | Yes | Inquiry ID |

### Response Model

```python
list[InquiryMessageResponse]
```

### Success Response

**Status:** `200 OK`

Example:

```json
[
  {
    "id": 1,
    "inquiry_id": 42,
    "sender_id": 7,
    "message": "Is this vehicle still available?",
    "created_at": "2026-09-15T19:00:00"
  },
  {
    "id": 2,
    "inquiry_id": 42,
    "sender_id": 12,
    "message": "Yes, the vehicle is available.",
    "created_at": "2026-09-15T19:05:00"
  }
]
```

---

## 3.2 Send Inquiry Message

Allows an authenticated inquiry participant to send a message.

### Endpoint

```http
POST /inquiries/{inquiry_id}/messages
```

### Authentication

Required.

### Tags

`Inquiry Messages`

### Path Parameters

| Parameter | Type | Required | Description |
|---|---|---|---|
| `inquiry_id` | integer | Yes | Inquiry ID |

### Request Body

Schema:

```python
InquiryMessageCreate
```

Example:

```json
{
  "message": "Can I schedule a test drive?"
}
```

### Success Response

**Status:** `201 Created`

Response model:

```python
InquiryMessageResponse
```

Example:

```json
{
  "id": 3,
  "inquiry_id": 42,
  "sender_id": 7,
  "message": "Can I schedule a test drive?",
  "created_at": "2026-09-15T19:10:00"
}
```


# 4. Buyer or user Purchase APIs

## 4.1 List Buyer Purchases

Returns purchases/transactions belonging to the authenticated buyer.

### Endpoint

```http
GET /buyer/purchases
```

### Authentication

Required.

### Tags

`Buyer Purchases`

### Query Parameters

| Parameter | Type | Default | Validation | Description |
|---|---|---:|---|---|
| `page` | integer | `1` | `>= 1` | Page number |
| `limit` | integer | `20` | `1–100` | Records per page |
| `transaction_status` | `TransactionStatus` | None | Enum | Filter by transaction status |

### Example

```http
GET /buyer/purchases?page=1&limit=20
```

With status filtering:

```http
GET /buyer/purchases?page=1&limit=20&transaction_status=COMPLETED
```

The valid values of `transaction_status` are defined by:

```python
app.models.enums.TransactionEnums.TransactionStatus
```

### Response Model

```python
PaginatedResponse[BuyerPurchaseResponse]
```

### Success Response

**Status:** `200 OK`

Example:

```json
{
  "data": [
    {
      "transaction_id": 501,
      "status": "COMPLETED"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 1,
    "pages": 1
  }
}
```

## 4.2 Get Buyer Purchase

Returns details for a specific buyer transaction.

### Endpoint

```http
GET /buyer/purchases/{transaction_id}
```

### Authentication

Required.

### Tags

`Buyer Purchases`

### Path Parameters

| Parameter | Type | Required | Description |
|---|---|---|---|
| `transaction_id` | integer | Yes | Transaction ID |

### Response Model

```python
BuyerPurchaseResponse
```

### Success Response

**Status:** `200 OK`

Example:

```json
{
  "transaction_id": 501,
  "status": "COMPLETED"
}
```

### Errors

- `404` — Transaction not found
- `403` — Transaction does not belong to the authenticated buyer

# 5. Buyer(User) Dashboard API

## 5.1 Get Buyer Dashboard

Returns dashboard information for the authenticated buyer.

### Endpoint

```http
GET /buyer/dashboard
```

### Authentication

Required.

### Tags

`Buyer Dashboard`

### Response Model

```python
BuyerDashboardResponse
```

### Success Response

**Status:** `200 OK`

Example structure:

```json
{
  "total_inquiries": 10,
  "total_purchases": 3,
  "favorite_cars": 8,
  "recently_viewed": 5
}
```

The exact fields are determined by `BuyerDashboardResponse`.


# 6. Seller Dashboard API

## 6.1 Get Seller Dashboard

Returns seller dashboard metrics for an authenticated seller/reseller/user.

### Endpoint

```http
GET /seller/dashboard
```

### Authentication

Required.

### Tags

`Seller Dashboard`

### Allowed Roles

The endpoint accepts users with any of these roles:

```python
UserRoles.SELLER
UserRoles.USER
UserRoles.RESELLER
```

### Authorization Logic

```python
if current_user.role not in {
    UserRoles.SELLER,
    UserRoles.USER,
    UserRoles.RESELLER
}:
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Seller or reseller access required."
    )
```

### Response Model

```python
SellerDashboardResponse
```

### Success Response

**Status:** `200 OK`

Example structure:

```json
{
  "total_listings": 25,
  "active_listings": 18,
  "total_inquiries": 32,
  "completed_sales": 7
}
```

The exact fields are determined by `SellerDashboardResponse`.

### Forbidden Response

**Status:** `403 Forbidden`

```json
{
  "detail": "Seller or reseller access required."
}
```



# 7. Seller Inquiry APIs

## 7.1 List Seller Inquiries

Returns inquiries received by the authenticated seller.

### Endpoint

```http
GET /seller/inquiries
```

### Authentication

Required.

### Tags

`Seller Inquiries`

### Query Parameters

| Parameter | Type | Default | Validation | Description |
|---|---|---:|---|---|
| `page` | integer | `1` | `>= 1` | Page number |
| `limit` | integer | `20` | `1–100` | Records per page |
| `status` | `InquiryStatus` | None | Enum | Filter inquiries by status |

### Important

The Python parameter is:

```python
inquiry_status
```

but the public query parameter is:

```text
status
```

because the endpoint uses:

```python
Query(None, alias="status")
```

### Example

```http
GET /seller/inquiries?page=1&limit=20
```

With filtering:

```http
GET /seller/inquiries?page=1&limit=20&status=PENDING
```

Valid values are defined by:

```python
app.models.inquiries.InquiryStatus
```

### Response Model

```python
PaginatedResponse[SellerInquiryResponse]
```

### Success Response

**Status:** `200 OK`

Example:

```json
{
  "data": [
    {
      "id": 42,
      "listing_id": 101,
      "buyer_id": 7,
      "status": "PENDING"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 1,
    "pages": 1
  }
}
```

---

## 7.2 Get Seller Inquiry Details

Returns details of a specific inquiry received by the seller.

### Endpoint

```http
GET /seller/inquiries/{inquiry_id}
```

### Authentication

Required.

### Tags

`Seller Inquiries`

### Path Parameters

| Parameter | Type | Required | Description |
|---|---|---|---|
| `inquiry_id` | integer | Yes | Inquiry ID |

### Response Model

```python
SellerInquiryDetailResponse
```

### Success Response

**Status:** `200 OK`

Example:

```json
{
  "id": 42,
  "listing_id": 101,
  "buyer_id": 7,
  "status": "PENDING"
}
```

### Errors

- `404` — Inquiry not found
- `403` — Seller is not authorized to access the inquiry

---

## 7.3 Update Inquiry Status

Updates the status of an inquiry.

### Endpoint

```http
PATCH /seller/inquiries/{inquiry_id}/status
```

### Authentication

Required.

### Tags

`Seller Inquiries`

### Path Parameters

| Parameter | Type | Required | Description |
|---|---|---|---|
| `inquiry_id` | integer | Yes | Inquiry ID |

### Request Body

Schema:

```python
SellerInquiryStatusUpdate
```

Example:

```json
{
  "status": "RESPONDED"
}
```

The valid status values are defined by:

```python
InquiryStatus
```

### Success Response

**Status:** `200 OK`

Response model:

```python
SellerInquiryDetailResponse
```

Example:

```json
{
  "id": 42,
  "listing_id": 101,
  "buyer_id": 7,
  "status": "RESPONDED"
}
```

---

## 7.4 Reply to Buyer Inquiry

Allows a seller to send a message in an inquiry conversation.

### Endpoint

```http
POST /seller/inquiries/{inquiry_id}/messages
```

### Authentication

Required.

### Tags

`Seller Inquiries`

### Path Parameters

| Parameter | Type | Required | Description |
|---|---|---|---|
| `inquiry_id` | integer | Yes | Inquiry ID |

### Request Body

Schema:

```python
InquiryMessageCreate
```

Example:

```json
{
  "message": "Yes, the car is available. You can visit tomorrow."
}
```

### Success Response

**Status:** `201 Created`

Response model:

```python
InquiryMessageResponse
```

Example:

```json
{
  "id": 4,
  "inquiry_id": 42,
  "sender_id": 12,
  "message": "Yes, the car is available. You can visit tomorrow.",
  "created_at": "2026-09-15T19:20:00"
}
```

---

# 8. API Endpoint Summary

| # | Method | Endpoint | Tag | Purpose |
|---:|---|---|---|---|
| 1 | `GET` | `/buyer/listings/{listing_id}` | Buyer or user Discovery | View listing and record view |
| 2 | `GET` | `/buyer/recently-viewed` | Buyer or user Discovery | Get recently viewed listings |
| 3 | `GET` | `/buyer/interested-cars` | Buyer or user Discovery | Get interested/favorite cars |
| 4 | `POST` | `/buyer/listings/{listing_id}/inquiries` | Buyer or user Inquiries | Create buyer inquiry |
| 5 | `GET` | `/buyer/inquiries` | Buyer or user Inquiries | List buyer inquiries |
| 6 | `GET` | `/buyer/inquiries/{inquiry_id}` | Buyer or user Inquiries | Get buyer inquiry details |
| 7 | `GET` | `/inquiries/{inquiry_id}/messages` | Inquiry Messages | List inquiry messages |
| 8 | `POST` | `/inquiries/{inquiry_id}/messages` | Inquiry Messages | Send inquiry message |
| 9 | `GET` | `/buyer/purchases` | Buyer or user Purchases | List buyer purchases |
| 10 | `GET` | `/buyer/purchases/{transaction_id}` | Buyer or user Purchases | Get purchase details |
| 11 | `GET` | `/buyer/dashboard` | Buyer Dashboard | Get Buyer or user dashboard |
| 12 | `GET` | `/seller/dashboard` | Seller Dashboard | Get seller dashboard |
| 13 | `GET` | `/seller/inquiries` | Seller Inquiries | List seller inquiries |
| 14 | `GET` | `/seller/inquiries/{inquiry_id}` | Seller Inquiries | Get seller inquiry details |
| 15 | `PATCH` | `/seller/inquiries/{inquiry_id}/status` | Seller Inquiries | Update inquiry status |
| 16 | `POST` | `/seller/inquiries/{inquiry_id}/messages` | Seller Inquiries | Reply to buyer |

# 9. Request/Response Schema Mapping

## Buyer Schemas

Imported from:

```python
app.schemas.buyer_schema
```

| Schema | Usage |
|---|---|
| `BuyerDashboardResponse` | Buyer dashboard response |
| `BuyerInquiryCreate` | Create buyer inquiry request |
| `BuyerInquiryDetailResponse` | Buyer inquiry details |
| `BuyerInquiryResponse` | Buyer inquiry list item |
| `BuyerPurchaseResponse` | Buyer purchase response |
| `InquiryMessageCreate` | Send inquiry message request |
| `InquiryMessageResponse` | Inquiry message response |
| `RecentlyViewedListingResponse` | Recently viewed listing |

## Seller Schemas

Imported from:

```python
app.schemas.seller_schema
```

| Schema | Usage |
|---|---|
| `SellerInquiryDetailResponse` | Seller inquiry details |
| `SellerInquiryResponse` | Seller inquiry list item |
| `SellerInquiryStatusUpdate` | Update inquiry status request |

## Marketplace Schemas

Imported from:

```python
app.schemas.marketplace_schema
```

| Schema | Usage |
|---|---|
| `FavoriteResponse` | Interested/favorite car response |
| `ListingResponseSecond` | Buyer listing response |

## Dashboard Schemas

Imported from:

```python
app.schemas.dashboard_schema
```

| Schema | Usage |
|---|---|
| `SellerDashboardResponse` | Seller dashboard response |

## Pagination

Imported from:

```python
app.schemas.cars_schema
```

Generic response:

```python
PaginatedResponse[T]
```

Used for:

```text
PaginatedResponse[BuyerInquiryResponse]
PaginatedResponse[BuyerPurchaseResponse]
PaginatedResponse[SellerInquiryResponse]
```

---

# 10. Typical Buyer Flow

```text
Authenticate
    |
    v
Browse Listing
    |
    +--> Listing view is recorded
    |
    v
Save / Favorite Car
    |
    v
Create Inquiry
    |
    v
Send / Receive Messages
    |
    v
Seller Responds
    |
    v
Inquiry Status Updated
    |
    v
Purchase
    |
    v
View Purchase
```


# 11. Typical Seller Flow

```text
Authenticate
    |
    v
Open Seller Dashboard
    |
    v
View Incoming Inquiries
    |
    v
Open Inquiry
    |
    +--> Review Buyer Information
    |
    +--> Review Listing Information
    |
    v
Reply to Buyer
    |
    v
Update Inquiry Status
    |
    v
Continue Conversation
    |
    v
Complete Sale
```

---

# 12. cURL Examples

## View Listing

```bash
curl -X GET "http://localhost:8000/buyer/listings/101" \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

## Recently Viewed

```bash
curl -X GET "http://localhost:8000/buyer/recently-viewed?limit=20" \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

## Interested Cars

```bash
curl -X GET "http://localhost:8000/buyer/interested-cars" \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

## Create Inquiry

```bash
curl -X POST "http://localhost:8000/buyer/listings/101/inquiries" \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Is this vehicle still available?"
  }'
```

## List Buyer Inquiries

```bash
curl -X GET "http://localhost:8000/buyer/inquiries?page=1&limit=20" \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

## Get Inquiry

```bash
curl -X GET "http://localhost:8000/buyer/inquiries/42" \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

## List Inquiry Messages

```bash
curl -X GET "http://localhost:8000/inquiries/42/messages" \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

## Send Inquiry Message

```bash
curl -X POST "http://localhost:8000/inquiries/42/messages" \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Can I schedule a test drive?"
  }'
```

## List Purchases

```bash
curl -X GET "http://localhost:8000/buyer/purchases?page=1&limit=20" \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

## Get Purchase

```bash
curl -X GET "http://localhost:8000/buyer/purchases/501" \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

## Buyer Dashboard

```bash
curl -X GET "http://localhost:8000/buyer/dashboard" \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

## Seller Dashboard

```bash
curl -X GET "http://localhost:8000/seller/dashboard" \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

## Seller Inquiries

```bash
curl -X GET "http://localhost:8000/seller/inquiries?page=1&limit=20" \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

## Filter Seller Inquiries

```bash
curl -X GET "http://localhost:8000/seller/inquiries?page=1&limit=20&status=PENDING" \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

## Get Seller Inquiry

```bash
curl -X GET "http://localhost:8000/seller/inquiries/42" \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

## Update Inquiry Status

```bash
curl -X PATCH "http://localhost:8000/seller/inquiries/42/status" \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "RESPONDED"
  }'
```

## Seller Reply

```bash
curl -X POST "http://localhost:8000/seller/inquiries/42/messages" \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "The vehicle is available for a test drive."
  }'
```

---

# 13. FastAPI Integration

Example router registration:

```python
from fastapi import FastAPI

from app.routers.buyer import router as buyer_router
from app.routers.dashboard import router as dashboard_router
from app.routers.seller import router as seller_router

app = FastAPI()

app.include_router(buyer_router)
app.include_router(dashboard_router)
app.include_router(seller_router)
```

If the project uses prefixes, for example:

```python
app.include_router(
    buyer_router,
    prefix="/api/v1"
)
```

then the resulting endpoint becomes:

```http
GET /api/v1/buyer/dashboard
```

# 14. Authorization Matrix

| API Area | Buyer | User | Seller | Reseller |
|---|:---:|:---:|:---:|:---:|
| Buyer Discovery | Yes* | Yes* | Depends on service | Depends on service |
| Buyer Inquiries | Yes* | Yes* | Depends on service | Depends on service |
| Inquiry Messages | Participant | Participant | Participant | Participant |
| Buyer Purchases | Owner only | Owner only | No* | No* |
| Buyer Dashboard | Yes* | Yes* | Depends on service | Depends on service |
| Seller Dashboard | No* | Yes | Yes | Yes |
| Seller Inquiries | No* | Depends on service | Yes* | Yes* |
| Seller Status Update | No* | Depends on service | Yes* | Yes* |
| Seller Reply | No* | Depends on service | Yes* | Yes* |

`*` Actual authorization is ultimately determined by the corresponding service-layer implementation.


# 15. Recommended API Improvements

## 15.1 Use explicit HTTP status constants

Instead of:

```python
raise HTTPException(code, str(exc))
```

prefer:

```python
raise HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail=str(exc)
)
```

This is easier to read and maintain.

## 15.2 Avoid catching all exceptions

Current pattern:

```python
except Exception as exc:
    _raise(exc)
```

can hide programming errors.

A better approach is to catch only expected service exceptions:

```python
except LookupError as exc:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=str(exc)
    )
except PermissionError as exc:
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=str(exc)
    )
except ValueError as exc:
    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail=str(exc)
    )
```

Unexpected exceptions should be allowed to reach the application's global exception handler.

## 15.3 Use consistent endpoint naming

The current design uses:

```text
/buyer/inquiries/{id}/...
/seller/inquiries/{id}/...
/inquiries/{id}/messages
```

For a more consistent REST structure, consider:

```text
/buyer/inquiries/{inquiry_id}/messages
/seller/inquiries/{inquiry_id}/messages
```

or a shared:

```text
/inquiries/{inquiry_id}/messages
```

with service-layer participant authorization.

## 15.4 Document exact enum values

The OpenAPI documentation will automatically expose enum values when the Pydantic schemas and SQLAlchemy/Python enums are correctly defined.

The exact values should be taken directly from:

```python
TransactionStatus
InquiryStatus
UserRoles
```

rather than hard-coded in documentation.


# 16. OpenAPI / Swagger

When the FastAPI application is running, the API documentation is normally available at:

```text
/docs
```

For example:

```text
http://localhost:8000/docs
```

ReDoc is normally available at:

```text
http://localhost:8000/redoc
```

The exact host, port, and global API prefix depend on the application's deployment configuration.
