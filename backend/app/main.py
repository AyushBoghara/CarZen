from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import os

from app.api.v1.notification import notifications   
from app.api.v1.payment import payments
from app.api.v1.report import reports
from . import models  # Import models to register them with SQLAlchemy

from app.api.v1 import home as h
from app.api.v1.auth import auth as authRouter
from app.api.v1.users import users_management
from app.api.v1.car_management import cars
from app.api.v1.car_management import catalog
from app.api.v1.car_management import marketplace
from app.api.v1.addresss import addresses
from app.api.v1.contact import contacts
from app.api.v1.seller import seller_dashboard
from app.api.v1.buyer import buyer
from app.api.v1.seller import seller
from app.api.v1.order import orders

from app.api.v1.services import (
    service_catalog,
    service_requests,
    services,
)
from app.api.v1.transactions import transactions
from app.api.v1.reviews import reviews
from app.api.v1.admin import admin_management

from contextlib import asynccontextmanager
from app.database.connection.conn import Base, engine

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Automatically create tables if they do not exist
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(title="CarZen", lifespan=lifespan)

Path("uploads").mkdir(exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "").split(",")
    if origin.strip()
]

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=[
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE",
        "OPTIONS",
    ],
    allow_headers=[
        "Authorization",
        "Content-Type",
    ],
)

app.include_router(h.router, tags=["home"])
# Register and login auth routes
app.include_router(authRouter.router, prefix="/v1/auth", tags=["auth"])

app.include_router(users_management.router, prefix="/v1", tags=["users"])
app.include_router(cars.router, prefix="/v1", tags=["cars"])
app.include_router(catalog.router, prefix="/v1")
app.include_router(marketplace.router, prefix="/v1")
app.include_router(seller_dashboard.router, prefix="/v1")
app.include_router(buyer.router, prefix="/v1")
app.include_router(seller.router, prefix="/v1")
app.include_router(orders.router, prefix="/v1")
app.include_router(notifications.router, prefix="/v1")
app.include_router(payments.router, prefix="/v1")
app.include_router(reports.router, prefix="/v1")

# Address router 
app.include_router(addresses.router, prefix="/v1", tags=["address"])

# Contacts router
app.include_router(contacts.router, prefix="/v1", tags=["contacts"])

# Vehicle Maintenance History and Service Centers (registered before catalog to avoid /services/{service_id} shadowing /services/history)
app.include_router(services.router, prefix="/v1")

# Admin-Provided Service Catalog & Service Requests
app.include_router(service_catalog.router, prefix="/v1")
app.include_router(service_requests.router, prefix="/v1")

# Transactions
app.include_router(transactions.router, prefix="/v1")

# Reviews
app.include_router(reviews.router, prefix="/v1")

# Admin Management (Listings)
app.include_router(admin_management.router, prefix="/v1")
