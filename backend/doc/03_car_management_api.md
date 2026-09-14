# CarZen Car Management API

## Overview

Base URL: `http://127.0.0.1:8000`  
API version prefix: `/v1`

## Catalog APIs

Catalog hierarchy is authoritative:

```text
Car Brand -> Car Model -> Car Variant -> Car
```

Only active, non-deleted catalog entries can be used while creating or updating a car.

### Car Brands

| Method | Path                               | Access | Description                                                        |
| ------ | ---------------------------------- | ------ | ------------------------------------------------------------------ |
| GET    | `/v1/car-brands`                   | Public | Paginated brands. Filters: `page`, `limit`, `search`, `is_active`. |
| GET    | `/v1/car-brands/{brand_id}`        | Public | One active/non-deleted brand record.                               |
| POST   | `/v1/car-brands`                   | Public | Create a brand.                                                    |
| PATCH  | `/v1/car-brands/{brand_id}`        | Public | Partial update.                                                    |
| DELETE | `/v1/car-brands/{brand_id}`        | Public | Soft-delete and deactivate.                                        |
| PATCH  | `/v1/car-brands/{brand_id}/status` | Public | Set active/inactive state.                                         |

Create/update body:

```json
{
  "name": "Toyota",
  "slug": "toyota",
  "country": "Japan",
  "logo_url": "https://cdn.example.com/toyota.png",
  "description": "Japanese manufacturer",
  "is_active": true
}
```

Status body:

```json
{ "is_active": false }
```

Brand `name` and `slug` must be unique. Slugs use lowercase hyphenated text such as `land-rover`.

### Car Models

| Method | Path                               | Access | Description                                                               |
| ------ | ---------------------------------- | ------ | ------------------------------------------------------------------------- |
| GET    | `/v1/car-models`                   | Public | Filters: `page`, `limit`, `search`, `brand_id`, `body_type`, `is_active`. |
| GET    | `/v1/car-models/{model_id}`        | Public | One model.                                                                |
| GET    | `/v1/car-brands/{brand_id}/models` | Public | Paginated models belonging to a brand.                                    |
| POST   | `/v1/car-models`                   | Public | Create a model under an active brand.                                     |
| PATCH  | `/v1/car-models/{model_id}`        | Public | Partial update.                                                           |
| DELETE | `/v1/car-models/{model_id}`        | Public | Soft-delete and deactivate.                                               |
| PATCH  | `/v1/car-models/{model_id}/status` | Public | Set active/inactive state.                                                |

```json
{
  "brand_id": 1,
  "name": "Fortuner",
  "slug": "fortuner",
  "body_type": "suv",
  "seating_capacity": 7,
  "description": "Full-size SUV",
  "is_active": true
}
```

### Car Variants

| Method | Path                                 | Access | Description                                                                    |
| ------ | ------------------------------------ | ------ | ------------------------------------------------------------------------------ |
| GET    | `/v1/car-variants`                   | Public | Filters: `page`, `limit`, `brand_id`, `model_id`, `fuel_type`, `transmission`. |
| GET    | `/v1/car-variants/{variant_id}`      | Public | One variant.                                                                   |
| GET    | `/v1/car-models/{model_id}/variants` | Public | Paginated variants belonging to a model.                                       |
| POST   | `/v1/car-variants`                   | Public | Create a variant under an active model and brand.                              |
| PATCH  | `/v1/car-variants/{variant_id}`      | Public | Partial update.                                                                |
| DELETE | `/v1/car-variants/{variant_id}`      | Public | Soft-delete a variant.                                                         |

```json
{
  "model_id": 10,
  "variant_name": "4x4 Diesel AT",
  "fuel_type": "diesel",
  "transmission": "automatic",
  "engine_cc": 2755,
  "horsepower": 201,
  "seating_capacity": 7,
  "ex_showroom_price": 5200000
}
```

## Seller Car APIs

| Method | Path                | Access                         | Description                                                                                      |
| ------ | ------------------- | ------------------------------ | ------------------------------------------------------------------------------------------------ |
| POST   | `/v1/cars`          | Owner,seller        | Create a car owned by the token user.                                                            |
| GET    | `/v1/cars`          | Owner,seller        | Paginated list of the token user's cars.                                                         |
| GET    | `/v1/cars/{car_id}` | Owner,seller  | Full car detail, catalog hierarchy, safe owner summary, media, and features.                     |
| PATCH  | `/v1/cars/{car_id}` | Owner,seller | Partial update. Material identity changes return an approved/rejected car to `pending_approval`. |
| DELETE | `/v1/cars/{car_id}` | Owner,seller | Soft-delete car.                                                                                 |

`GET /v1/cars` supports: `page`, `limit`, `search`, `status`, `verification_status`, `brand_id`, `model_id`, `variant_id`, `fuel_type`, `transmission`, `city`, `state`, `min_price`, `max_price`, `min_year`, and `max_year`.

Create Car for seller:

```json
{
  "variant_id": 2,
  "registration_number": "GJ01AB1234",
  "vin_number": "MA3EJKD1S00123456",
  "manufacturing_year": 2022,
  "registration_year": 2022,
  "fuel_type": "diesel",
  "transmission": "automatic",
  "engine_cc": 2755,
  "horsepower": 201,
  "mileage_km": 35000,
  "color": "White",
  "seating_capacity": 7,
  "owner_count": 1,
  "ownership_type": "first_owner",
  "condition": "good",
  "insurance_company": "ABC Insurance",
  "insurance_type": "comprehensive",
  "insurance_expiry": "2027-03-15",
  "rc_status": "valid",
  "city": "Ahmedabad",
  "state": "Gujarat",
  "country": "India",
  "postal_code": "380001",
  "description": "Well maintained vehicle",
  "expected_market_price": 3200000
}
```

Validation rules:

- `owner_id` is always assigned from the JWT and is never accepted from clients.
- Resale submissions additionally require `registration_number`, `vin_number`, `registration_year`, and `ownership_type`.
- `variant_id` must resolve to an active, non-deleted variant, model, and brand.
- Registration year cannot precede manufacturing year.
- Registration number and VIN are unique when supplied.
- Mileage and monetary values cannot be negative; owner count must be at least one.
- New cars start as `pending_approval` and `is_verified: false`.

## Car Media APIs

Media remains nested under its car. There is no top-level image-upload API.

Owner is the user(seller), reseller.

| Method | Path                                         | Access | Description                                                                                             |
| ------ | -------------------------------------------- | ------ | ------------------------------------------------------------------------------------------------------- |
| GET    | `/v1/cars/{car_id}/media`                    | Owner  | List active media in ascending `sort_order`.                                                            |
| POST   | `/v1/cars/{car_id}/media`                    | Owner  | Upload media with `multipart/form-data`.                                                                |
| PATCH  | `/v1/cars/{car_id}/media/{media_id}`         | Owner  | Update `sort_order`, `is_primary`, or `thumbnail_url`. **Note: PATCH is not Requried for update image** |
| DELETE | `/v1/cars/{car_id}/media/{media_id}`         | Owner  | Soft-delete a media item.                                                                               |
| PATCH  | `/v1/cars/{car_id}/media/{media_id}/primary` | Owner  | Make one item primary and clear every other primary item.                                               |
| PATCH  | `/v1/cars/{car_id}/media/reorder`            | Owner  | Update sort order transactionally.                                                                      |

Upload fields:

| Form field   | Type    | Required | Notes                                                                              |
| ------------ | ------- | -------- | ---------------------------------------------------------------------------------- |
| `file`       | file    | Yes      | Allowed images: `.jpg`, `.jpeg`, `.png`, `.webp`; videos: `.mp4`, `.webm`, `.mov`. |
| `media_type` | string  | Yes      | `image` or `video`.                                                                |
| `sort_order` | integer | No       | Defaults to `0`.                                                                   |
| `is_primary` | boolean | No       | Defaults to `false`.                                                               |

Storage settings are environment-configurable: `CAR_MEDIA_UPLOAD_DIR` (default `uploads/cars`), `CAR_MEDIA_MAX_BYTES` (default 20 MB), and `CAR_MEDIA_MAX_COUNT` (default 20). Responses return a public application URL such as `/uploads/cars/123/<generated-file-name>`, never the filesystem path.

Reorder body:

```json
{
  "media": [
    { "id": 10, "sort_order": 0 },
    { "id": 11, "sort_order": 1 }
  ]
}
```

Every supplied media ID must belong to the requested car and may appear only once.

## Car Feature APIs

| Method | Path                                      | Access | Description             |
| ------ | ----------------------------------------- | ------ | ----------------------- |
| GET    | `/v1/cars/{car_id}/features`              | Owner  | List car features.      |
| POST   | `/v1/cars/{car_id}/features`              | Owner  | Add a feature.          |
| PATCH  | `/v1/cars/{car_id}/features/{feature_id}` | Owner  | Partial feature update. |
| DELETE | `/v1/cars/{car_id}/features/{feature_id}` | Owner  | Delete a feature.       |

```json
{
  "feature_name": "Sunroof",
  "feature_value": "Panoramic"
}
```

Feature names are required, limited to 150 characters, and cannot be duplicated for the same car.

## Admin Car APIs

| Method | Path                               | Access | Description                                                       |
| ------ | ---------------------------------- | ------ | ----------------------------------------------------------------- |
| GET    | `/v1/admin/cars`                   | Admin  | Paginated list of all active cars.                                |
| GET    | `/v1/admin/cars/{car_id}`          | Admin  | Full car, owner summary, catalog, media, and features.            |
| POST   | `/v1/admin/cars/{car_id}/approve`  | Admin  | Approve and verify an eligible car.                               |
| POST   | `/v1/admin/cars/{car_id}/reject`   | Admin  | Reject car and persist a mandatory reason.                        |
| POST   | `/v1/admin/cars/{car_id}/verify`   | Admin  | Verify/approve a car.                                             |
| POST   | `/v1/admin/cars/{car_id}/unverify` | Admin  | Remove verification and return approved cars to pending approval. |

Admin list filters: `page`, `limit`, `search`, `owner_id`, `brand_id`, `model_id`, `variant_id`, `city`, `state`, `fuel_type`, `transmission`, `verification_status`, and `status`.

Reject body:

```json
{
  "reason": "Vehicle registration information could not be verified."
}
```

Approval lifecycle:

```text
pending_approval -> approved -> published
        |              |
        +-> rejected   +-> pending_approval after material car changes
```

Approval stores `is_verified`, `approval_status`, `verified_at`, `verified_by_id`, and (for rejection) `rejection_reason`.

## Listings

A car is the physical vehicle; a listing is its sale advertisement. One non-deleted listing is allowed per car.

| Method | Path                                  | Access | Description                                          |
| ------ | ------------------------------------- | ------ | ---------------------------------------------------- |
| POST   | `/v1/cars/{car_id}/listing`           | Owner  | Create a draft listing.                              |
| GET    | `/v1/cars/{car_id}/listing`           | Owner  | Read own listing.                                    |
| PATCH  | `/v1/cars/{car_id}/listing`           | Owner  | Partial update own listing.                          |
| DELETE | `/v1/cars/{car_id}/listing`           | Owner  | Soft-delete own listing.                             |
| POST   | `/v1/cars/{car_id}/listing/publish`   | Owner  | Publish only when the car is approved and verified.  |
| POST   | `/v1/cars/{car_id}/listing/unpublish` | Owner  | Return listing to draft.                             |
| GET    | `/v1/listings`                        | Public | Browse active listings of verified cars.             |
| GET    | `/v1/listings/{listing_id}`           | Public | Read an active listing and increment its view count. |

Create body:

```json
{
  "listing_type": "sale",
  "title": "2022 Toyota Fortuner 4x4 Diesel AT",
  "description": "Single-owner, service history available.",
  "asking_price": 3200000,
  "negotiable": true,
  "expiry_date": "2027-01-31T23:59:59"
}
```

Public listing filters: `page`, `limit`, `brand_id`, `model_id`, `variant_id`, `fuel_type`, `transmission`, `city`, `state`, `min_price`, `max_price`, `min_year`, `max_year`, `min_mileage`, `max_mileage`, and `condition`.

## Favorites

| Method | Path                         | Access | Description                        |
| ------ | ---------------------------- | ------ | ---------------------------------- |
| POST   | `/v1/cars/{car_id}/favorite` | User   | Save an active car once.           |
| DELETE | `/v1/cars/{car_id}/favorite` | User   | Remove saved car.                  |
| GET    | `/v1/users/me/favorites`     | User   | List the current user's favorites. |

Adding the same car twice returns `409 Conflict`.

## End-to-End Workflow

1. Admin creates active brand, model, and variant records.
2. Seller creates a car using the variant ID.
3. Seller adds vehicle features and media.
4. Admin reviews the car and approves or rejects it.
5. Seller creates a draft listing for an approved car.
6. Seller publishes the verified listing.
7. Buyers browse public listings and optionally favorite cars.

## Running and Maintaining

Start the API:

```powershell
python run.py
```

The approval lifecycle migration has already been applied to the local database. For another database or environment, run:

```powershell
python scripts\migrate_car_management.py
```

Run this before deploying code that expects the `approval_status`, `rejection_reason`, `verified_at`, and `verified_by_id` columns.
