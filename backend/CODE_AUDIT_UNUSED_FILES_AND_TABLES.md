# CarZen Code and SQL Table Audit

Audit date: 2026-09-17  
Scope: Python source under `app/`, registered FastAPI routes, SQLAlchemy models, Alembic files, and the connected `carzen_db` schema.

## How to read this report

* **Implemented** means the capability has a router registered in `app/main.py` and code that reads or writes its model.
* **Partial** means the code exists but a required workflow or a dedicated domain capability is missing.
* **Dormant** means a model/table is registered with SQLAlchemy but has no API router or service that uses it. Do not delete it until its intended product feature is confirmed.
* **Unused candidate** means static source search found no application reference outside the file itself or SQLAlchemy's model-registration import.

## Requested management modules

| # | Module | Status | Evidence and notes |
| --- | --- | --- | --- |
| 1 | User Management | Implemented | Authentication, registration, login, profile update, password change, soft deletion, and admin user/role/status controls are exposed by `app/api/v1/auth/auth.py` and `app/api/v1/users/users_management.py`. Uses `users`, `addresses`, and `contacts`. |
| 2 | Seller Management | Partial | Seller dashboard plus seller inquiry/message management are implemented in `app/api/v1/seller/`. Sellers are roles on `users`; there is no standalone seller profile, onboarding, or seller-specific table. |
| 3 | Buyer Management | Partial | Buyer discovery, recent views, favourites, inquiries/messages, purchase-history reads, and a dashboard are implemented in `app/api/v1/buyer/buyer.py`. Buyers are roles on `users`; there is no separate buyer profile table. Purchase history depends on the incomplete `transactions` workflow described below. |
| 4 | Car Management | Implemented | Cars, brand/model/variant catalog, media, features, seller CRUD, and admin approval/verification are implemented in `app/api/v1/car_management/cars.py` and `catalog.py`. |
| 5 | Listing Management | Implemented | Listing create/read/update/soft-delete, publish/unpublish, public search/filtering, and detail views are implemented in `app/api/v1/car_management/marketplace.py`. |
| 6 | Favorite Management | Implemented | Add, remove, and list favourite cars are implemented in `marketplace.py`; buyer discovery also exposes interested cars. Uses `favorites`. |
| 7 | Order Management | Implemented | Buyer creation/cancellation, seller acceptance/rejection/status progression, and admin review/status controls are implemented in `app/api/v1/order/orders.py`. Uses `orders`. |
| 8 | Payment Management | Implemented | Razorpay order creation, signature verification, webhook handling, and payment retrieval are implemented in `app/api/v1/payment/payments.py` and `app/services/payments/payment_service.py`. It requires the Razorpay environment variables to be configured. |
| 9 | Notification Management | Implemented | List, unread list, mark one/all read, and deletion are implemented in `app/api/v1/notification/notifications.py`; other services create notifications. Uses `notifications`. |
| 10 | Admin Management | Partial | Admin registration/profile management, user moderation, car/catalog moderation, order oversight, and report moderation exist. There is no standalone admin model or admin dashboard; administration is role-based through `users.role`. |

## Active SQL tables

The following application tables are present in both SQLAlchemy metadata and the connected `carzen_db` database, and are used by an active router or service.

| Area | Tables |
| --- | --- |
| Identity and contact | `users`, `addresses`, `contacts` |
| Car catalog and inventory | `car_brands`, `car_models`, `car_variants`, `cars`, `car_media`, `car_features` |
| Marketplace and buyer activity | `listings`, `favorites`, `listing_views`, `inquiries`, `inquiry_messages` |
| Transaction workflow | `orders`, `payments` |
| Cross-cutting features | `notifications`, `reports` |

`alembic_version` is also present in the database. It is Alembic's migration-tracking table and must be retained.

## Dormant or incomplete SQL tables

These tables exist in the database and are registered by `app/models/__init__.py`, but they have no complete product workflow in the current codebase.

| Tables | Source files | Classification | Static audit result |
| --- | --- | --- | --- |
| `service_centers`, `service_records`, `service_items` | `app/models/service_centers.py`, `app/models/service_records.py`, `app/models/service_items.py`, `app/models/enums/ServiceEnums.py` | Dormant feature group | No router, schema, or service creates, reads, updates, or deletes service centres/records/items. Relationships alone do not implement a service-management feature. |
| `reviews` | `app/models/reviews.py` | Dormant | No review router, schema, or service exists. |
| `price_predictions`, `prediction_features` | `app/models/price_predictions.py`, `app/models/prediction_features.py`, `app/models/enums/PredictionEnums.py` | Dormant feature group | No prediction router, schema, service, or model invocation exists. |
| `transactions` | `app/models/transactions.py` | Incomplete, not unused | Buyer purchase endpoints query this table, but no code constructs `Transactions(...)` or updates its state. Orders and payments use `orders` and `payments` instead, so buyer purchase history will remain empty unless another system writes rows directly. |

## Unused file candidates

These are the only source files with no static application usage outside their own definition. They are candidates for removal after a product-owner check.

| File | Why it is a candidate |
| --- | --- |
| `app/exceptions/customException.py` | No import or use was found. Authentication uses `app/exceptions/authExceptions.py` instead. |
| `app/models/enums/Country.py` | No import or use was found. Country fields in the current models use strings. |

## Important implementation gaps

1. **Transactions are disconnected from orders and payments.** Either create/update a `transactions` row as the order advances, or remove the buyer purchase endpoints and table if `orders` is the intended source of purchase history.
2. **Dormant tables should not be silently retained.** Decide whether service records, reviews, and price prediction are upcoming features. If not, remove their models, relationships, tables, and enum files in a dedicated migration.
3. **Migration coverage is incomplete.** `app/main.py` runs `Base.metadata.create_all()`, while Alembic only contains later incremental migrations. New environments can therefore receive schema changes outside Alembic history. Adopt Alembic as the single schema-management path before production.
4. **The ten modules are role-based, not separate account entities.** This is a sound simplification if users, buyers, sellers, and admins share one account profile. If each needs dedicated business data, add explicit profile tables and workflows.

## Database verification

The connected database contains 25 application tables plus `alembic_version`. The database table list matches the current SQLAlchemy model list; the removed `ownership_history` table is not present.

This audit is static: it identifies code reachability, not whether a table contains production data. Check row counts, backup requirements, and external consumers before dropping any table.
