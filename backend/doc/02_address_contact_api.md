# Address & Contact Management API 

## 1. Overview

These APIs allow an authenticated user to:

### Address Management
- Create an address
- Get all addresses
- Get a single address
- Update an address
- Soft-delete an address

### Contact Management
- Create contact details
- Get all contact details
- Get a single contact
- Update contact details
- Update contact visibility
- Soft-delete contact details

All endpoints require authentication through `get_current_user`.


## 2. Authentication

All APIs require:

```http
Authorization: Bearer <access_token>
```

The authenticated user's ID is obtained from the access token. Do not send `user_id` from the frontend.



# 3. Address Management APIs

## 3.1 Create Address

### Endpoint

```http
POST /address-add
```

### Description

Creates a new address for the authenticated user.

### Request Body

```json
{
    "address_line_1": "101, C G Road",
    "address_line_2": "Navrangpura",
    "landmark": "Near Municipal Market",
    "city": "Ahmedabad",
    "state": "Gujarat",
    "country": "India",
    "postal_code": "380009",
    "latitude": 23.0225,
    "longitude": 72.5714,
    "is_default": true
}
```

### Response

**201 Created**

```json
{
    "id": 9,
    "address_line_1": "101, C G Road",
    "address_line_2": "Navrangpura",
    "landmark": "Near Municipal Market",
    "city": "Ahmedabad",
    "state": "Gujarat",
    "country": "India",
    "postal_code": "380009",
    "latitude": 23.0225,
    "longitude": 72.5714,
    "is_default": true
}
```

### Error Response

**409 Conflict**

```json
{
    "detail": "Unable to create address. Please check the address data."
}
```


## 3.2 Get All Addresses

### Endpoint

```http
GET /address
```

### Description

Returns all active addresses belonging to the authenticated user. Soft-deleted addresses are excluded.

### Response

**200 OK**

```json
[
    {
        "id": 9,
        "address_line_1": "101, C G Road",
        "address_line_2": "Navrangpura",
        "landmark": "Near Municipal Market",
        "city": "Ahmedabad",
        "state": "Gujarat",
        "country": "India",
        "postal_code": "380009",
        "latitude": 23.0225,
        "longitude": 72.5714,
        "is_default": true
    }
]
```

> Note: the service returns an empty list when there are no addresses. If a `404` is required for an empty result, use `if not address:` instead of `if address is None:`.


## 3.3 Get Address By ID

### Endpoint

```http
GET /address/{address_id}
```

### Example

```http
GET /address/9
```

### Response

**200 OK**

```json
{
    "id": 9,
    "address_line_1": "101, C G Road",
    "address_line_2": "Navrangpura",
    "landmark": "Near Municipal Market",
    "city": "Ahmedabad",
    "state": "Gujarat",
    "country": "India",
    "postal_code": "380009",
    "latitude": 23.0225,
    "longitude": 72.5714,
    "is_default": true
}
```

### Error Response

**404 Not Found**

```json
{
    "detail": "Address not found."
}
```

The service verifies that the address belongs to the authenticated user.

## 3.4 Update Address

### Endpoint

```http
PATCH /address/{address_id}
```

### Example

```http
PATCH /address/9
```

### Description

Updates an existing address. Only fields that need to be changed should be sent.

### Request Body

```json
{
    "address_line_1": "202, C G Road",
    "landmark": "Near Municipal Market",
    "postal_code": "380010"
}
```

### Response

**200 OK**

```json
{
    "id": 9,
    "address_line_1": "202, C G Road",
    "address_line_2": "Navrangpura",
    "landmark": "Near Municipal Market",
    "city": "Ahmedabad",
    "state": "Gujarat",
    "country": "India",
    "postal_code": "380010",
    "latitude": 23.0225,
    "longitude": 72.5714,
    "is_default": true
}
```

### Make Address Default

```json
{
    "is_default": true
}
```

When an address is made default, other active default addresses belonging to the same user are automatically changed to `false`.


## 3.5 Delete Address

### Endpoint

```http
DELETE /address/{address_id}
```

### Example

```http
DELETE /address/9
```

### Description

Soft-deletes the address by setting `deleted_at`. The database record is not physically deleted.

### Response

**200 OK**

```json
{
    "message": "Address deleted successfully."
}
```

### Delete Again

**404 Not Found**

```json
{
    "detail": "Address Not Found."
}
```

# 4. Contact Management APIs

## 4.1 Create Contact

### Endpoint

```http
POST /contact-add
```

### Description

Creates contact information for the authenticated user and associates it with one of the user's active addresses.

### Request Body

```json
{
    "address_id": 9,
    "whatsapp_number": "9632587420",
    "preferred_contact_method": "phone",
    "contact_visibility": "buyers_only",
    "is_visible": true
}
```

### Address Validation

The supplied `address_id` must belong to the authenticated user and must not be soft-deleted.

### Response

**201 Created**

```json
{
    "id": 1,
    "email": "user@gmail.com",
    "phone_number": "8696544250",
    "whatsapp_number": "9632587420",
    "preferred_contact_method": "phone",
    "contact_visibility": "buyers_only",
    "is_visible": true,
    "address": {
        "id": 9,
        "address_line_1": "101, C G Road",
        "address_line_2": "Navrangpura",
        "landmark": "Near Municipal Market",
        "city": "Ahmedabad",
        "state": "Gujarat",
        "country": "India",
        "postal_code": "380009",
        "latitude": 23.0225,
        "longitude": 72.5714,
        "is_default": true
    }
}
```

`email` and `phone_number` are taken from the authenticated user's `User` record and are not accepted from the request body.


## 4.2 Get All Contacts

### Endpoint

```http
GET /contact
```

### Description

Returns all active contacts belonging to the authenticated user.

### Response

**200 OK**

```json
[
    {
        "id": 1,
        "email": "user@gmail.com",
        "phone_number": "8696544250",
        "whatsapp_number": "9632587420",
        "preferred_contact_method": "phone",
        "contact_visibility": "buyers_only",
        "is_visible": true,
        "address": {
            "id": 9,
            "address_line_1": "101, C G Road",
            "address_line_2": "Navrangpura",
            "landmark": "Near Municipal Market",
            "city": "Ahmedabad",
            "state": "Gujarat",
            "country": "India",
            "postal_code": "380009",
            "latitude": 23.0225,
            "longitude": 72.5714,
            "is_default": true
        }
    }
]
```

## 4.3 Get Contact By ID

### Endpoint

```http
GET /contact/{contact_id}
```

### Example

```http
GET /contact/1
```

### Response

**200 OK**

```json
{
    "id": 1,
    "email": "user@gmail.com",
    "phone_number": "8696544250",
    "whatsapp_number": "9632587420",
    "preferred_contact_method": "phone",
    "contact_visibility": "buyers_only",
    "is_visible": true,
    "address": {
        "id": 9,
        "address_line_1": "101, C G Road",
        "city": "Ahmedabad",
        "state": "Gujarat",
        "country": "India",
        "postal_code": "380009",
        "is_default": true
    }
}
```

### Error Response

**404 Not Found**

```json
{
    "detail": "Contact Not Found."
}
```

## 4.4 Update Contact

### Endpoint

```http
PATCH /contact/{contact_id}
```

### Example

```http
PATCH /contact/1
```

### Request Body

```json
{
    "whatsapp_number": "9876543210",
    "preferred_contact_method": "whatsapp"
}
```

### Change Address

```json
{
    "address_id": 10
}
```

The API verifies that the new address belongs to the authenticated user and is active.

### Response

**200 OK**

```json
{
    "id": 1,
    "email": "user@gmail.com",
    "phone_number": "8696544250",
    "whatsapp_number": "9876543210",
    "preferred_contact_method": "whatsapp",
    "contact_visibility": "buyers_only",
    "is_visible": true,
    "address": {
        "id": 10,
        "address_line_1": "New Address",
        "city": "Ahmedabad",
        "state": "Gujarat",
        "country": "India"
    }
}
```

## 4.5 Update Contact Visibility

### Endpoint

```http
PATCH /contact/{contact_id}/visibility
```

### Example

```http
PATCH /contact/1/visibility
```

### Description

Updates only the contact visibility setting.

### Request Body

```json
{
    "contact_visibility": "public"
}
```

Example visibility values:

```text
public
buyers_only
private
```

Use the exact values defined by the `ContactVisibility` enum.

### Response

**200 OK**

```json
{
    "id": 1,
    "email": "user@gmail.com",
    "phone_number": "8696544250",
    "whatsapp_number": "9632587420",
    "preferred_contact_method": "phone",
    "contact_visibility": "public",
    "is_visible": true,
    "address": {
        "id": 9,
        "address_line_1": "101, C G Road",
        "city": "Ahmedabad",
        "state": "Gujarat",
        "country": "India",
        "postal_code": "380009",
        "is_default": true
    }
}
```


## 4.6 Delete Contact

### Endpoint

```http
DELETE /contact/{contact_id}
```

### Example

```http
DELETE /contact/1
```

### Description

Soft-deletes the contact by setting `deleted_at`.

### Response

**200 OK**

```json
{
    "message": "Contact deleted successfully."
}
```

### Delete Again

**404 Not Found**

```json
{
    "detail": "Contact Not Found."
}
```

# 5. API Summary

| Method | Endpoint | Purpose |
|---|---|---|
| `POST` | `/address-add` | Create address |
| `GET` | `/address` | Get all addresses |
| `GET` | `/address/{address_id}` | Get address |
| `PATCH` | `/address/{address_id}` | Update address |
| `DELETE` | `/address/{address_id}` | Soft-delete address |
| `POST` | `/contact-add` | Create contact |
| `GET` | `/contact` | Get all contacts |
| `GET` | `/contact/{contact_id}` | Get contact |
| `PATCH` | `/contact/{contact_id}` | Update contact |
| `PATCH` | `/contact/{contact_id}/visibility` | Update visibility |
| `DELETE` | `/contact/{contact_id}` | Soft-delete contact |

---

# 6. HTTP Status Codes

| Status | Meaning | Usage |
|---|---|---|
| `200` | OK | GET, PATCH, DELETE success |
| `201` | Created | Address/contact created |
| `404` | Not Found | Address/contact doesn't exist |
| `403` | Forbidden | User is not permitted |
| `409` | Conflict | Validation/database conflict |
| `500` | Internal Server Error | Unexpected server error |

---

# 7. Security and Ownership

Resources are always scoped to the authenticated user.

### Address

```python
Address.user_id == owner.id
```

### Contact

```python
Contact.user_id == owner.id
```

Therefore, a user cannot access, update, or delete another user's address/contact by changing the ID in the URL.

For example:

```http
GET /address/25
GET /contact/25
PATCH /contact/25
DELETE /contact/25
```

will return `404` when the resource does not belong to the authenticated user.

# 8. Soft Delete Behavior

Both addresses and contacts use soft deletion.

Instead of deleting the database record:

```python
deleted_at = datetime.now(timezone.utc)
```

is stored.

All normal queries filter:

```python
deleted_at.is_(None)
```

Therefore:

- Deleted records are hidden from GET APIs.
- A deleted ID cannot be updated.
- A deleted ID cannot be deleted again.
- Re-deleting the same ID returns `404 Not Found`.
