import sys
import os
import json
from collections import defaultdict

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.main import app

openapi = app.openapi()
schemas = openapi.get("components", {}).get("schemas", {})

def resolve_ref(ref_str):
    name = ref_str.split("/")[-1]
    return schemas.get(name, {})

def get_schema_details(schema, depth=0):
    if depth > 5:
        return schema
    if "$ref" in schema:
        return get_schema_details(resolve_ref(schema["$ref"]), depth + 1)
    if "allOf" in schema:
        merged = {"type": "object", "properties": {}, "required": []}
        for sub in schema["allOf"]:
            sub_resolved = get_schema_details(sub, depth + 1)
            if "properties" in sub_resolved:
                merged["properties"].update(sub_resolved["properties"])
            if "required" in sub_resolved:
                merged["required"].extend(sub_resolved["required"])
        return merged
    return schema

def build_primitive(field, name=""):
    if "enum" in field and field["enum"]:
        return field["enum"][0]
    if "example" in field:
        return field["example"]
    if "default" in field and field["default"] is not None:
        return field["default"]

    ftype = field.get("type", "string")
    fformat = field.get("format", "")
    n = name.lower()

    if ftype == "integer":
        if "id" in n:
            return 1
        if "year" in n:
            return 2023
        if "mileage" in n:
            return 18500
        if "amount" in n or "price" in n:
            return 750000
        if "page" in n:
            return 1
        if "limit" in n or "size" in n:
            return 10
        if "rating" in n:
            return 5
        return 1
    if ftype == "number":
        if "price" in n or "amount" in n:
            return 750000.00
        if "rating" in n:
            return 4.8
        return 10.5
    if ftype == "boolean":
        if "is_primary" in n or "is_active" in n or "success" in n or "is_available" in n:
            return True
        return False
    if fformat == "date-time":
        return "2026-09-28T10:00:00Z"
    if fformat == "date":
        return "2026-09-28"
    if fformat == "email" or "email" in n:
        return "user@carzen.com"
    if "phone" in n or "contact" in n:
        return "+919876543210"
    if "token" in n:
        return "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    if "first_name" in n:
        return "John"
    if "last_name" in n:
        return "Doe"
    if "username" in n:
        return "johndoe"
    if "password" in n:
        return "SecureP@ssw0rd123"
    if "brand" in n and "name" in n:
        return "Toyota"
    if "model" in n and "name" in n:
        return "Camry"
    if "variant" in n and "name" in n:
        return "XLE Hybrid"
    if "vin" in n:
        return "1HGCR2F83HA123456"
    if "registration" in n:
        return "KA01MJ2023"
    if "city" in n:
        return "Bengaluru"
    if "state" in n:
        return "Karnataka"
    if "pincode" in n or "postal" in n:
        return "560001"
    if "address" in n:
        return "123 MG Road, Indiranagar"
    if "title" in n or "car_title" in n:
        return "2023 Toyota Camry XLE Hybrid"
    if "notes" in n or "description" in n:
        return "Single owner, complete service history, mint condition."
    if "razorpay_order_id" in n:
        return "order_K8dG9zZ1X7V3A1"
    if "razorpay_payment_id" in n:
        return "pay_K8dH1bZ2Y8W4B2"
    if "razorpay_signature" in n:
        return "9b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c"
    if "url" in n or "link" in n or "image" in n:
        return "https://example.com/uploads/cars/sample.jpg"
    if "code" in n:
        return "CZN-2026-001"
    return "string"

def build_example(schema, depth=0):
    if depth > 4:
        return {}
    if "$ref" in schema:
        return build_example(resolve_ref(schema["$ref"]), depth + 1)
    if "allOf" in schema:
        res = {}
        for sub in schema["allOf"]:
            sub_res = build_example(sub, depth + 1)
            if isinstance(sub_res, dict):
                res.update(sub_res)
        return res
    if "anyOf" in schema:
        return build_example(schema["anyOf"][0], depth + 1)
    if "oneOf" in schema:
        return build_example(schema["oneOf"][0], depth + 1)

    if "enum" in schema and schema["enum"]:
        return schema["enum"][0]

    stype = schema.get("type", "object")
    if stype == "object" or "properties" in schema:
        obj = {}
        props = schema.get("properties", {})
        for prop_name, prop_val in props.items():
            obj[prop_name] = build_field_example(prop_name, prop_val, depth + 1)
        return obj
    elif stype == "array":
        item_schema = schema.get("items", {})
        return [build_example(item_schema, depth + 1)]
    return build_primitive(schema)

def build_field_example(name, field, depth):
    if "$ref" in field:
        return build_example(resolve_ref(field["$ref"]), depth + 1)
    if "allOf" in field:
        return build_example(field["allOf"][0], depth + 1)
    if "anyOf" in field:
        return build_example(field["anyOf"][0], depth + 1)
    if "oneOf" in field:
        return build_example(field["oneOf"][0], depth + 1)
    if "enum" in field and field["enum"]:
        return field["enum"][0]

    ftype = field.get("type")
    if ftype == "array":
        items = field.get("items", {})
        return [build_field_example(name, items, depth + 1)]
    if ftype == "object" or "properties" in field:
        return build_example(field, depth + 1)
    return build_primitive(field, name)

def get_field_type_str(field):
    if "$ref" in field:
        ref_name = field["$ref"].split("/")[-1]
        target = schemas.get(ref_name, {})
        if "enum" in target:
            return f"`enum`: {', '.join([str(e) for e in target['enum']])}"
        return f"`{ref_name}`"
    if "enum" in field:
        return f"`enum`: {', '.join([str(e) for e in field['enum']])}"
    ftype = field.get("type", "string")
    if ftype == "array":
        items = field.get("items", {})
        item_str = get_field_type_str(items)
        return f"`array[{item_str.replace('`', '')}]`"
    return f"`{ftype}`"

def build_fields_table(schema_obj):
    resolved = get_schema_details(schema_obj)
    props = resolved.get("properties", {})
    if not props:
        return ""
    
    required_fields = set(resolved.get("required", []))
    lines = [
        "| Field | Type | Required | Description |",
        "| :--- | :--- | :--- | :--- |"
    ]
    for prop_name, prop_data in props.items():
        type_str = get_field_type_str(prop_data)
        is_req = "**Yes**" if prop_name in required_fields else "No"
        desc = prop_data.get("description") or prop_data.get("title") or "-"
        desc = desc.replace("\n", " ").strip()
        lines.append(f"| `{prop_name}` | {type_str} | {is_req} | {desc} |")
    return "\n".join(lines) + "\n"

def determine_auth(path, method, operation):
    tags = [t.lower() for t in operation.get("tags", [])]
    p = path.lower()

    if "/admin" in p or any("admin" in t for t in tags):
        return "Admin (`Bearer <token>` with `role=ADMIN`)"
    if p in ["/", "/v1/auth/login", "/v1/auth/register", "/v1/auth/register-admin", "/v1/payments/webhook"]:
        return "Public (No authentication required)"
    if p.startswith("/v1/listings") and method == "GET":
        return "Public (No authentication required)"
    if p.startswith("/v1/services") and method == "GET" and not p.startswith("/v1/services/history"):
        return "Public (No authentication required)"
    if p.startswith("/v1/cars/") and p.endswith("/reviews") and method == "GET":
        return "Public (No authentication required)"
    if p.startswith("/v1/car-brands") and method == "GET":
        return "Public / Authenticated"
    if p.startswith("/v1/car-models") and method == "GET":
        return "Public / Authenticated"
    if p.startswith("/v1/car-variants") and method == "GET":
        return "Public / Authenticated"
    if p.startswith("/v1/seller"):
        return "Seller (`Bearer <token>` with `role=USER`)"
    if p.startswith("/v1/buyer"):
        return "Buyer (`Bearer <token>` with `role=USER`)"
    return "Authenticated User (`Bearer <token>`)"

CATEGORY_ORDER = [
    ("System & Health", ["home"]),
    ("Authentication & Authorization", ["auth"]),
    ("User Profile & Management", ["users"]),
    ("Address Management", ["address"]),
    ("Contact Information", ["contacts"]),
    ("Vehicle Catalog (Brands, Models, Variants)", ["Car Brands", "Car Models", "Car Variants"]),
    ("Seller Car Inventory & Assets", ["cars", "Car Features", "Car Media"]),
    ("Marketplace Listings & Public Catalog", ["Listings"]),
    ("Favorites & Wishlist", ["Favorites"]),
    ("Buyer Operations", ["Buyer Dashboard", "Buyer Discovery", "Buyer Inquiries", "Buyer Orders", "Buyer Purchases"]),
    ("Seller Operations", ["Seller Dashboard", "Seller Inquiries", "Seller Orders"]),
    ("Inquiry Messaging", ["Inquiry Messages"]),
    ("Vehicle Orders & Checkout", ["Orders"]),
    ("Payments & Razorpay Integration", ["Payments"]),
    ("Financial Transactions Ledger", ["Transactions"]),
    ("Service Center & Maintenance History", ["Service Cars", "Service Catalog", "Service Requests", "Service History"]),
    ("Reviews & Ratings", ["Reviews"]),
    ("Moderation Reports", ["Reports"]),
    ("Notifications System", ["Notifications"]),
    ("Admin Operations & Management", [
        "Admin Listings", "Admin Orders", "Admin Service Catalog",
        "Admin Service Requests", "Admin Transactions", "Admin Reviews", "Admin Reports"
    ])
]

tag_to_category = {}
for cat_name, tags in CATEGORY_ORDER:
    for t in tags:
        tag_to_category[t] = cat_name

endpoints_by_cat = defaultdict(list)

for path, path_item in sorted(openapi.get("paths", {}).items()):
    for method, operation in path_item.items():
        if method.lower() not in ["get", "post", "put", "patch", "delete"]:
            continue
        op_tags = operation.get("tags", ["General"])
        primary_tag = op_tags[0] if op_tags else "General"
        if any("admin" in t.lower() for t in op_tags) and primary_tag != "users":
            cat = "Admin Operations & Management"
        else:
            cat = tag_to_category.get(primary_tag, "Other Operations")
        
        endpoints_by_cat[cat].append({
            "path": path,
            "method": method.upper(),
            "operation": operation,
            "tag": primary_tag
        })

doc = []
doc.append("# CarZen Full Project REST API Documentation\n")
doc.append("> **Version**: 1.0.0  \n> **Base URL**: `http://localhost:8000` (Local) / `https://api.carzen.example.com` (Production)  \n> **API Prefix**: `/v1`  \n> **Interactive Swagger UI**: [`http://localhost:8000/docs`](http://localhost:8000/docs)  \n> **ReDoc**: [`http://localhost:8000/redoc`](http://localhost:8000/redoc)  \n")
doc.append("\n---\n")

# Table of Contents
doc.append("## Table of Contents\n")
doc.append("1. [Overview & Architecture Standards](#overview--architecture-standards)")
doc.append("2. [Authentication & Authorization Guide](#authentication--authorization-guide)")
doc.append("3. [Car Management & User Workflow](#car-management--user-workflow)")
doc.append("4. [HTTP Status Codes & Error Formats](#http-status-codes--error-formats)")

cat_num = 5
for cat_name, _ in CATEGORY_ORDER:
    count = len(endpoints_by_cat.get(cat_name, []))
    if count > 0:
        anchor = cat_name.lower().replace(" ", "-").replace("&", "").replace("(", "").replace(")", "").replace(",", "")
        doc.append(f"{cat_num}. [{cat_name} ({count} Endpoints)](#{anchor})")
        cat_num += 1

doc.append("\n---\n")

# Overview Section
doc.append("## Overview & Architecture Standards\n")
doc.append("""
The CarZen REST API powers an end-to-end automotive platform built with FastAPI, SQLAlchemy 2.0, and MySQL. It features:
- **Vehicle Catalog**: Multi-tier hierarchy of Brands, Models, and Variants with vehicle specs.
- **Inventory Management**: Seller car registry with multi-image gallery upload, primary image selection, and customizable feature badges.
- **Marketplace Engine**: Public listings with keyword search, brand/model filters, price sorting, and admin approval workflows.
- **Negotiation & Inquiries**: Buyer-seller inquiry threads with direct messaging and real-time status transitions.
- **Checkout & Razorpay**: Multi-mode orders supporting full payment, booking deposit, cash-on-delivery confirmation, and signature verification.
- **Workshop & Service Management**: Service catalog, slot reservation, job lifecycle tracking (Pending -> Scheduled -> In-Progress -> Completed), digital odometer recording, and automatic service booklet creation.
- **Trust & Safety**: Verified reviews, buyer dispute reporting, and comprehensive admin moderation suites.

### Standard Request Headers
For JSON endpoints:
```http
Content-Type: application/json
Accept: application/json
Authorization: Bearer <your_jwt_access_token>
```
For file upload endpoints (`POST /v1/cars/{car_id}/media`):
```http
Content-Type: multipart/form-data
Authorization: Bearer <your_jwt_access_token>
```
""")

doc.append("## Authentication & Authorization Guide\n")
doc.append("""
All protected endpoints require an `Authorization` header containing a valid Bearer JWT.

### Auth Flow
1. **Register**: `POST /v1/auth/register` creates a user account.
2. **Login**: `POST /v1/auth/login` verifies credentials and returns a signed JWT token.
3. **Attach Header**: Send `Authorization: Bearer <token>` with every subsequent request.
4. **Token Validation**: Call `GET /v1/auth/validate` to verify session liveness and fetch user details.

### Roles and Permissions
| Role | Code Value | Description |
| :--- | :--- | :--- |
| **Public** | None | Unauthenticated access to public catalog, active services, health checks, and webhooks. |
| **User (Buyer & Seller)** | `user` | Standard platform account. Can register cars, create listings, submit inquiries, place orders, book workshop services, and leave reviews. |
| **Admin** | `admin` | Elevated operational role. Can verify cars, approve/reject listings, configure service catalogs, assign technicians, manage users, and resolve dispute reports. |
""")

doc.append("## Car Management & User Workflow\n")
doc.append("""
CarZen operates with **two fundamental system user roles**: `ADMIN` and `USER` (where any `USER` can seamlessly act as both **Buyer** and **Seller** within the platform).

### User Roles Architecture
- **Admin (`admin`)**: Responsible for master catalog curation (Brands, Models, Variants), reviewing and verifying car registrations, approving or rejecting vehicle submissions and listings, and overseeing platform orders.
- **User (`user`)**: Standard platform account with dual capabilities:
  - **As Seller**: Registers vehicles with VIN and specifications, uploads media and feature badges, creates listings, negotiates inquiries, and accepts orders.
  - **As Buyer**: Explores active listings with comprehensive filters, bookmarks favorites, submits inquiries to sellers, places orders, and makes payments.

### End-to-End Workflow Diagram

```mermaid
flowchart TD
    subgraph Admin_Catalog["1. Catalog Setup (Admin)"]
        A["Admin creates Brands, Models & Variants"]
    end

    subgraph Seller_Onboarding["2. Car Submission (User as Seller)"]
        B["Seller submits Car details: VIN, Reg No, Mileage, etc."]
        C["Seller uploads Images/Media & Features"]
        B --> C
        C --> D["Car status: PENDING_APPROVAL\\nis_verified: False"]
    end

    subgraph Admin_Review["3. Verification & Approval (Admin)"]
        D --> E{"Admin Review"}
        E -- Reject --> F["Car status: REJECTED\\n(Reason recorded & Seller notified)"]
        E -- Approve --> G["Car status: APPROVED\\nis_verified: True"]
    end

    subgraph Seller_Listing["4. Marketplace Listing (User as Seller)"]
        G --> H["Seller creates Listing (DRAFT)"]
        H --> I["Seller Publishes Listing"]
        I --> J["Listing: ACTIVE\\nCar status: PUBLISHED"]
    end

    subgraph Buyer_Interaction["5. Discovery & Inquiry (User as Buyer)"]
        J --> K["Buyer searches / views public listings"]
        K --> L["Buyer adds to Favorites & sends Inquiries"]
        L --> M["Buyer and Seller message / negotiate"]
    end

    subgraph Order_Sale["6. Purchase & Sold Lifecycle"]
        M --> N["Buyer places Order (Status: PENDING)"]
        N --> O["Seller Accepts Order -> Listing: RESERVED"]
        O --> P["Payment completed (PAID)"]
        P --> Q["Seller marks Order COMPLETED"]
        Q --> R["Listing: SOLD\\nCar status: SOLD"]
    end

    A -. Used by .-> B
```

### Detailed Workflow Phases

#### 1. Catalog Setup (Admin)
- **Relevant Endpoints**: `POST /v1/car-brands`, `POST /v1/car-models`, `POST /v1/car-variants`
- Master database hierarchy (Brand $\\\\to$ Model $\\\\to$ Variant) must exist before users can register cars.
- Establishes standardized vehicle taxonomy: body types, fuel types, transmission, horsepower, and engine capacity.

#### 2. Car Submission & Media Upload (User as Seller)
- **Relevant Endpoints**:
  - `POST /v1/cars` (Creates vehicle entry)
  - `POST /v1/cars/{car_id}/media` (Uploads images and videos with primary flag & sort order)
  - `POST /v1/cars/{car_id}/features` (Adds equipment and features)
- **Status Upon Creation**: `approval_status = PENDING_APPROVAL`, `is_verified = False`.
- Automated notifications are broadcast to all active platform administrators.
- Strict validation rules apply: resale vehicles (`OLD`) require registration number, VIN, registration year, and ownership type.

#### 3. Verification & Approval (Admin)
- **Relevant Endpoints**:
  - `GET /v1/admin/cars` (Admin lists pending/submitted cars)
  - `POST /v1/admin/cars/{car_id}/approve` (Verifies and approves car)
  - `POST /v1/admin/cars/{car_id}/reject` (Rejects car with recorded feedback reason)
- Approving sets `is_verified = True` and `approval_status = APPROVED`.
- Notifications alert the seller regarding approval or required corrections.
- *Security Rule*: If a seller edits sensitive attributes (VIN, registration number, manufacturing year, transmission, fuel type, or variant), the car is automatically revoked to `PENDING_APPROVAL` and unverified.

#### 4. Marketplace Listing & Publishing (User as Seller)
- **Relevant Endpoints**:
  - `POST /v1/cars/{car_id}/listing` (Creates draft listing with asking price and title)
  - `POST /v1/cars/{car_id}/listing/publish` (Publishes listing to marketplace)
  - `POST /v1/cars/{car_id}/listing/unpublish` (Reverts listing to draft)
- Only cars with `approval_status = APPROVED` can be published.
- Publishing changes `Listings.listing_status` to `ACTIVE` and `Cars.approval_status` to `PUBLISHED`.

#### 5. Discovery, Favorites & Inquiry Negotiation (User as Buyer)
- **Relevant Endpoints**:
  - `GET /v1/listings` (Public marketplace search with multi-criteria filters)
  - `GET /v1/buyer/listings/{listing_id}` (Views car detail & automatically records view analytics)
  - `POST /v1/cars/{car_id}/favorite` (Adds listing to buyer favorites)
  - `POST /v1/buyer/listings/{listing_id}/inquiries` (Buyer opens inquiry with seller)
  - `POST /v1/inquiries/{inquiry_id}/messages` (Two-way chat between buyer and seller)

#### 6. Order Placement & Sold Lifecycle (Buyer & Seller)
- **Relevant Endpoints**:
  - `POST /v1/orders` (Buyer creates purchase order; order `status = PENDING`)
  - `POST /v1/seller/orders/{order_id}/accept` (Seller confirms; listing becomes `RESERVED`)
  - `POST /v1/payments/razorpay/verify` (Buyer pays; order `payment_status = PAID`)
  - `PATCH /v1/seller/orders/{order_id}/status` (Seller moves order to `PROCESSING` $\\\\to$ `COMPLETED`)
- When an order reaches `COMPLETED`:
  - `Listings.listing_status` transitions to `SOLD`.
  - `Cars.approval_status` transitions to `SOLD`.
  - All users who saved this car in their favorites receive an automated notification that the car has been sold.

### Status Transition Matrix

| Platform Stage | Car Approval Status (`Cars.approval_status`) | Car Verified (`Cars.is_verified`) | Listing Status (`Listings.listing_status`) | Order Status (`Orders.status`) |
| :--- | :--- | :--- | :--- | :--- |
| **Car Created by Seller** | `PENDING_APPROVAL` | `False` | *(Not Created)* | *(Not Created)* |
| **Admin Rejects Car** | `REJECTED` | `False` | *(Not Created)* | *(Not Created)* |
| **Admin Approves Car** | `APPROVED` | `True` | *(Not Created)* | *(Not Created)* |
| **Seller Creates Listing** | `APPROVED` | `True` | `DRAFT` | *(Not Created)* |
| **Seller Publishes Listing** | `PUBLISHED` | `True` | `ACTIVE` | *(Not Created)* |
| **Buyer Places Order** | `PUBLISHED` | `True` | `ACTIVE` | `PENDING` |
| **Seller Accepts Order** | `PUBLISHED` | `True` | `RESERVED` | `CONFIRMED` |
| **Payment Captured** | `PUBLISHED` | `True` | `RESERVED` | `PROCESSING` |
| **Order Completed / Handed Over** | `SOLD` | `True` | `SOLD` | `COMPLETED` |
| **Order Cancelled / Rejected** | `PUBLISHED` | `True` | `ACTIVE` *(restored)* | `CANCELLED` / `REJECTED` |
""")

doc.append("## HTTP Status Codes & Error Formats\n")
doc.append("""
| HTTP Status | Name | Meaning |
| :--- | :--- | :--- |
| **`200 OK`** | Success | Standard response for successful GET, PATCH, and PUT operations. |
| **`201 Created`** | Created | Successfully created a new resource (auth, car, listing, order, review, etc.). |
| **`204 No Content`** | Deleted | Successful deletion with no response body. |
| **`400 Bad Request`** | Bad Request | Invalid business state transition (e.g. attempting to cancel an in-progress service). |
| **`401 Unauthorized`** | Unauthorized | Invalid, expired, or missing JWT Bearer token. |
| **`403 Forbidden`** | Forbidden | Insufficient permissions (e.g. standard user calling admin endpoints). |
| **`404 Not Found`** | Not Found | Entity with requested identifier does not exist. |
| **`422 Unprocessable`**| Validation Error | Payload failed Pydantic schema validation. |
| **`500 Internal Error`**| Server Error | Unexpected server runtime exception. |

#### Example Error Payload (400 / 401 / 403 / 404)
```json
{
  "detail": "Listing not found or you are not authorized to modify it."
}
```

#### Example Validation Error Payload (422)
```json
{
  "detail": [
    {
      "loc": ["body", "price"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```
""")

doc.append("\n---\n")

def generate_curl(method, path, auth_str, req_example, query_params):
    url_suffix = ""
    if query_params:
        qp_sample = "&".join([f"{p['name']}={p.get('schema', {}).get('default', 1)}" for p in query_params[:2]])
        url_suffix = f"?{qp_sample}"

    lines = [f'curl -X {method} "http://localhost:8000{path}{url_suffix}" \\']
    if "Public" not in auth_str:
        lines.append('  -H "Authorization: Bearer <YOUR_ACCESS_TOKEN>" \\')
    lines.append('  -H "Accept: application/json" \\')
    
    if req_example:
        lines.append('  -H "Content-Type: application/json" \\')
        body_json = json.dumps(req_example, indent=2)
        indented_body = "\n".join(["  " + l for l in body_json.split("\n")])
        lines.append(f"  -d '{body_json}'")
    else:
        # strip trailing slash
        lines[-1] = lines[-1].rstrip(" \\")
        
    return "\n".join(lines)

def format_endpoint(ep):
    path = ep["path"]
    method = ep["method"]
    op = ep["operation"]
    summary = op.get("summary") or f"{method} {path}"
    desc = op.get("description", "").strip()
    auth_str = determine_auth(path, method, op)

    md = []
    md.append(f"### {method} `{path}`\n")
    md.append(f"**Summary**: {summary}  \n")
    if desc:
        md.append(f"**Description**: {desc}  \n")
    md.append(f"**Authentication**: {auth_str}  \n")

    params = op.get("parameters", [])
    path_params = [p for p in params if p.get("in") == "path"]
    query_params = [p for p in params if p.get("in") == "query"]

    if path_params:
        md.append("\n#### Path Parameters\n")
        md.append("| Parameter | Type | Required | Description |")
        md.append("| :--- | :--- | :--- | :--- |")
        for p in path_params:
            ptype = p.get("schema", {}).get("type", "string")
            pdesc = p.get("description") or "-"
            md.append(f"| `{p.get('name')}` | `{ptype}` | **Yes** | {pdesc} |")

    if query_params:
        md.append("\n#### Query Parameters\n")
        md.append("| Parameter | Type | Required | Default | Description |")
        md.append("| :--- | :--- | :--- | :--- | :--- |")
        for p in query_params:
            pschema = p.get("schema", {})
            ptype = pschema.get("type", "string")
            req = "**Yes**" if p.get("required") else "No"
            default = str(pschema.get("default", "-"))
            pdesc = p.get("description") or "-"
            md.append(f"| `{p.get('name')}` | `{ptype}` | {req} | `{default}` | {pdesc} |")

    req_example = None
    if "requestBody" in op:
        content = op["requestBody"].get("content", {})
        content_type = list(content.keys())[0] if content else "application/json"
        body_schema = content.get(content_type, {}).get("schema", {})
        
        md.append(f"\n#### Request Body (`{content_type}`)\n")
        if "multipart" in content_type:
            md.append("Send as multipart form data. Key fields include uploaded binary file (`files`) and optional attributes.\n")
        else:
            table_md = build_fields_table(body_schema)
            if table_md:
                md.append(table_md)
            req_example = build_example(body_schema)
            md.append("\n**Example Payload**:\n```json\n" + json.dumps(req_example, indent=2) + "\n```\n")

    # Responses
    responses = op.get("responses", {})
    success_codes = [c for c in responses.keys() if c.startswith("2")]
    if not success_codes:
        success_codes = ["200"]
    
    sc = success_codes[0]
    resp_obj = responses.get(sc, {})
    resp_desc = resp_obj.get("description", "Successful Operation")
    md.append(f"\n#### Response (`{sc} {resp_desc}`)\n")

    resp_content = resp_obj.get("content", {})
    if resp_content and "application/json" in resp_content:
        resp_schema = resp_content["application/json"].get("schema", {})
        example_resp = build_example(resp_schema)
        md.append("```json\n" + json.dumps(example_resp, indent=2) + "\n```\n")
    elif sc == "204":
        md.append("*No content returned on successful deletion (Status 204).*\n")
    else:
        md.append("```json\n{\n  \"message\": \"Operation completed successfully\"\n}\n```\n")

    # cURL Example
    curl_snippet = generate_curl(method, path, auth_str, req_example, query_params)
    md.append("#### Example cURL Request\n```bash\n" + curl_snippet + "\n```\n")

    md.append("\n---\n")
    return "\n".join(md)

# Write all categories
for cat_name, _ in CATEGORY_ORDER:
    eps = endpoints_by_cat.get(cat_name, [])
    if not eps:
        continue
    anchor = cat_name.lower().replace(" ", "-").replace("&", "").replace("(", "").replace(")", "").replace(",", "")
    doc.append(f"## {cat_name}\n")
    doc.append(f"*Total Endpoints: {len(eps)}*\n\n")
    for ep in eps:
        doc.append(format_endpoint(ep))

output_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "docs", "API_DOCUMENTATION.md"))
os.makedirs(os.path.dirname(output_path), exist_ok=True)
with open(output_path, "w", encoding="utf-8") as f:
    f.write("\n".join(doc))

print(f"Generated Comprehensive API Documentation with {sum(len(v) for v in endpoints_by_cat.values())} endpoints at: {output_path}")
