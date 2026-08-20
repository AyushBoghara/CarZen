# Car Selling, Reselling, Service and Resale Price Prediction System

## 1. Problem Definition

The existing process of buying, selling, reselling, and servicing cars is often dependent on manual searches, individual dealers, classified advertisements, and personal estimation of vehicle prices. Buyers may find it difficult to determine whether a car is fairly priced, while sellers may not know the appropriate resale value of their vehicle.

There is also a lack of an integrated platform that combines **car buying, car selling, car reselling, vehicle service information, and resale-price prediction** in a single system.

The proposed system aims to develop a web-based car management and marketplace platform that allows users to list cars for sale, search and compare available cars, manage resale information, access service-related information, and estimate the expected resale price of a vehicle using a machine-learning-based prediction system.

The backend of the system will be developed using **Python and FastAPI**, while **MySQL** will be used to store user, vehicle, selling, reselling, service, and prediction-related information.

---

## 2. Objective of the New System

The main objective of the proposed system is to develop an integrated platform for car selling, buying, reselling, servicing, and resale-price prediction.

### Specific Objectives

1. To provide a platform for users to buy and sell used and new cars.
2. To allow sellers to create and manage car listings.
3. To allow buyers to search and filter cars according to their requirements.
4. To provide detailed information about available vehicles.
5. To support car reselling by maintaining vehicle and ownership information.
6. To provide information related to vehicle servicing and maintenance.
7. To predict the estimated resale price of a car using machine learning.
8. To store system data securely using a MySQL database.
9. To provide REST APIs using FastAPI for communication between the frontend and backend.
10. To provide an admin module for managing users, cars, services, and listings.
11. To reduce the difficulty involved in estimating the market value of used cars.
12. To improve transparency between buyers and sellers.

---

## 3. Core Components

The proposed system consists of the following major components:

### 3.1 User Management

This component manages user registration, login, profiles, authentication, and user information.

### 3.2 Car Management

This component manages vehicle information such as:

- Car brand
- Car model
- Manufacturing year
- Registration year
- Fuel type
- Transmission
- Mileage
- Engine capacity
- Number of owners
- Vehicle condition
- Location
- Expected price
- Selling status

### 3.3 Car Selling Module

Sellers can add vehicles to the platform and provide information about the car. They can update or remove their listings.

### 3.4 Car Buying/Search Module

Buyers can search for available vehicles and apply filters based on price, brand, model, fuel type, year, mileage, location, and other characteristics.

### 3.5 Reselling Module

The reselling module manages vehicles that are being sold again by their current owners. It can maintain previous ownership, purchase information, vehicle history, and resale information.

### 3.6 Car Service Module

The service module maintains vehicle-service-related information such as:

- Service type
- Service date
- Service cost
- Service center
- Maintenance details
- Next service date
- Vehicle service history

### 3.7 Resale Price Prediction Module

This module estimates the expected resale value of a vehicle based on relevant vehicle characteristics.

Possible prediction factors include:

- Brand
- Model
- Manufacturing year
- Vehicle age
- Mileage
- Fuel type
- Transmission
- Number of previous owners
- Engine capacity
- Vehicle condition
- Location
- Previous selling price

### 3.8 Admin Module

The administrator can manage:

- Users
- Car listings
- Reselling records
- Service information
- Prediction records
- Categories
- Reported listings
- System data

### 3.9 FastAPI Backend

FastAPI will act as the backend framework and provide RESTful APIs for communication between the frontend, database, authentication system, car modules, service modules, and prediction system.

### 3.10 MySQL Database

MySQL will be used as the primary relational database for storing and managing application data.

---

## 4. Project Profile

| Item              | Description                                                             |
| ----------------- | ----------------------------------------------------------------------- |
| Project Name      | Car Selling, Reselling, Service and Resale Price Prediction System      |
| Project Type      | Web-Based Application                                                   |
| Domain            | Automobile / E-Commerce / Machine Learning                              |
| Frontend          | Web-based User Interface                                                |
| Backend           | Python                                                                  |
| Backend Framework | FastAPI                                                                 |
| Database          | MySQL                                                                   |
| Prediction        | Machine Learning                                                        |
| API Architecture  | REST API                                                                |
| Main Users        | Buyers, Sellers, Car Owners, Service Users, Admin                       |
| Main Purpose      | Car Buying, Selling, Reselling, Service Management and Price Prediction |

The project combines **automobile marketplace functionality with machine learning-based price prediction** to provide a centralized platform for vehicle transactions and management.

---

## 5. Need of the New System

The proposed system is needed because traditional car-buying and selling processes have several limitations.

### Major Reasons

1. **Difficulty in determining the correct car price**\
   Users may not know the actual market value of a used vehicle.

2. **Lack of centralized information**\
   Car information, selling information, and service records may be available through different sources.

3. **Manual price estimation**\
   Resale prices are often estimated manually based on personal experience.

4. **Difficulty in finding suitable cars**\
   Buyers need an efficient search and filtering mechanism.

5. **Limited vehicle history information**\
   Previous ownership and service information may not be easily available.

6. **Lack of integrated service management**\
   Vehicle service information is often maintained separately.

7. **Increasing used-car market**\
   More people are purchasing and reselling used vehicles, increasing the need for an organized platform.

8. **Need for data-driven prediction**\
   Machine learning can help estimate resale prices based on historical vehicle data.

---

## 6. Scope of the New System

The system will cover the following areas:

### Buyer Scope

- User registration and login
- Search cars
- Filter cars
- View car details
- Compare available vehicles
- Check expected resale price
- View seller information
- View service information

### Seller Scope

- Register as a seller
- Add car listings
- Upload vehicle information
- Set selling price
- Update listings
- Remove listings
- Manage selling status

### Reselling Scope

- Add resale vehicle
- Maintain ownership information
- Maintain previous purchase details
- Estimate resale price
- List vehicle for resale
- Maintain resale history

### Service Scope

- Add service records
- View service history
- Maintain service dates
- Maintain service costs
- Track maintenance information

### Prediction Scope

The machine learning module will estimate the expected resale price using historical and current vehicle attributes.

### Admin Scope

- Manage users
- Manage vehicles
- Manage listings
- Manage service records
- Manage prediction data
- Manage reported content
- Monitor system activity

---

## 7. Advantages and Limitations of the Proposed System

### Advantages

1. Provides a centralized platform for car buying and selling.
2. Supports both selling and reselling of vehicles.
3. Helps users estimate the expected resale price.
4. Reduces manual price estimation.
5. Provides vehicle search and filtering.
6. Maintains vehicle and service information.
7. Provides structured data management through MySQL.
8. FastAPI provides a lightweight and efficient backend API.
9. Machine learning provides data-driven price estimation.
10. Helps buyers make better purchasing decisions.
11. Helps sellers determine a reasonable asking price.
12. Provides an admin system for centralized management.

### Limitations

1. Prediction accuracy depends on the quality and quantity of training data.
2. Market prices can change because of demand, location, and economic conditions.
3. The predicted price may differ from the actual selling price.
4. Incorrect vehicle information can affect prediction accuracy.
5. Vehicle physical condition may be difficult to represent completely through numerical data.
6. Initial implementation may have limited service-center coverage.
7. The system requires reliable internet connectivity.
8. The prediction model may require periodic retraining with updated market data.
9. Fraudulent or inaccurate seller-provided information may affect the reliability of listings.

---

## 8. Proposed Timeline Chart

| Phase    | Activities                          | Duration |
| -------- | ----------------------------------- | -------- |
| Phase 1  | Requirement Analysis                | Week 1   |
| Phase 2  | System Analysis and Planning        | Week 2   |
| Phase 3  | Database Design using MySQL         | Week 3   |
| Phase 4  | System and API Design               | Week 4   |
| Phase 5  | User and Authentication Module      | Week 5   |
| Phase 6  | Car Buying and Selling Module       | Week 6   |
| Phase 7  | Reselling Module                    | Week 7   |
| Phase 8  | Car Service Module                  | Week 8   |
| Phase 9  | Dataset Preparation and ML Model    | Week 9   |
| Phase 10 | Resale Price Prediction Integration | Week 10  |
| Phase 11 | Testing and Bug Fixing              | Week 11  |
| Phase 12 | Documentation and Final Deployment  | Week 12  |

### Timeline Representation

| Activity                 | W1 | W2 | W3 | W4 | W5 | W6 | W7 | W8 | W9 | W10 | W11 | W12 |
| ------------------------ | -- | -- | -- | -- | -- | -- | -- | -- | -- | --- | --- | --- |
| Requirement Analysis     | ✓  |    |    |    |    |    |    |    |    |     |     |     |
| System Analysis          |    | ✓  |    |    |    |    |    |    |    |     |     |     |
| MySQL Database Design    |    |    | ✓  |    |    |    |    |    |    |     |     |     |
| System/API Design        |    |    |    | ✓  |    |    |    |    |    |     |     |     |
| User Module              |    |    |    |    | ✓  |    |    |    |    |     |     |     |
| Selling/Buying Module    |    |    |    |    |    | ✓  |    |    |    |     |     |     |
| Reselling Module         |    |    |    |    |    |    | ✓  |    |    |     |     |     |
| Service Module           |    |    |    |    |    |    |    | ✓  |    |     |     |     |
| ML Model                 |    |    |    |    |    |    |    |    | ✓  |     |     |     |
| Prediction Integration   |    |    |    |    |    |    |    |    |    | ✓   |     |     |
| Testing                  |    |    |    |    |    |    |    |    |    |     | ✓   |     |
| Documentation/Deployment |    |    |    |    |    |    |    |    |    |     |     | ✓   |

---

## 9. Targeted Users

The proposed system targets the following users:

### 9.1 Buyers

Users who want to search for and purchase new or used cars.

### 9.2 Sellers

Individuals or businesses that want to sell their vehicles through the platform.

### 9.3 Car Resellers/Dealers

Dealers and resellers who regularly purchase and sell used vehicles.

### 9.4 Car Owners

Vehicle owners who want to maintain service records and determine the expected resale value of their vehicle.

### 9.5 Service Providers

Authorized or independent service centers that provide vehicle maintenance services.

### 9.6 Administrator

The administrator manages users, vehicle listings, services, transactions-related records, and overall system operations.

---

# 10. Requirement Determination and Analysis

Requirement determination identifies what the proposed system needs to accomplish and what resources are required to develop and operate it.

The requirements are divided into:

1. Functional requirements
2. Non-functional requirements
3. Hardware requirements
4. Software requirements
5. Database requirements
6. Machine-learning requirements

### 10.1 Functional Requirements

The system should provide:

- User registration
- User login
- User profile management
- Car listing creation
- Car listing modification
- Car listing deletion
- Car search
- Car filtering
- Car details
- Selling functionality
- Reselling functionality
- Service record management
- Resale price prediction
- Admin management
- Database management
- API-based communication

### 10.2 Non-Functional Requirements

#### Performance

The system should respond to user requests efficiently and should be capable of handling multiple API requests.

#### Security

The system should protect user accounts and sensitive information through authentication and authorization mechanisms.

#### Reliability

The system should maintain consistent data and minimize failures during normal operation.

#### Scalability

The system should allow additional vehicles, users, service centers, and prediction records to be added as the system grows.

#### Usability

The user interface should be simple and understandable for buyers, sellers, and administrators.

#### Maintainability

The backend should be organized into separate modules so that future changes can be implemented easily.

---

# 11. Requirement Determination

### 11.1 Hardware Requirements

#### Development System

- Processor: Intel Core i5 / AMD Ryzen 5 or higher
- RAM: Minimum 8 GB
- Storage: Minimum 256 GB SSD
- Network: Internet connection
- Display: Standard HD display

#### Server Requirements

The production server requirements will depend on the number of users and API requests. A cloud or dedicated server can be used for deployment.

### 11.2 Software Requirements

| Component               | Technology                 |
| ----------------------- | -------------------------- |
| Programming Language    | Python                     |
| Backend Framework       | FastAPI                    |
| Database                | MySQL                      |
| API                     | REST API                   |
| Machine Learning        | Python ML libraries        |
| Database Connectivity   | Python Database Driver/ORM |
| Operating System        | Windows/Linux              |
| API Testing             | Postman                    |
| Development Environment | VS Code / PyCharm          |
| Version Control         | Git/GitHub                 |

---

# 12. Requirement Specification

## 12.1 User Requirements

Users should be able to:

- Register an account.
- Log in securely.
- Manage their profile.
- Search for cars.
- Filter cars.
- View car details.
- Add cars for sale.
- Manage their listings.
- View resale information.
- Enter vehicle information for price prediction.
- View predicted resale price.
- View vehicle service information.

## 12.2 Seller Requirements

Sellers should be able to:

- Add vehicle details.
- Upload vehicle information/images.
- Specify selling price.
- Update vehicle details.
- Change listing status.
- Remove their listing.
- View their listed vehicles.

## 12.3 Reseller Requirements

Resellers should be able to:

- Add vehicles for resale.
- Maintain purchase information.
- Maintain resale information.
- Check predicted resale value.
- Manage multiple vehicle listings.

## 12.4 Service Requirements

The system should allow service-related information to be recorded, including:

- Vehicle
- Service type
- Service date
- Service cost
- Service center
- Maintenance description
- Next service date

## 12.5 Prediction Requirements

The prediction system should accept vehicle characteristics and provide an estimated resale price.

Example input attributes:

- Brand
- Model
- Year
- Mileage
- Fuel type
- Transmission
- Engine
- Number of owners
- Condition
- Location

The output will be an **estimated resale price**.

## 12.6 Administrator Requirements

The administrator should be able to:

- Manage users.
- Manage cars.
- Manage sellers.
- Manage listings.
- Manage service information.
- Monitor prediction records.
- Remove inappropriate listings.
- View system information.

---

# 13. System Design

The proposed system follows a layered architecture.

### 13.1 Architecture

**User → Frontend → FastAPI Backend → Business Logic → MySQL Database**

For prediction:

**User → Frontend → FastAPI → Prediction Module → ML Model → Predicted Resale Price**

### 13.2 Main System Modules

```text
Car Selling & Reselling System
│
├── User Management
│   ├── Registration
│   ├── Login
│   └── Profile
│
├── Car Management
│   ├── Add Car
│   ├── Update Car
│   ├── Search Car
│   └── Car Details
│
├── Selling Module
│   ├── Create Listing
│   ├── Manage Listing
│   └── Selling Status
│
├── Reselling Module
│   ├── Resale Listing
│   ├── Ownership History
│   └── Resale Information
│
├── Service Module
│   ├── Service Records
│   ├── Maintenance
│   └── Service History
│
├── Price Prediction
│   ├── Vehicle Input
│   ├── ML Model
│   └── Predicted Price
│
└── Admin Module
    ├── User Management
    ├── Car Management
    ├── Listing Management
    └── System Management
```

---

## 13.3 MySQL Database Design

The proposed MySQL database can contain the following major tables:

### Users Table

Stores user account information.

**Important fields:**

- user\_id
- name
- email
- phone
- password/authentication information
- user\_type
- created\_at

### Cars Table

Stores vehicle information.

**Important fields:**

- car\_id
- brand
- model
- manufacturing\_year
- registration\_year
- fuel\_type
- transmission
- mileage
- engine\_capacity
- owner\_count
- condition
- location

### Listings Table

Stores cars currently listed for sale.

**Important fields:**

- listing\_id
- car\_id
- seller\_id
- listing\_type
- asking\_price
- listing\_status
- listed\_date

### Ownership History Table

Stores previous ownership information.

**Important fields:**

- ownership\_id
- car\_id
- owner\_id
- purchase\_date
- sale\_date
- purchase\_price
- sale\_price

### Service Records Table

Stores vehicle maintenance information.

**Important fields:**

- service\_id
- car\_id
- service\_center
- service\_type
- service\_date
- service\_cost
- description
- next\_service\_date

### Prediction Records Table

Stores resale-price prediction information.

**Important fields:**

- prediction\_id
- car\_id
- predicted\_price
- prediction\_date
- model\_version

### Admin Table

Stores administrator information and administrative access details.

---

# 14. Use Case Diagram

The main actors of the system are:

1. **Buyer**
2. **Seller**
3. **Car Reseller**
4. **Service Provider**
5. **Administrator**

### Use Case Diagram Structure

```text
                         ┌─────────────────────────┐
                         │   Car Selling &          │
                         │   Reselling System       │
                         └─────────────────────────┘

 Buyer ────────────────► │ Register / Login         │
 Buyer ────────────────► │ Search Cars             │
 Buyer ────────────────► │ Filter Cars             │
 Buyer ────────────────► │ View Car Details        │
 Buyer ────────────────► │ View Service History    │
 Buyer ────────────────► │ Predict Resale Price    │
 Buyer ────────────────► │ Purchase/Contact Seller │
                         │                         │
 Seller ───────────────► │ Login                   │
 Seller ───────────────► │ Add Car Listing         │
 Seller ───────────────► │ Update Listing          │
 Seller ───────────────► │ Delete Listing          │
 Seller ───────────────► │ Manage Selling Status   │
 Seller ───────────────► │ Predict Resale Price    │
                         │                         │
 Reseller ─────────────► │ Add Resale Vehicle     │
 Reseller ─────────────► │ Manage Resale Listing  │
 Reseller ─────────────► │ View Vehicle History   │
 Reseller ─────────────► │ Predict Resale Price   │
                         │                         │
 Service Provider ─────► │ Add Service Record      │
 Service Provider ─────► │ Update Service Record   │
 Service Provider ─────► │ View Service History   │
                         │                         │
 Admin ─────────────────►│ Manage Users            │
 Admin ─────────────────►│ Manage Cars             │
 Admin ─────────────────►│ Manage Listings         │
 Admin ─────────────────►│ Manage Services        │
 Admin ─────────────────►│ Manage System Data     │
                         └─────────────────────────┘
```

### Use Case Summary

| Actor            | Main Use Cases                                                                                  |
| ---------------- | ----------------------------------------------------------------------------------------------- |
| Buyer            | Register, Login, Search Cars, Filter Cars, View Details, View Service History, Price Prediction |
| Seller           | Register, Login, Add Car, Update Listing, Delete Listing, Manage Selling Status                 |
| Reseller         | Add Resale Car, Manage Resale Listing, View Vehicle History, Price Prediction                   |
| Service Provider | Add Service Record, Update Service Record, Manage Service History                               |
| Admin            | Manage Users, Cars, Listings, Services, Predictions and System Data                             |

## Overall System Flow

```text
                 ┌──────────────┐
                 │    Users     │
                 └──────┬───────┘
                        │
                        ▼
                ┌───────────────┐
                │   Frontend    │
                └───────┬───────┘
                        │
                        ▼
                ┌───────────────┐
                │    FastAPI    │
                │    Backend    │
                └───────┬───────┘
                        │
             ┌──────────┴──────────┐
             │                     │
             ▼                     ▼
      ┌──────────────┐      ┌──────────────┐
      │   Business   │      │ ML Prediction│
      │    Logic     │      │    Module    │
      └──────┬───────┘      └──────────────┘
             │
             ▼
       ┌──────────────┐
       │    MySQL     │
       │   Database   │
       └──────────────┘
```

The proposed system therefore combines **car marketplace functionality, vehicle reselling, service-history management, MySQL-based data management, and machine-learning-based resale price prediction** into one integrated application.
