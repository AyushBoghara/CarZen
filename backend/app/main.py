from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.api.v1.notification import notifications
from app.api.v1.payment import payments
from app.api.v1.report import reports
from . import models # Import modles to register them with SQLAlchemy
from app.database.connection.conn import Base,engine

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

#create tables 
Base.metadata.create_all(bind=engine)

app = FastAPI(title="CarZen")

Path("uploads").mkdir(exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(h.router,tags=["home"])
# Register and login auth routes
app.include_router(authRouter.router,prefix="/v1/auth",tags=["auth"])

app.include_router(users_management.router,prefix="/v1",tags=["users"])
app.include_router(cars.router,prefix="/v1",tags=["cars"])
app.include_router(catalog.router,prefix="/v1")
app.include_router(marketplace.router,prefix="/v1")
app.include_router(seller_dashboard.router,prefix="/v1")
app.include_router(buyer.router,prefix="/v1")
app.include_router(seller.router,prefix="/v1")
app.include_router(orders.router,prefix="/v1")
app.include_router(notifications.router,prefix="/v1")
app.include_router(payments.router,prefix="/v1")
app.include_router(reports.router,prefix="/v1")

# address router 
app.include_router(addresses.router,prefix="/v1",tags=["address"])

# contacts router
app.include_router(contacts.router,prefix="/v1",tags=["contacts"])
