from enum import Enum


class BodyType(str, Enum):
    HATCHBACK = "hatchback"
    SEDAN = "sedan"
    SUV = "suv"
    MUV = "muv"
    COUPE = "coupe"
    CONVERTIBLE = "convertible"
    PICKUP = "pickup"
    MINIVAN = "minivan"
    OTHER = "other"


class FuelType(str, Enum):
    PETROL = "petrol"
    DIESEL = "diesel"
    CNG = "cng"
    ELECTRIC = "electric"
    HYBRID = "hybrid"


class TransmissionType(str, Enum):
    MANUAL = "manual"
    AUTOMATIC = "automatic"
    AMT = "amt"
    CVT = "cvt"
    DCT = "dct"


class OwnershipType(str, Enum):
    FIRST_OWNER = "first_owner"
    SECOND_OWNER = "second_owner"
    THIRD_OWNER = "third_owner"
    FOURTH_OR_MORE = "fourth_or_more"


class CarCondition(str, Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"


class MediaType(str, Enum):
    IMAGE = "image"
    VIDEO = "video"
    DOCUMENT = "document"