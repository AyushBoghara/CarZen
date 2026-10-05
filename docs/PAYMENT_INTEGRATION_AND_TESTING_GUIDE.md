# CarZen - Payment & Transaction Workflow Guide

This document is a complete, step-by-step implementation and manual testing manual for CarZen's payment systems:
1. **Online Razorpay Flow** (Card, UPI, Netbanking)
2. **Offline Mode Flow** (Cash on Handover / Delivery)
3. **Financial Ledger & State Verification** (Transactions table, Order state, Car & Listing state)

---

## 1. System Architecture & Lifecycle

### Entity Relationships

```
[Listings] ─── (Active)
    │
    ▼ Buyer places order
 [Orders]  ─── (Status: PENDING)
    │
    ▼ Seller accepts order
 [Orders]  ─── (Status: CONFIRMED) ──> [Listings] changes to RESERVED
    │
    ├─── Mode A: Online (Razorpay)
    │      │
    │      ├──> POST /v1/payments (status: PENDING, razorpay_order_id created)
    │      └──> POST /v1/payments/{id}/verify (HMAC SHA-256 verified)
    │
    └─── Mode B: Offline (Cash)
           │
           ├──> POST /v1/payments (method: cash, status: PENDING)
           └──> POST /v1/payments/{id}/confirm-cash (Seller or Admin confirms)
    │
    ▼ When Payment reaches SUCCESS:
 ┌───────────────────────────────────────────────────────────┐
 │ 1. Payments.status = SUCCESS                              │
 │ 2. Orders.payment_status = PAID                           │
 │ 3. Transactions row created (COMPLETED ledger entry)      │
 │ 4. Listings.listing_status = SOLD                         │
 │ 5. Cars.approval_status = SOLD                            │
 └───────────────────────────────────────────────────────────┘
```

---

## 2. Prerequisites & Environment Setup

### 2.1 Backend Environment Configuration
Check `backend/.env` and ensure the following keys are present:

```env
# Razorpay Credentials (from Razorpay Dashboard -> Settings -> API Keys)
RAZORPAY_KEY_ID=rzp_test_TdsPijG9uRETAs
RAZORPAY_KEY_SECRET=m612UabU1BXaEmchewU3jJhV
RAZORPAY_WEBHOOK_SECRET=https://zynvert.in/
RAZORPAY_MAX_ORDER_AMOUNT_PAISE=500000000
```

> **Note**: `RAZORPAY_KEY_ID` (starts with `rzp_test_`) is public. `RAZORPAY_KEY_SECRET` is the private key used to verify cryptographic HMAC signatures.

### 2.2 Postman Auth Tokens
You need two JWT bearer tokens:
- **`BUYER_TOKEN`**: User who purchases the vehicle (`role: user`).
- **`SELLER_TOKEN`**: User who owns the vehicle listing (`role: user` or `admin`).

Obtain tokens via `POST http://localhost:8000/v1/auth/login`:
```json
{
  "email": "buyer@example.com",
  "password": "yourpassword"
}
```

---

## 3. Flow 1: Online Razorpay Flow (Manual Postman Guide)

### Step 1: Buyer Creates an Order
- **Method**: `POST`
- **URL**: `http://localhost:8000/v1/orders`
- **Headers**:
  - `Authorization: Bearer <BUYER_TOKEN>`
  - `Content-Type: application/json`
- **Body**:
  ```json
  {
    "listing_id": 1,
    "notes": "Buying via Razorpay test"
  }
  ```
- **Response (`201 Created`)**:
  ```json
  {
    "id": 10,
    "listing_id": 1,
    "amount": "250000.00",
    "status": "pending",
    "payment_status": "pending"
  }
  ```
- **Save**: `order_id = 10`.

---

### Step 2: Seller Accepts the Order
CarZen requires the seller to accept the order before payment can be collected. Accepting automatically marks the car listing as `RESERVED`.

- **Method**: `PATCH`
- **URL**: `http://localhost:8000/v1/seller/orders/10/accept`
- **Headers**:
  - `Authorization: Bearer <SELLER_TOKEN>`
- **Response (`200 OK`)**:
  ```json
  {
    "id": 10,
    "status": "confirmed",
    "payment_status": "pending"
  }
  ```

---

### Step 3: Buyer Initiates Online Payment
The buyer selects online card/UPI payment. The server creates an order on Razorpay servers and stores a `pending` payment record.

- **Method**: `POST`
- **URL**: `http://localhost:8000/v1/payments`
- **Headers**:
  - `Authorization: Bearer <BUYER_TOKEN>`
  - `Content-Type: application/json`
- **Body**:
  ```json
  {
    "order_id": 10,
    "payment_method": "card"
  }
  ```
- **Response (`201 Created`)**:
  ```json
  {
    "id": 15,
    "order_id": 10,
    "amount": "250000.00",
    "currency": "INR",
    "payment_method": "card",
    "provider": "razorpay",
    "razorpay_order_id": "order_AbCdEf12345678",
    "razorpay_key_id": "rzp_test_TdsPijG9uRETAs",
    "status": "pending"
  }
  ```
- **Save from response**:
  - `payment_id` = `15`
  - `razorpay_order_id` = `"order_AbCdEf12345678"`

---

### Step 4: Verify Payment & Cryptographic Signature

In production, the frontend Razorpay modal returns `razorpay_payment_id` and `razorpay_signature`. To test this in Postman, you can generate the signature using either **Method A** or **Method B**.

#### Method A: Postman Script (Automatic)
In Postman, create a new request for `POST http://localhost:8000/v1/payments/15/verify`.
Under the **Pre-request Script** tab, paste:

```javascript
// 1. Paste your RAZORPAY_KEY_SECRET from backend/.env
const secret = "m612UabU1BXaEmchewU3jJhV";

// 2. Paste the razorpay_order_id from Step 3
const orderId = "order_AbCdEf12345678";

// 3. Generate a random unique test payment ID
const paymentId = "pay_test_" + Date.now();

// 4. Calculate HMAC-SHA256
const payload = orderId + "|" + paymentId;
const signature = CryptoJS.HmacSHA256(payload, secret).toString(CryptoJS.enc.Hex);

// 5. Store globally for the body
pm.globals.set("rzp_order_id", orderId);
pm.globals.set("rzp_payment_id", paymentId);
pm.globals.set("rzp_signature", signature);
```

Then in the **Body (`raw json`)** tab:
```json
{
  "razorpay_order_id": "{{rzp_order_id}}",
  "razorpay_payment_id": "{{rzp_payment_id}}",
  "razorpay_signature": "{{rzp_signature}}"
}
```

#### Method B: Terminal / Python One-Liner (Direct)
If you want to paste the exact signature manually without Postman variables, run this in your terminal:

```bash
python -c "import hmac, hashlib; secret='m612UabU1BXaEmchewU3jJhV'; oid='order_AbCdEf12345678'; pid='pay_test_001'; print(hmac.new(secret.encode(), f'{oid}|{pid}'.encode(), hashlib.sha256).hexdigest())"
```
It prints the signature (e.g. `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`).

Paste directly into Postman **Body**:
```json
{
  "razorpay_order_id": "order_AbCdEf12345678",
  "razorpay_payment_id": "pay_test_001",
  "razorpay_signature": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
}
```

#### Send Verification:
- **Method**: `POST`
- **URL**: `http://localhost:8000/v1/payments/15/verify`
- **Headers**:
  - `Authorization: Bearer <BUYER_TOKEN>`
  - `Content-Type: application/json`

- **Response (`200 OK`)**:
  ```json
  {
    "id": 15,
    "order_id": 10,
    "amount": "250000.00",
    "currency": "INR",
    "payment_method": "card",
    "provider": "razorpay",
    "razorpay_order_id": "order_AbCdEf12345678",
    "razorpay_payment_id": "pay_test_001",
    "status": "success"
  }
  ```

---

## 4. Flow 2: Offline Mode (Cash on Delivery / Handover)

The offline flow requires **no external Razorpay API credentials** and is handled entirely inside CarZen.

### Step 1: Create and Accept Order
Follow Step 1 and Step 2 from Flow 1 so that the order is `CONFIRMED` and the listing is `RESERVED`.
*(Example: `order_id = 11`)*.

---

### Step 2: Buyer Selects Cash Payment
The buyer selects `cash` as their payment method.

- **Method**: `POST`
- **URL**: `http://localhost:8000/v1/payments`
- **Headers**:
  - `Authorization: Bearer <BUYER_TOKEN>`
  - `Content-Type: application/json`
- **Body**:
  ```json
  {
    "order_id": 11,
    "payment_method": "cash"
  }
  ```
- **Response (`201 Created`)**:
  ```json
  {
    "id": 16,
    "order_id": 11,
    "amount": "250000.00",
    "currency": "INR",
    "payment_method": "cash",
    "provider": "cash",
    "razorpay_order_id": null,
    "razorpay_payment_id": null,
    "status": "pending"
  }
  ```
- **Note**: Notifications are immediately sent to both the buyer and seller confirming cash selection.

---

### Step 3: Seller or Admin Confirms Cash Receipt
When the buyer and seller meet and exchange cash at car handover, the seller (or an admin) confirms receipt in the app.

- **Method**: `POST`
- **URL**: `http://localhost:8000/v1/payments/16/confirm-cash`
- **Headers**:
  - `Authorization: Bearer <SELLER_TOKEN>` (or Admin token)
  - `Content-Type: application/json`
- **Body**:
  ```json
  {
    "notes": "Full cash received at vehicle handover inspection."
  }
  ```
- **Response (`200 OK`)**:
  ```json
  {
    "id": 16,
    "order_id": 11,
    "amount": "250000.00",
    "currency": "INR",
    "payment_method": "cash",
    "provider": "cash",
    "razorpay_order_id": null,
    "razorpay_payment_id": "cash_order_11_pay_16_1727715000",
    "status": "success"
  }
  ```

---

## 5. Verifying Results (Ledger & States)

Regardless of whether Online or Cash was used, verify that the system executed the atomic database transitions:

### 5.1 Check Buyer Financial Ledger
- **Method**: `GET`
- **URL**: `http://localhost:8000/v1/transactions/buy`
- **Headers**: `Authorization: Bearer <BUYER_TOKEN>`
- **Expected Data**:
  ```json
  {
    "data": [
      {
        "id": 5,
        "order_id": 10,
        "listing_id": 1,
        "car_id": 2,
        "buyer_id": 1,
        "seller_id": 3,
        "final_price": 250000.0,
        "payment_method": "card",
        "payment_status": "paid",
        "transaction_status": "completed"
      }
    ],
    "pagination": { "page": 1, "limit": 20, "total": 1, "pages": 1 }
  }
  ```

### 5.2 Check Order Status
- **Method**: `GET`
- **URL**: `http://localhost:8000/v1/orders/10`
- **Headers**: `Authorization: Bearer <BUYER_TOKEN>`
- **Expected**:
  - `payment_status`: `"paid"`

### 5.3 Check Listing & Car Status
- **Method**: `GET`
- **URL**: `http://localhost:8000/v1/cars/listings/1`
- **Expected**:
  - `listing_status`: `"sold"`
  - `car.approval_status`: `"sold"`

---

## 6. Common Errors & Troubleshooting

| Error Message | Cause | Solution |
| :--- | :--- | :--- |
| `Razorpay order does not match this payment.` | The `razorpay_order_id` in request body belongs to a different payment row or Postman variable is resolving to an old value. | Check `GET /v1/payments/{id}` to see the exact `razorpay_order_id` assigned to that payment ID. |
| `Invalid Razorpay payment signature.` | Using `RAZORPAY_KEY_ID` instead of `RAZORPAY_KEY_SECRET` in HMAC generation, or trailing whitespace in `payment_id`. | Ensure the secret matches `RAZORPAY_KEY_SECRET` from `.env`. |
| `Only confirmed or processing orders can be paid.` | Attempting to create payment while order is still `pending`. | Call `PATCH /v1/seller/orders/{order_id}/accept` first as the seller. |
| `Only a reserved listing can be paid for.` | Listing is not marked `reserved`. | When seller accepts the order, listing automatically becomes `reserved`. Ensure no conflicting order exists. |
| `Only the seller of this order or an admin can confirm cash receipt.` | A buyer or unrelated user tried to confirm cash. | Use the `SELLER_TOKEN` of the car owner, or an `ADMIN_TOKEN`. |
| `This Razorpay payment has already been processed.` | Re-using the same `razorpay_payment_id` for two different verify attempts. | Generate a new test payment ID (e.g. `pay_test_` + timestamp). |
