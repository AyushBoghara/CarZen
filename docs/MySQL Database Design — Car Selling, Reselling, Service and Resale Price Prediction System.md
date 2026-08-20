# 13.3 Database Design Using MySQL

The proposed system uses **MySQL** as the relational database management system. The database is designed using a normalized relational structure to store user information, vehicle details, car listings, ownership history, service records, inquiries, favorites, and machine-learning-based resale price predictions.

The database uses **Primary Keys (PK)** to uniquely identify records and **Foreign Keys (FK)** to establish relationships between related tables.

## 13.3.1 Database Name

**Database Name:** `car_marketplace_db`

---

# 13.3.2 Main Database Tables

The proposed database contains the following tables:

| No. | Table Name | Purpose |
|---:|---|---|
| 1 | `users` | Stores buyer, seller, reseller and other user accounts |
| 2 | `user_addresses` | Stores user location/address information |
| 3 | `car_brands` | Stores car manufacturer/brand information |
| 4 | `car_models` | Stores car model information |
| 5 | `cars` | Stores complete vehicle information |
| 6 | `car_images` | Stores images associated with vehicles |
| 7 | `listings` | Stores cars currently available for sale/resale |
| 8 | `ownership_history` | Stores vehicle ownership and purchase/sale history |
| 9 | `service_centers` | Stores service-center information |
| 10 | `service_records` | Stores vehicle maintenance/service history |
| 11 | `favorites` | Stores cars saved by users |
| 12 | `inquiries` | Stores buyer-seller communication/inquiry information |
| 13 | `transactions` | Stores completed vehicle sale/resale transaction information |
| 14 | `price_predictions` | Stores ML-based resale price prediction results |
| 15 | `admins` | Stores administrator information and administrative access |

---

# 13.3.3 Users Table

### Table Name: `users`

This table stores the basic information of all registered users.

| Field Name | Data Type | Constraint | Description |
|---|---|---|---|
| `user_id` | BIGINT | PK, AUTO_INCREMENT | Unique user ID |
| `first_name` | VARCHAR(50) | NOT NULL | User first name |
| `last_name` | VARCHAR(50) | NULL | User last name |
| `email` | VARCHAR(150) | UNIQUE, NOT NULL | User email address |
| `phone` | VARCHAR(20) | UNIQUE | User phone number |
| `password_hash` | VARCHAR(255) | NOT NULL | Encrypted/hashed password |
| `user_type` | ENUM | NOT NULL | Buyer/Seller/Reseller |
| `profile_image` | VARCHAR(500) | NULL | Profile image path/URL |
| `is_active` | BOOLEAN | DEFAULT TRUE | Account status |
| `created_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | Account creation date |
| `updated_at` | DATETIME | NULL | Last update date |
| `last_login_at` | DATETIME | NULL | Last login time |

### User Types

- Buyer
- Seller
- Reseller

A user can use the platform for buying, selling or reselling according to the functionality provided to that account.

---

# 13.3.4 User Addresses Table

### Table Name: `user_addresses`

This table stores user address and location information.

| Field Name | Data Type | Constraint | Description |
|---|---|---|---|
| `address_id` | BIGINT | PK, AUTO_INCREMENT | Unique address ID |
| `user_id` | BIGINT | FK, NOT NULL | Related user |
| `address_line1` | VARCHAR(255) | NOT NULL | Address |
| `address_line2` | VARCHAR(255) | NULL | Additional address |
| `city` | VARCHAR(100) | NOT NULL | City |
| `state` | VARCHAR(100) | NOT NULL | State |
| `pincode` | VARCHAR(10) | NOT NULL | Postal code |
| `country` | VARCHAR(100) | DEFAULT 'India' | Country |
| `is_default` | BOOLEAN | DEFAULT FALSE | Default address |
| `created_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | Creation date |

### Relationship

`users (1) → user_addresses (M)`

One user can have multiple addresses.

---

# 13.3.5 Car Brands Table

### Table Name: `car_brands`

This table stores car manufacturer information.

| Field Name | Data Type | Constraint | Description |
|---|---|---|---|
| `brand_id` | INT | PK, AUTO_INCREMENT | Unique brand ID |
| `brand_name` | VARCHAR(100) | UNIQUE, NOT NULL | Brand name |
| `country` | VARCHAR(100) | NULL | Manufacturer country |
| `logo_url` | VARCHAR(500) | NULL | Brand logo |
| `is_active` | BOOLEAN | DEFAULT TRUE | Brand status |
| `created_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | Creation date |

### Examples

- Maruti Suzuki
- Hyundai
- Tata
- Toyota
- Honda
- Mahindra
- Kia
- BMW
- Mercedes-Benz

---

# 13.3.6 Car Models Table

### Table Name: `car_models`

This table stores individual models belonging to car brands.

| Field Name | Data Type | Constraint | Description |
|---|---|---|---|
| `model_id` | INT | PK, AUTO_INCREMENT | Unique model ID |
| `brand_id` | INT | FK, NOT NULL | Related brand |
| `model_name` | VARCHAR(100) | NOT NULL | Model name |
| `variant` | VARCHAR(100) | NULL | Variant |
| `body_type` | VARCHAR(50) | NULL | Sedan/SUV/Hatchback etc. |
| `fuel_type` | VARCHAR(30) | NULL | Petrol/Diesel/CNG/EV/Hybrid |
| `transmission_type` | VARCHAR(30) | NULL | Manual/Automatic |
| `seating_capacity` | TINYINT | NULL | Number of seats |
| `is_active` | BOOLEAN | DEFAULT TRUE | Model status |
| `created_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | Creation date |

### Relationship

`car_brands (1) → car_models (M)`

One brand can have multiple car models.

---

# 13.3.7 Cars Table

### Table Name: `cars`

This is the **main vehicle table**. It stores the detailed information required for selling, reselling, searching and price prediction.

| Field Name | Data Type | Constraint | Description |
|---|---|---|---|
| `car_id` | BIGINT | PK, AUTO_INCREMENT | Unique vehicle ID |
| `model_id` | INT | FK, NOT NULL | Related car model |
| `registration_number` | VARCHAR(30) | UNIQUE | Vehicle registration number |
| `vin_number` | VARCHAR(100) | UNIQUE | Vehicle identification number |
| `manufacturing_year` | YEAR | NOT NULL | Manufacturing year |
| `registration_year` | YEAR | NULL | Registration year |
| `fuel_type` | VARCHAR(30) | NOT NULL | Fuel type |
| `transmission` | VARCHAR(30) | NOT NULL | Transmission type |
| `engine_cc` | DECIMAL(8,2) | NULL | Engine capacity |
| `mileage_km` | DECIMAL(12,2) | NOT NULL | Total kilometers driven |
| `horsepower` | DECIMAL(8,2) | NULL | Engine power |
| `seating_capacity` | TINYINT | NULL | Number of seats |
| `color` | VARCHAR(50) | NULL | Vehicle color |
| `owner_count` | TINYINT | DEFAULT 1 | Number of previous owners |
| `condition` | VARCHAR(30) | NOT NULL | Vehicle condition |
| `insurance_valid_until` | DATE | NULL | Insurance expiry |
| `insurance_type` | VARCHAR(50) | NULL | Insurance type |
| `rc_status` | VARCHAR(30) | NULL | Registration certificate status |
| `location_city` | VARCHAR(100) | NOT NULL | Vehicle city |
| `location_state` | VARCHAR(100) | NOT NULL | Vehicle state |
| `location_pincode` | VARCHAR(10) | NULL | Vehicle postal code |
| `description` | TEXT | NULL | Vehicle description |
| `created_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | Record creation |
| `updated_at` | DATETIME | NULL | Last update |

### Important ML Features

The following fields are particularly useful for resale-price prediction:

- `manufacturing_year`
- `registration_year`
- `fuel_type`
- `transmission`
- `engine_cc`
- `mileage_km`
- `owner_count`
- `condition`
- `location_city`
- `location_state`
- `model_id`

---

# 13.3.8 Car Images Table

### Table Name: `car_images`

This table stores multiple images for each vehicle.

| Field Name | Data Type | Constraint | Description |
|---|---|---|---|
| `image_id` | BIGINT | PK, AUTO_INCREMENT | Unique image ID |
| `car_id` | BIGINT | FK, NOT NULL | Related car |
| `image_url` | VARCHAR(500) | NOT NULL | Image location |
| `image_type` | VARCHAR(50) | NULL | Front/Rear/Interior/Side/etc. |
| `is_primary` | BOOLEAN | DEFAULT FALSE | Main vehicle image |
| `created_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | Upload date |

### Relationship

`cars (1) → car_images (M)`

One car can have multiple images.

---

# 13.3.9 Listings Table

### Table Name: `listings`

This table manages vehicles listed for sale or resale.

| Field Name | Data Type | Constraint | Description |
|---|---|---|---|
| `listing_id` | BIGINT | PK, AUTO_INCREMENT | Unique listing ID |
| `car_id` | BIGINT | FK, NOT NULL | Vehicle being listed |
| `seller_id` | BIGINT | FK, NOT NULL | User selling the vehicle |
| `listing_type` | ENUM | NOT NULL | SALE/RESALE |
| `asking_price` | DECIMAL(15,2) | NOT NULL | Seller asking price |
| `negotiable` | BOOLEAN | DEFAULT TRUE | Price negotiation option |
| `listing_status` | ENUM | NOT NULL | ACTIVE/SOLD/EXPIRED/REMOVED |
| `listed_date` | DATETIME | DEFAULT CURRENT_TIMESTAMP | Listing date |
| `expiry_date` | DATETIME | NULL | Listing expiry |
| `views_count` | INT | DEFAULT 0 | Number of views |
| `created_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | Creation date |
| `updated_at` | DATETIME | NULL | Last update |

### Listing Types

- SALE
- RESALE

---

# 13.3.10 Ownership History Table

### Table Name: `ownership_history`

This table maintains the complete ownership history of a vehicle.

| Field Name | Data Type | Constraint | Description |
|---|---|---|---|
| `ownership_id` | BIGINT | PK, AUTO_INCREMENT | Unique ownership record |
| `car_id` | BIGINT | FK, NOT NULL | Vehicle |
| `owner_id` | BIGINT | FK, NOT NULL | Owner |
| `ownership_start_date` | DATE | NOT NULL | Ownership start |
| `ownership_end_date` | DATE | NULL | Ownership end |
| `purchase_price` | DECIMAL(15,2) | NULL | Purchase price |
| `sale_price` | DECIMAL(15,2) | NULL | Sale price |
| `purchase_date` | DATE | NULL | Purchase date |
| `sale_date` | DATE | NULL | Sale date |
| `created_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | Record creation |

### Relationship

`cars (1) → ownership_history (M)`

One car can have multiple previous owners.

This table is especially important for the **reselling module** and **price prediction**.

---

# 13.3.11 Service Centers Table

### Table Name: `service_centers`

This table stores information about vehicle service centers.

| Field Name | Data Type | Constraint | Description |
|---|---|---|---|
| `service_center_id` | BIGINT | PK, AUTO_INCREMENT | Unique service center ID |
| `name` | VARCHAR(150) | NOT NULL | Service center name |
| `contact_person` | VARCHAR(100) | NULL | Contact person |
| `phone` | VARCHAR(20) | NULL | Contact number |
| `email` | VARCHAR(150) | NULL | Email |
| `address` | VARCHAR(255) | NULL | Address |
| `city` | VARCHAR(100) | NOT NULL | City |
| `state` | VARCHAR(100) | NOT NULL | State |
| `pincode` | VARCHAR(10) | NULL | Postal code |
| `rating` | DECIMAL(3,2) | NULL | Service center rating |
| `is_active` | BOOLEAN | DEFAULT TRUE | Service center status |
| `created_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | Creation date |

---

# 13.3.12 Service Records Table

### Table Name: `service_records`

This table stores the complete maintenance and service history of each vehicle.

| Field Name | Data Type | Constraint | Description |
|---|---|---|---|
| `service_id` | BIGINT | PK, AUTO_INCREMENT | Unique service record |
| `car_id` | BIGINT | FK, NOT NULL | Vehicle |
| `service_center_id` | BIGINT | FK, NULL | Service center |
| `service_type` | VARCHAR(100) | NOT NULL | Type of service |
| `service_date` | DATE | NOT NULL | Service date |
| `odometer_reading` | DECIMAL(12,2) | NULL | Mileage at service |
| `service_cost` | DECIMAL(12,2) | NULL | Service cost |
| `parts_cost` | DECIMAL(12,2) | NULL | Spare-parts cost |
| `labor_cost` | DECIMAL(12,2) | NULL | Labor cost |
| `description` | TEXT | NULL | Service details |
| `next_service_date` | DATE | NULL | Recommended next service |
| `next_service_mileage` | DECIMAL(12,2) | NULL | Recommended mileage |
| `created_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | Record creation |

### Examples of Service Types

- Oil Change
- General Service
- Brake Service
- Tyre Replacement
- Battery Replacement
- Engine Service
- AC Service
- Major Repair

---

# 13.3.13 Favorites Table

### Table Name: `favorites`

This table stores cars saved by users for future reference.

| Field Name | Data Type | Constraint | Description |
|---|---|---|---|
| `favorite_id` | BIGINT | PK, AUTO_INCREMENT | Unique favorite ID |
| `user_id` | BIGINT | FK, NOT NULL | User |
| `car_id` | BIGINT | FK, NOT NULL | Saved car |
| `created_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | Date saved |

### Relationship

`users (1) → favorites (M)`

`cars (1) → favorites (M)`

A user can save multiple cars.

---

# 13.3.14 Inquiries Table

### Table Name: `inquiries`

This table stores communication or inquiries made by buyers regarding a vehicle.

| Field Name | Data Type | Constraint | Description |
|---|---|---|---|
| `inquiry_id` | BIGINT | PK, AUTO_INCREMENT | Unique inquiry ID |
| `listing_id` | BIGINT | FK, NOT NULL | Related listing |
| `buyer_id` | BIGINT | FK, NOT NULL | Buyer |
| `seller_id` | BIGINT | FK, NOT NULL | Seller |
| `message` | TEXT | NOT NULL | Inquiry message |
| `status` | ENUM | DEFAULT 'OPEN' | Inquiry status |
| `created_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | Inquiry date |
| `updated_at` | DATETIME | NULL | Last update |

### Inquiry Status

- OPEN
- RESPONDED
- CLOSED

---

# 13.3.15 Transactions Table

### Table Name: `transactions`

This table stores completed vehicle purchase and sale transactions.

| Field Name | Data Type | Constraint | Description |
|---|---|---|---|
| `transaction_id` | BIGINT | PK, AUTO_INCREMENT | Unique transaction ID |
| `listing_id` | BIGINT | FK, NOT NULL | Related listing |
| `car_id` | BIGINT | FK, NOT NULL | Vehicle |
| `buyer_id` | BIGINT | FK, NOT NULL | Buyer |
| `seller_id` | BIGINT | FK, NOT NULL | Seller |
| `transaction_price` | DECIMAL(15,2) | NOT NULL | Final selling price |
| `transaction_date` | DATETIME | NOT NULL | Transaction date |
| `payment_status` | ENUM | NOT NULL | Payment status |
| `transaction_status` | ENUM | NOT NULL | Transaction status |
| `created_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | Record creation |

### Payment Status

- PENDING
- PARTIAL
- PAID
- FAILED

### Transaction Status

- INITIATED
- COMPLETED
- CANCELLED

The `transaction_price` is also valuable historical data for the **ML resale-price prediction model**.

---

# 13.3.16 Price Predictions Table

### Table Name: `price_predictions`

This table stores the output of the machine-learning resale-price prediction system.

| Field Name | Data Type | Constraint | Description |
|---|---|---|---|
| `prediction_id` | BIGINT | PK, AUTO_INCREMENT | Unique prediction ID |
| `car_id` | BIGINT | FK, NULL | Existing vehicle |
| `user_id` | BIGINT | FK, NOT NULL | User requesting prediction |
| `predicted_price` | DECIMAL(15,2) | NOT NULL | Predicted resale price |
| `min_price` | DECIMAL(15,2) | NULL | Lower estimated range |
| `max_price` | DECIMAL(15,2) | NULL | Upper estimated range |
| `model_name` | VARCHAR(100) | NOT NULL | ML model name |
| `model_version` | VARCHAR(50) | NULL | Model version |
| `confidence_score` | DECIMAL(5,2) | NULL | Prediction confidence |
| `prediction_input` | JSON | NOT NULL | Input features used |
| `prediction_date` | DATETIME | DEFAULT CURRENT_TIMESTAMP | Prediction date |

### Example Prediction

A user enters:

- Brand: Hyundai
- Model: Creta
- Year: 2022
- Mileage: 35,000 km
- Fuel: Petrol
- Transmission: Automatic
- Owners: 1
- Condition: Good

The ML system generates:

**Estimated Resale Price: ₹12,50,000**

The prediction result is stored in the `price_predictions` table.

---

# 13.3.17 Admin Table

### Table Name: `admins`

This table stores administrator-specific information.

| Field Name | Data Type | Constraint | Description |
|---|---|---|---|
| `admin_id` | BIGINT | PK, AUTO_INCREMENT | Unique admin ID |
| `user_id` | BIGINT | FK, UNIQUE, NOT NULL | Related user |
| `role` | ENUM | NOT NULL | Admin role |
| `is_active` | BOOLEAN | DEFAULT TRUE | Admin status |
| `created_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | Creation date |
| `updated_at` | DATETIME | NULL | Last update |

### Admin Roles

- SUPER_ADMIN
- ADMIN
- MODERATOR

---

# 13.3.18 Database Relationships

The major relationships between the tables are:

```text
users
  │
  ├──────────────► user_addresses
  │
  ├──────────────► listings
  │                    │
  │                    └──────────► inquiries
  │
  ├──────────────► favorites
  │
  ├──────────────► transactions
  │
  └──────────────► price_predictions


car_brands
    │
    └──────────────► car_models
                         │
                         └──────────────► cars
                                           │
              ┌────────────────────────────┼────────────────────┐
              │                            │                    │
              ▼                            ▼                    ▼
        car_images                  service_records      ownership_history
                                           │
                                           ▼
                                   service_centers

cars
  │
  ├──────────────► listings
  │
  ├──────────────► favorites
  │
  ├──────────────► transactions
  │
  └──────────────► price_predictions
```

---

# 13.3.19 Entity Relationship Structure

### User Relationships

```text
USER
 │
 ├──< USER_ADDRESS
 │
 ├──< LISTING
 │
 ├──< FAVORITE
 │
 ├──< INQUIRY
 │
 ├──< TRANSACTION
 │
 └──< PRICE_PREDICTION
```

### Vehicle Relationships

```text
CAR_BRAND
    │
    └──< CAR_MODEL
             │
             └──< CAR
                    │
                    ├──< CAR_IMAGE
                    ├──< LISTING
                    ├──< OWNERSHIP_HISTORY
                    ├──< SERVICE_RECORD
                    ├──< FAVORITE
                    ├──< TRANSACTION
                    └──< PRICE_PREDICTION
```

---

# 13.3.20 Primary Key and Foreign Key Summary

| Table | Primary Key | Important Foreign Keys |
|---|---|---|
| `users` | `user_id` | — |
| `user_addresses` | `address_id` | `user_id` |
| `car_brands` | `brand_id` | — |
| `car_models` | `model_id` | `brand_id` |
| `cars` | `car_id` | `model_id` |
| `car_images` | `image_id` | `car_id` |
| `listings` | `listing_id` | `car_id`, `seller_id` |
| `ownership_history` | `ownership_id` | `car_id`, `owner_id` |
| `service_centers` | `service_center_id` | — |
| `service_records` | `service_id` | `car_id`, `service_center_id` |
| `favorites` | `favorite_id` | `user_id`, `car_id` |
| `inquiries` | `inquiry_id` | `listing_id`, `buyer_id`, `seller_id` |
| `transactions` | `transaction_id` | `listing_id`, `car_id`, `buyer_id`, `seller_id` |
| `price_predictions` | `prediction_id` | `car_id`, `user_id` |
| `admins` | `admin_id` | `user_id` |

---

# 13.3.21 Database Design for Resale Price Prediction

The database is designed to preserve historical data that can later be used to train and improve the machine-learning model.

### Important Prediction Features

```text
Car Information
      │
      ├── Brand
      ├── Model
      ├── Manufacturing Year
      ├── Registration Year
      ├── Fuel Type
      ├── Transmission
      ├── Engine Capacity
      ├── Mileage
      ├── Owner Count
      ├── Condition
      └── Location
             │
             ▼
     Historical Sales Data
             │
             ▼
      Machine Learning Model
             │
             ▼
       Predicted Resale Price
```

The `transactions` table provides historical actual selling prices, while the `cars` table provides vehicle characteristics. These datasets can be combined to create the training dataset for the resale-price prediction model.

---

# 13.3.22 Recommended Database Normalization

The database follows the principles of **relational database normalization**, particularly:

### First Normal Form (1NF)

Each field contains a single atomic value, and repeating groups are avoided.

### Second Normal Form (2NF)

Non-key attributes depend on the complete primary key.

### Third Normal Form (3NF)

Non-key attributes depend on the primary key and not on other non-key attributes.

For example, brand information is separated from the `cars` table into:

```text
car_brands
     ↓
car_models
     ↓
cars
```

This avoids repeatedly storing the same brand and model information for every vehicle.

---

# 13.3.23 Final Database Module

The complete database architecture can therefore be represented as:

```text
                    CAR MARKETPLACE DATABASE
                              │
       ┌──────────────────────┼──────────────────────┐
       │                      │                      │
       ▼                      ▼                      ▼
   USER MODULE           VEHICLE MODULE         ADMIN MODULE
       │                      │                      │
       ├─ users               ├─ car_brands         └─ admins
       └─ user_addresses      ├─ car_models
                              ├─ cars
                              └─ car_images
                                     │
              ┌──────────────────────┼──────────────────────┐
              │                      │                      │
              ▼                      ▼                      ▼
          SELLING                 RESELLING              SERVICE
              │                      │                      │
              └─ listings            └─ ownership_history  ├─ service_centers
                                                           └─ service_records

                              │
              ┌───────────────┼────────────────┐
              │               │                │
              ▼               ▼                ▼
          FAVORITES        INQUIRIES       TRANSACTIONS
              │               │                │
              └───────────────┴────────────────┘
                              │
                              ▼
                    PRICE PREDICTION MODULE
                              │
                              ▼
                     price_predictions
```

## 13.3.24 Final Database Table List

The final MySQL database will contain **15 main tables**:

1. `users`
2. `user_addresses`
3. `car_brands`
4. `car_models`
5. `cars`
6. `car_images`
7. `listings`
8. `ownership_history`
9. `service_centers`
10. `service_records`
11. `favorites`
12. `inquiries`
13. `transactions`
14. `price_predictions`
15. `admins`

This database design supports the complete project lifecycle: **user registration → car listing → car search → buying/selling → reselling → ownership history → vehicle servicing → transaction history → resale-price prediction**.