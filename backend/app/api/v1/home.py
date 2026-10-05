from fastapi import APIRouter
router = APIRouter()

@router.get("/")
def home():
    return {"message":"API is working successfully! For My CarZen"}
